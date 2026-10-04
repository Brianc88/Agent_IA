from mcp_db_agent.domain.value_matching import resolver_valor

from rapidfuzz import fuzz, process


valores_validos = [
    "NUEVA EPS",
    "NUEVA EPS SUBSIDIADO",
    "NUEVA EPS CONTRIBUTIVO",
    "CAJACOPI EPS S.A.S",
    "SEGUROS GENERALES SURAMERICANA S.A."
]


pruebas = [
    "Nueva EPS",
    "Nueva Eps Subsidiado",
    "CAJACOPI EPS SAS",
    "Seguros Generales",
    "CAJACOPI XYZ",
]


for valor in pruebas:
    print("\n" + "=" * 60)
    print(f"ENTRADA: {valor}")

    mejores = process.extract(
        valor.strip().upper(),
        [v.strip().upper() for v in valores_validos],
        scorer=fuzz.token_set_ratio,
        limit=5,
    )

    for candidato, score, _ in mejores:
        print(f"{score:.1f} -> {candidato}")