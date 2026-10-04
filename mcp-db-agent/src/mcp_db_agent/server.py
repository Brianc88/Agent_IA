"""
Punto de entrada del servidor MCP.
Conecta: configuración -> repositorios concretos -> tools -> MCPServer.
"""

import os

from mcp.server.mcpserver import MCPServer, Context
from mcp.server.transport_security import TransportSecuritySettings
from mcp_db_agent.config.settings import settings
from mcp_db_agent.infrastructure.auth_middleware import BearerAuthMiddleware
from mcp_db_agent.infrastructure.catalog_repository_sqlserver import CatalogRepositorySqlServer
from mcp_db_agent.infrastructure.indicator_executor_sqlserver import IndicatorExecutorSqlServer
from mcp_db_agent.infrastructure.value_catalog_repository_sqlserver import ValueCatalogRepositorySqlServer
from mcp_db_agent.tools.indicator_tools import ejecutar_indicador, listar_indicadores
from mcp_db_agent.domain.value_matching import AmbiguedadValorError

catalog_repo = CatalogRepositorySqlServer(settings.agent_db)
executor_repo = IndicatorExecutorSqlServer(settings.his_db)
value_repo = ValueCatalogRepositorySqlServer(settings.agent_db, settings.his_db)

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
        return ejecutar_indicador(
            catalog_repo,
            executor_repo,
            value_repo,
            nombre_sp,
            parametros,
        )

    except AmbiguedadValorError as e:
        return {
            "exitoso": False,
            "tipo_error": "parametro_ambiguo",
            "valor_recibido": e.valor_recibido,
            "alternativas": e.alternativas,
        }
    except ValueError as e:
        return {
            "exitoso": False,
            "tipo_error": "validacion",
            "error": str(e),
        }

    except Exception as e:
        return {
            "exitoso": False,
            "tipo_error": "ejecucion",
            "error": str(e),
        }

def crear_app():
    token = os.environ["MCP_BEARER_TOKEN"]
    app = mcp.streamable_http_app(
        host="0.0.0.0",
        transport_security=TransportSecuritySettings(
            allowed_hosts=["192.168.1.16:8000", "localhost:8000", "127.0.0.1:8000"],
            allowed_origins=["*"],
        ),
    )
    return BearerAuthMiddleware(app, token)

if __name__ == "__main__":
    mcp.run(transport="stdio")