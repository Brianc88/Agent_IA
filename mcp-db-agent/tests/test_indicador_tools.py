from mcp_db_agent.config.settings import settings
from mcp_db_agent.infrastructure.catalog_repository_sqlserver import CatalogRepositorySqlServer
from mcp_db_agent.infrastructure.indicator_executor_sqlserver import IndicatorExecutorSqlServer
from mcp_db_agent.infrastructure.value_catalog_repository_sqlserver import ValueCatalogRepositorySqlServer
from mcp_db_agent.tools.indicator_tools import ejecutar_indicador


catalog_repo = CatalogRepositorySqlServer(settings.agent_db)
executor_repo = IndicatorExecutorSqlServer(settings.his_db)
value_repo = ValueCatalogRepositorySqlServer(
    settings.agent_db,
    settings.his_db,
)


resultado = ejecutar_indicador(
    catalog_repo=catalog_repo,
    executor_repo=executor_repo,
    value_repo=value_repo,
    nombre_sp="agent.sp_FacturacionSummary",
    parametros={
        "fecha_inicial": "2024-05-01",
        "fecha_final": "2024-05-31",
        "contrato": "Nueva EPS",
    },
)

print(resultado)