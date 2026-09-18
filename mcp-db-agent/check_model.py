
from src.mcp_db_agent.domain.models import Indicador, NivelRiesgo, EstadoIndicador, ParametroIndicador

# Caso válido: tu indicador real sp_FacturacionSummary
indicador = Indicador(
    id=3,
    nombre_sp="sp_FacturacionSummary",
    descripcion="Calcula el valor neto TOTAL facturado...",
    nivel_riesgo=NivelRiesgo.SOLO_LECTURA,
    estado=EstadoIndicador.APROBADO,
    timeout_segundos=10,
    max_filas_retorno=1,
    parametros=[
        ParametroIndicador(nombre="fecha_inicial", tipo_dato="date", requerido=True, orden=1, ejemplo="2026-09-10"),
    ],
)
print("✅ Indicador válido creado:", indicador.nombre_sp)
print("¿Es ejecutable?", indicador.es_ejecutable())

# Caso inválido: a propósito, un nivel_riesgo que no existe
try:
    Indicador(
        id=99,
        nombre_sp="sp_Falso",
        descripcion="test",
        nivel_riesgo="algo_invalido",   # ❌ esto no está en el Enum
        estado=EstadoIndicador.APROBADO,
        timeout_segundos=10,
        max_filas_retorno=1,
    )
except Exception as e:
    print("\n❌ Pydantic rechazó el dato inválido, como se esperaba:")
    print(e)