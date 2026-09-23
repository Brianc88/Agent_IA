"""
Implementación de ValueCatalogRepository: lee la configuración de
FuentesValoresValidos (en AGENT_DB) y ejecuta la consulta real contra
la base que corresponda, con cache en memoria por TTL.
"""

import time

from mcp_db_agent.config.settings import DatabaseSettings
from mcp_db_agent.infrastructure.db_connection import crear_conexion


class ValueCatalogRepositorySqlServer:
    def __init__(self, agent_db_settings: DatabaseSettings, his_db_settings: DatabaseSettings):
        self._agent_db_settings = agent_db_settings
        self._his_db_settings = his_db_settings
        # cache simple en memoria: nombre_parametro -> (timestamp_guardado, valores, ttl_segundos)
        self._cache: dict[str, tuple[float, list[str], int]] = {}

    def _obtener_configuracion(self, nombre_parametro: str):
        """Lee de AGENT_DB la fuente configurada para este parámetro, si existe."""
        with crear_conexion(self._agent_db_settings) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT fv.conexion_destino, fv.consulta_sql, fv.umbral_fuzzy, fv.cache_ttl_segundos
                FROM agent_ia.FuentesValoresValidos fv
                JOIN agent_ia.Parametros p ON p.id = fv.parametro_id
                WHERE p.nombre_parametro = ? AND fv.activo = 1
                """,
                nombre_parametro,
            )
            return cursor.fetchone()

    def obtener_umbral(self, nombre_parametro: str) -> int | None:
        """Devuelve el umbral configurado para este parámetro, o None si no aplica."""
        config = self._obtener_configuracion(nombre_parametro)
        return config.umbral_fuzzy if config else None

    def obtener_valores_validos(self, nombre_parametro: str) -> list[str] | None:
        # 1. Revisar cache primero
        if nombre_parametro in self._cache:
            guardado_en, valores, ttl = self._cache[nombre_parametro]
            if time.time() - guardado_en < ttl:
                return valores

        # 2. Leer configuración desde AGENT_DB
        config = self._obtener_configuracion(nombre_parametro)
        if config is None:
            return None  # este parámetro no tiene fuzzy matching configurado

        # 3. Ejecutar la consulta real contra la BD que corresponda
        db_settings = (
            self._his_db_settings if config.conexion_destino == "HIS_DB" else self._agent_db_settings
        )
        with crear_conexion(db_settings) as conn:
            cursor = conn.cursor()
            cursor.execute(config.consulta_sql)
            valores = [str(fila[0]) for fila in cursor.fetchall() if fila[0] is not None]

        # 4. Guardar en cache y devolver
        self._cache[nombre_parametro] = (time.time(), valores, config.cache_ttl_segundos)
        return valores