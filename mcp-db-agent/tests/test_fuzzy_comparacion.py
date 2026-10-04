from rapidfuzz import fuzz, process


valores_validos = [
    "NUEVA EPS",
    "NUEVA EPS SUBSIDIADO",
    "NUEVA EPS CONTRIBUTIVO",
    "CAJACOPI EPS S.A.S",
    "SEGUROS GENERALES SURAMERICANA S.A.",
]


entradas = [
    "Nueva EPS",
    "Nueva Eps Subsidiado",
    "CAJACOPI EPS SAS",
    "Seguros Generales",
    "CAJACOPI XYZ",
]


for entrada in entradas:

    print("=" * 60)
    print(f"ENTRADA: {entrada}")

    print("\nTOKEN_SET_RATIO")

    resultados = process.extract(
        entrada.upper(),
        valores_validos,
        scorer=fuzz.token_set_ratio,
        limit=5,
    )

    for valor, score, _ in resultados:
        print(f"{score:.1f} -> {valor}")

    print("\nWRATIO")

    resultados = process.extract(
        entrada.upper(),
        valores_validos,
        scorer=fuzz.WRatio,
        limit=5,
    )

    for valor, score, _ in resultados:
        print(f"{score:.1f} -> {valor}")