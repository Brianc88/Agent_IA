
"""
Interfaces (contratos) de repositorios — el dominio define QUÉ necesita,
sin saber CÓMO se implementa (SQL Server, otra BD, un mock de pruebas, etc.)
"""

from typing import Protocol

from mcp_db_agent.domain.models import Indicador


class CatalogRepository(Protocol):
    """Contrato para leer el catálogo de indicadores y registrar auditoría."""

    def obtener_indicador_por_nombre(self, nombre_sp: str) -> Indicador | None:
        """Busca un indicador por su nombre de SP. None si no existe."""
        ...

    def listar_indicadores_aprobados(self) -> list[Indicador]:
        """Devuelve todos los indicadores en estado 'aprobado' y activos."""
        ...

    def registrar_ejecucion(
        self,
        indicador_id: int,
        parametros_enviados: dict,
        exitoso: bool,
        filas_retornadas: int | None,
        duracion_ms: int,
        mensaje_error: str | None = None,
    ) -> None:
        """Guarda un registro de auditoría de una ejecución (éxito o fallo)."""
        ...


class IndicatorExecutorRepository(Protocol):
    """Contrato para ejecutar el SP real contra el HIS."""

    def ejecutar(
        self,
        nombre_sp: str,
        parametros: dict,
        timeout_segundos: int,
        max_filas_retorno: int,
    ) -> list[dict]:
        """Ejecuta el SP dado y devuelve las filas como lista de diccionarios."""
        ...