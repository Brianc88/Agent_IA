import asyncio;
from mcp_db_agent.server import run_indicator

resultado = asyncio.run(
    run_indicator(None, 'agent.sp_FacturacionSummary', 
                  {'fecha_inicial': '2024-05-01', 
                   'fecha_final': '2024-05-31', 
                   'contrato': 'Nueva Eps'}
                  )
    ) 
print(resultado)
