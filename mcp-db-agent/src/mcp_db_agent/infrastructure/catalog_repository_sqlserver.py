"""
Implementación de CatalogRepository usando SQL Server (AGENT_DB).
"""

import json

from mcp_db_agent.config.settings import DatabaseSettings
from mcp_db_agent.domain.models import (
    EstadoIndicador,
    Indicador,
    NivelRiesgo,
    ParametroIndicador,
)
from mcp_db_agent.infrastructure.db_connection import crear_conexion


class CatalogRepositorySqlServer:
    def __init__(self, db_settings: DatabaseSettings):
        self._db_settings = db_settings

    def _fila_a_indicador(self, fila, parametros: list[ParametroIndicador]) -> Indicador:
        ejemplos = json.loads(fila.ejemplos_preguntas) if fila.ejemplos_preguntas else []
        return Indicador(
            id=fila.id,
            nombre_sp=fila.nombre_sp,
            descripcion=fila.descripcion,
            nivel_riesgo=NivelRiesgo(fila.nivel_riesgo),
            estado=EstadoIndicador(fila.estado),
            timeout_segundos=fila.timeout_segundos,
            max_filas_retorno=fila.max_filas_retorno,
            ejemplos_preguntas=ejemplos,
            parametros=parametros,
        )

    def _obtener_parametros(self, cursor, indicador_id: int) -> list[ParametroIndicador]:
        cursor.execute(
            """
            SELECT p.nombre_parametro, p.tipo_dato, ip.requerido, ip.orden, ip.ejemplo
            FROM agent_ia.IndicadorParametros ip
            JOIN agent_ia.Parametros p ON p.id = ip.parametro_id
            WHERE ip.indicador_id = ?
            ORDER BY ip.orden
            """,
            indicador_id,
        )
        return [
            ParametroIndicador(
                nombre=row.nombre_parametro,
                tipo_dato=row.tipo_dato,
                requerido=bool(row.requerido),
                orden=row.orden,
                ejemplo=row.ejemplo,
            )
            for row in cursor.fetchall()
        ]

    def obtener_indicador_por_nombre(self, nombre_sp: str) -> Indicador | None:
        with crear_conexion(self._db_settings) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, nombre_sp, descripcion, ejemplos_preguntas,
                       nivel_riesgo, estado, timeout_segundos, max_filas_retorno
                FROM agent_ia.CatalogoIndicadores
                WHERE nombre_sp = ? AND activo = 1
                """,
                nombre_sp,
            )
            fila = cursor.fetchone()
            if fila is None:
                return None

            parametros = self._obtener_parametros(cursor, fila.id)
            return self._fila_a_indicador(fila, parametros)

    def listar_indicadores_aprobados(self) -> list[Indicador]:
        with crear_conexion(self._db_settings) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                Exec agent_ia.sp_mcp_listar_sp 
                """ 
            )
            filas = cursor.fetchall()
            indicadores = []
            for fila in filas:
                parametros = self._obtener_parametros(cursor, fila.id)
                indicadores.append(self._fila_a_indicador(fila, parametros))
            return indicadores

    def registrar_ejecucion(
        self,
        indicador_id: int,
        parametros_enviados: dict,
        exitoso: bool,
        filas_retornadas: int | None,
        duracion_ms: int,
        mensaje_error: str | None = None,
    ) -> None:
        with crear_conexion(self._db_settings) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO agent_ia.LogEjecucionesIndicador
                    (indicador_id, tenant_id, parametros_enviados, exitoso,
                     mensaje_error, filas_retornadas, duracion_ms)
                VALUES (?, 1, ?, ?, ?, ?, ?)
                """,
                indicador_id,
                json.dumps(parametros_enviados),
                exitoso,
                mensaje_error,
                filas_retornadas,
                duracion_ms,
            )
            conn.commit()