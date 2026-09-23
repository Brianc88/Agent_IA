from mcp_db_agent.config.settings import settings
from mcp_db_agent.infrastructure.value_catalog_repository_sqlserver import ValueCatalogRepositorySqlServer
from mcp_db_agent.domain.value_matching import resolver_valor

repo = ValueCatalogRepositorySqlServer(settings.agent_db, settings.his_db)

valores_reales = repo.obtener_valores_validos("centro_costo")
print("Valores reales de centro_costo:", valores_reales)

umbral = repo.obtener_umbral("centro_costo")
resultado = resolver_valor("diagnostico", valores_reales, umbral)
print("Resultado para 'diagnostico':", resultado) 