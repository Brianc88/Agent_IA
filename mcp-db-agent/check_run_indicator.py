"""
Diagnóstico directo: llama a la lógica de run_indicator SIN pasar por MCP/Inspector,
para ver el traceback completo del error real.
"""

import traceback

from mcp_db_agent.config.settings import settings
from mcp_db_agent.infrastructure.catalog_repository_sqlserver import CatalogRepositorySqlServer
from mcp_db_agent.infrastructure.indicator_executor_sqlserver import IndicatorExecutorSqlServer
from mcp_db_agent.tools.indicator_tools import ejecutar_indicador

catalog_repo = CatalogRepositorySqlServer(settings.agent_db)
executor_repo = IndicatorExecutorSqlServer(settings.his_db)

try:
    resultado = ejecutar_indicador(
        catalog_repo,
        executor_repo,
        nombre_sp="agent.sp_FacturacionPorDimension",
        parametros={
            "fecha_inicial": "2023-01-01",
            "fecha_final": "2026-09-15",
            "dimension": "convenio",
        },
    )
    print("✅ ÉXITO")
    print(resultado)
except Exception:
    print("❌ ERROR COMPLETO:")
    traceback.print_exc()