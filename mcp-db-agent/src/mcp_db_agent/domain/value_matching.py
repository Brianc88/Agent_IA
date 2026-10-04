"""
Lógica de resolución de valores: compara un texto recibido contra una lista
de valores reales y decide si coincide, se auto-corrige, o queda ambiguo.
No depende de SQL ni de ninguna infraestructura externa.
"""

from dataclasses import dataclass

from rapidfuzz import fuzz, process
import re

@dataclass
class ResultadoMatch:
    valor_resuelto: str | None   # el valor real a usar, si se resolvió
    fue_corregido: bool          # True si no fue coincidencia exacta
    alternativas: list[str]      # sugerencias, solo si NO se resolvió
    
class AmbiguedadValorError(ValueError):
    def __init__(self, valor_recibido: str, alternativas: list[str]):
        self.valor_recibido = valor_recibido
        self.alternativas = alternativas

        super().__init__(
            f"'{valor_recibido}' no coincide de forma única con los valores válidos. "
            f"Alternativas: {alternativas}"
        )

#################################################################
# Resolver valor
#################################################################
def resolver_valor(
    valor_recibido: str,
    valores_validos: list[str],
    umbral: int,
    margen_ambiguedad: int = 5,
) -> ResultadoMatch:

    normalizado = valor_recibido.strip().upper()

    mapa_normalizado_a_original = {
        v.strip().upper(): v
        for v in valores_validos
    }

    # 1. Coincidencia exacta
    if normalizado in mapa_normalizado_a_original:
        return ResultadoMatch(
            valor_resuelto=mapa_normalizado_a_original[normalizado],
            fue_corregido=False,
            alternativas=[],
        )

    # 2. Normalización compacta para comparar ignorando
    #    espacios y signos de puntuación.
    compacto_recibido = re.sub(
        r"[^A-Z0-9]",
        "",
        normalizado,
    )

    candidatos = [
        candidato
        for candidato in mapa_normalizado_a_original.keys()
        if compacto_recibido in re.sub(
            r"[^A-Z0-9]",
            "",
            candidato,
        )
    ]

    # 3. Si no encontramos candidatos que contengan realmente
    #    la expresión recibida, no hacemos fuzzy matching.
    if not candidatos:
        return ResultadoMatch(
            valor_resuelto=None,
            fue_corregido=False,
            alternativas=[],
        )

    # 4. Buscar mejores coincidencias fuzzy únicamente
    #    entre candidatos semánticamente relacionados.
    mejores = process.extract(
        normalizado,
        candidatos,
        scorer=fuzz.WRatio,
        limit=5,
    )

    if not mejores:
        return ResultadoMatch(
            valor_resuelto=None,
            fue_corregido=False,
            alternativas=[],
        )

    # 5. Filtrar por umbral
    candidatos_validos = [
        m
        for m in mejores
        if m[1] >= umbral
    ]

    # 6. No hay coincidencias suficientemente buenas
    if not candidatos_validos:
        return ResultadoMatch(
            valor_resuelto=None,
            fue_corregido=False,
            alternativas=[
                mapa_normalizado_a_original[m[0]]
                for m in mejores[:3]
            ],
        )

    mejor = candidatos_validos[0]

    # 7. Verificar ambigüedad
    if len(candidatos_validos) > 1:

        segundo = candidatos_validos[1]

        diferencia = mejor[1] - segundo[1]

        if diferencia < margen_ambiguedad:
            return ResultadoMatch(
                valor_resuelto=None,
                fue_corregido=False,
                alternativas=[
                    mapa_normalizado_a_original[m[0]]
                    for m in candidatos_validos[:3]
                ],
            )

    # 8. Resolver automáticamente
    return ResultadoMatch(
        valor_resuelto=mapa_normalizado_a_original[mejor[0]],
        fue_corregido=True,
        alternativas=[],
    )
#################################################################
# Resolver lista o valor
#################################################################
def resolver_lista_o_valor(
    valor,
    valores_validos,
    umbral,
):
    if isinstance(valor, list):

        resueltos = []

        for item in valor:

            r = resolver_valor(
                item,
                valores_validos,
                umbral,
            )

            if r.valor_resuelto is None:
                raise AmbiguedadValorError(
                    valor_recibido=item,
                    alternativas=r.alternativas,
                )

            resueltos.append(r.valor_resuelto)

        return resueltos

    else:

        r = resolver_valor(
            valor,
            valores_validos,
            umbral,
        )

        if r.valor_resuelto is None:
            raise AmbiguedadValorError(
                valor_recibido=valor,
                alternativas=r.alternativas,
            )

        return r.valor_resuelto