"""
Lógica de resolución de valores: compara un texto recibido contra una lista
de valores reales y decide si coincide, se auto-corrige, o queda ambiguo.
No depende de SQL ni de ninguna infraestructura externa.
"""

from dataclasses import dataclass

from rapidfuzz import fuzz, process


@dataclass
class ResultadoMatch:
    valor_resuelto: str | None   # el valor real a usar, si se resolvió
    fue_corregido: bool          # True si no fue coincidencia exacta
    alternativas: list[str]      # sugerencias, solo si NO se resolvió


def resolver_valor(valor_recibido: str, valores_validos: list[str], umbral: int) -> ResultadoMatch:
    normalizado = valor_recibido.strip().upper()
    mapa_normalizado_a_original = {v.strip().upper(): v for v in valores_validos}

    # 1. Coincidencia exacta tras normalizar (mayúsculas/espacios) -> no es una "corrección"
    if normalizado in mapa_normalizado_a_original:
        return ResultadoMatch(
            valor_resuelto=mapa_normalizado_a_original[normalizado],
            fue_corregido=False,
            alternativas=[],
        )

    # 2. Fuzzy matching contra la lista real
    candidatos = list(mapa_normalizado_a_original.keys())
    mejores = process.extract(normalizado, candidatos, scorer=fuzz.WRatio, limit=3)

    if mejores and mejores[0][1] >= umbral:
        valor_original = mapa_normalizado_a_original[mejores[0][0]]
        return ResultadoMatch(valor_resuelto=valor_original, fue_corregido=True, alternativas=[])

    # 3. No hay coincidencia confiable -> devolver alternativas, no adivinar
    alternativas = [mapa_normalizado_a_original[m[0]] for m in mejores]
    return ResultadoMatch(valor_resuelto=None, fue_corregido=False, alternativas=alternativas)