"""
Punto de entrada del servidor MCP.
Conecta: configuración -> repositorios concretos -> tools -> MCPServer.
"""

from mcp.server.mcpserver import MCPServer, Context

from mcp_db_agent.config.settings import settings
from mcp_db_agent.infrastructure.catalog_repository_sqlserver import CatalogRepositorySqlServer
from mcp_db_agent.infrastructure.indicator_executor_sqlserver import IndicatorExecutorSqlServer
from mcp_db_agent.tools.indicator_tools import ejecutar_indicador, listar_indicadores

# Instancias únicas de los repositorios, construidas UNA vez al arrancar
catalog_repo = CatalogRepositorySqlServer(settings.agent_db)
executor_repo = IndicatorExecutorSqlServer(settings.his_db)

mcp = MCPServer(
    "mcp-db-agent",
    instructions=(
        "Agente para consultar indicadores del negocio. "
        "Usa 'list_available_indicators' primero para ver qué indicadores existen "
        "y qué parámetros necesitan, luego 'run_indicator' para ejecutarlos."
    ),
    version="0.1.0",
)


@mcp.tool()
async def list_available_indicators(ctx: Context) -> list[dict]:
    """Lista todos los indicadores disponibles, con su descripción y parámetros."""
    return listar_indicadores(catalog_repo)


@mcp.tool()
async def run_indicator(
    ctx: Context,
    nombre_sp: str,
    parametros: dict,
) -> dict:
    """
    Ejecuta un indicador del catálogo autorizado.

    nombre_sp: nombre exacto del procedimiento, tal como aparece en list_available_indicators.
    parametros: diccionario con los parámetros requeridos/opcionales de ese indicador.
    """
    try:
        return ejecutar_indicador(catalog_repo, executor_repo, nombre_sp, parametros)
    except ValueError as e:
        return {"exitoso": False, "error": str(e)}


if __name__ == "__main__":
    mcp.run(transport="stdio")