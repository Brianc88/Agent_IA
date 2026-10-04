from mcp_db_agent.domain.value_matching import resolver_valor


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

    resultado = resolver_valor(
        valor_recibido=entrada,
        valores_validos=valores_validos,
        umbral=90,
    )

    print("=" * 60)
    print(f"ENTRADA: {entrada}")
    print(f"RESUELTO: {resultado.valor_resuelto}")
    print(f"CORREGIDO: {resultado.fue_corregido}")
    print(f"ALTERNATIVAS: {resultado.alternativas}")