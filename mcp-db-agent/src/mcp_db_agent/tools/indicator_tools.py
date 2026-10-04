"""
Tools MCP: la capa que el LLM ve y usa directamente.
Aquí vive la lógica de: buscar en catálogo, validar, ejecutar, auditar.
"""

import time

from mcp_db_agent.domain.models import Indicador
from mcp_db_agent.domain.repositories import (
    CatalogRepository,
    IndicatorExecutorRepository,
    ValueCatalogRepository,
)
from mcp_db_agent.domain.value_matching import (
    resolver_lista_o_valor,
)

def _normalizar_parametros(parametros: dict) -> dict:
    """
    Normaliza los valores recibidos desde el LLM antes de cualquier validación.

    - Strings -> MAYÚSCULAS y sin espacios extremos.
    - Listas -> aplica la misma normalización a cada elemento.
    - Otros tipos -> se conservan sin cambios.
    """

    normalizados = {}

    for nombre, valor in parametros.items():

        if isinstance(valor, str):
            normalizados[nombre] = valor.strip().upper()

        elif isinstance(valor, list):
            normalizados[nombre] = [
                item.strip().upper() if isinstance(item, str) else item
                for item in valor
            ]

        else:
            normalizados[nombre] = valor

    return normalizados

def _validar_parametros(
    indicador: Indicador,
    parametros_recibidos: dict,
) -> None:
    """Valida que los parámetros requeridos estén presentes. Lanza ValueError si no."""

    nombres_esperados = {p.nombre for p in indicador.parametros}

    faltantes = [
        p.nombre
        for p in indicador.parametros
        if p.requerido and p.nombre not in parametros_recibidos
    ]

    if faltantes:
        raise ValueError(
            f"Faltan parámetros requeridos: {', '.join(faltantes)}"
        )

    desconocidos = set(parametros_recibidos.keys()) - nombres_esperados

    if desconocidos:
        raise ValueError(
            f"Parámetros no reconocidos para este indicador: "
            f"{', '.join(desconocidos)}"
        )


def listar_indicadores(
    catalog_repo: CatalogRepository,
) -> list[dict]:
    """Construye la respuesta que el LLM va a ver: catálogo completo, legible."""

    indicadores = catalog_repo.listar_indicadores_aprobados()

    return [
        {
            "nombre_sp": ind.nombre_sp,
            "descripcion": ind.descripcion,
            "ejemplos_preguntas": ind.ejemplos_preguntas,
            "parametros": [
                {
                    "nombre": p.nombre,
                    "tipo": p.tipo_dato,
                    "requerido": p.requerido,
                    "ejemplo": p.ejemplo,
                }
                for p in ind.parametros
            ],
        }
        for ind in indicadores
    ]


def ejecutar_indicador(
    catalog_repo: CatalogRepository,
    executor_repo: IndicatorExecutorRepository,
    value_repo: ValueCatalogRepository,
    nombre_sp: str,
    parametros: dict,
) -> dict:
    """
    Flujo completo y seguro de ejecución:

    1. Buscar en catálogo (whitelist) -> si no existe, rechazar.
    2. Validar que esté aprobado.
    3. Validar parámetros requeridos/desconocidos.
    4. Resolver y validar parámetros categóricos.
    5. Ejecutar contra HIS_DB.
    6. Registrar auditoría (éxito o fallo).
    """

    indicador = catalog_repo.obtener_indicador_por_nombre(nombre_sp)

    if indicador is None:
        raise ValueError(
            f"'{nombre_sp}' no está registrado en el catálogo autorizado."
        )

    if not indicador.es_ejecutable():
        raise ValueError(
            f"'{nombre_sp}' existe pero no está aprobado para ejecución "
            f"(estado actual: {indicador.estado})."
        )
    # 1. Normalizar valores recibidos desde el LLM
    parametros = _normalizar_parametros(parametros)
    
    # 2. Validar estructura de parámetros
    _validar_parametros(indicador, parametros)

    # 3. Resolver y validar valores categóricos
    #    Si no encuentra una coincidencia confiable,
    #    lanza una excepción y NO se ejecuta el SP.
    parametros = _resolver_parametros_categoricos(
        value_repo,
        indicador,
        parametros,
    )

    inicio = time.perf_counter()

    try:
        # 4. Solo aquí se ejecuta realmente el procedimiento SQL
        filas = executor_repo.ejecutar(
            nombre_sp=indicador.nombre_sp,
            parametros=parametros,
            timeout_segundos=indicador.timeout_segundos,
            max_filas_retorno=indicador.max_filas_retorno,
        )

        duracion_ms = int(
            (time.perf_counter() - inicio) * 1000
        )

        catalog_repo.registrar_ejecucion(
            indicador_id=indicador.id,
            parametros_enviados=parametros,
            exitoso=True,
            filas_retornadas=len(filas),
            duracion_ms=duracion_ms,
        )

        return {
            "exitoso": True,
            "filas": filas,
            "total_filas": len(filas),
        }

    except Exception as e:
        duracion_ms = int(
            (time.perf_counter() - inicio) * 1000
        )

        catalog_repo.registrar_ejecucion(
            indicador_id=indicador.id,
            parametros_enviados=parametros,
            exitoso=False,
            filas_retornadas=None,
            duracion_ms=duracion_ms,
            mensaje_error=str(e),
        )

        raise


def _resolver_parametros_categoricos(
    value_repo: ValueCatalogRepository,
    indicador: Indicador,
    parametros: dict,
) -> dict:

    resueltos = dict(parametros)

    for nombre, valor in parametros.items():

        valores_validos = value_repo.obtener_valores_validos(nombre)

        if valores_validos is None:
            continue

        umbral = value_repo.obtener_umbral(nombre)

        resueltos[nombre] = resolver_lista_o_valor(
            valor,
            valores_validos,
            umbral,
        )

    return resueltos