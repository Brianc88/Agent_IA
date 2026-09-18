"""
Tools MCP: la capa que el LLM ve y usa directamente.
Aquí vive la lógica de: buscar en catálogo, validar, ejecutar, auditar.
"""

import json
import time

from mcp_db_agent.domain.models import Indicador
from mcp_db_agent.domain.repositories import CatalogRepository, IndicatorExecutorRepository


def _validar_parametros(indicador: Indicador, parametros_recibidos: dict) -> None:
    """Valida que los parámetros requeridos estén presentes. Lanza ValueError si no."""
    nombres_esperados = {p.nombre for p in indicador.parametros}
    faltantes = [
        p.nombre for p in indicador.parametros
        if p.requerido and p.nombre not in parametros_recibidos
    ]
    if faltantes:
        raise ValueError(f"Faltan parámetros requeridos: {', '.join(faltantes)}")

    desconocidos = set(parametros_recibidos.keys()) - nombres_esperados
    if desconocidos:
        raise ValueError(f"Parámetros no reconocidos para este indicador: {', '.join(desconocidos)}")


def listar_indicadores(catalog_repo: CatalogRepository) -> list[dict]:
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
    nombre_sp: str,
    parametros: dict,
) -> dict:
    """
    Flujo completo y seguro de ejecución:
    1. Buscar en catálogo (whitelist) -> si no existe, rechazar.
    2. Validar que esté aprobado.
    3. Validar parámetros requeridos/desconocidos.
    4. Ejecutar contra HIS_DB.
    5. Registrar auditoría (éxito o fallo).
    """
    indicador = catalog_repo.obtener_indicador_por_nombre(nombre_sp)

    if indicador is None:
        raise ValueError(f"'{nombre_sp}' no está registrado en el catálogo autorizado.")

    if not indicador.es_ejecutable():
        raise ValueError(f"'{nombre_sp}' existe pero no está aprobado para ejecución (estado actual: {indicador.estado}).")

    _validar_parametros(indicador, parametros)

    inicio = time.perf_counter()
    try:
        filas = executor_repo.ejecutar(
            nombre_sp=indicador.nombre_sp,
            parametros=parametros,
            timeout_segundos=indicador.timeout_segundos,
            max_filas_retorno=indicador.max_filas_retorno,
        )
        duracion_ms = int((time.perf_counter() - inicio) * 1000)

        catalog_repo.registrar_ejecucion(
            indicador_id=indicador.id,
            parametros_enviados=parametros,
            exitoso=True,
            filas_retornadas=len(filas),
            duracion_ms=duracion_ms,
        )
        return {"exitoso": True, "filas": filas, "total_filas": len(filas)}

    except Exception as e:
        duracion_ms = int((time.perf_counter() - inicio) * 1000)
        catalog_repo.registrar_ejecucion(
            indicador_id=indicador.id,
            parametros_enviados=parametros,
            exitoso=False,
            filas_retornadas=None,
            duracion_ms=duracion_ms,
            mensaje_error=str(e),
        )
        raise