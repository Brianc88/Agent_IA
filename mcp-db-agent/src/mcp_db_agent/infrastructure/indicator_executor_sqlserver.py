"""
Implementación de IndicatorExecutorRepository usando SQL Server (HIS_DB).
"""

from mcp_db_agent.config.settings import DatabaseSettings
from mcp_db_agent.infrastructure.db_connection import crear_conexion


class IndicatorExecutorSqlServer:
    def __init__(self, db_settings: DatabaseSettings):
        self._db_settings = db_settings

    def ejecutar(
        self,
        nombre_sp: str,
        parametros: dict,
        timeout_segundos: int,
        max_filas_retorno: int,
    ) -> list[dict]:
        # nombre_sp viene siempre del catálogo (ya validado), nunca directo del LLM.
        placeholders = ", ".join(f"@{clave} = ?" for clave in parametros.keys())
        query = f"EXEC {nombre_sp} {placeholders}" if placeholders else f"EXEC {nombre_sp}"

        with crear_conexion(self._db_settings) as conn:
            conn.timeout = timeout_segundos
            cursor = conn.cursor()
            cursor.execute(query, list(parametros.values()))

            columnas = [col[0] for col in cursor.description]
            filas = cursor.fetchmany(max_filas_retorno)
            return [dict(zip(columnas, fila)) for fila in filas]