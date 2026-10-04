from mcp_db_agent.domain.value_matching import resolver_lista_o_valor


valores_validos = [
    "NUEVA EPS",
    "NUEVA EPS SUBSIDIADO",
    "NUEVA EPS CONTRIBUTIVO",
    "CAJACOPI EPS S.A.S",
    "SEGUROS GENERALES SURAMERICANA S.A.",
]


entradas = [
    "Nueva EPS",
    "CAJACOPI EPS SAS",
    "CAJACOPI XYZ",
]


for entrada in entradas:

    print("=" * 60)
    print(f"ENTRADA: {entrada}")

    try:

        resultado = resolver_lista_o_valor(
            valor=entrada,
            valores_validos=valores_validos,
            umbral=90,
        )

        print(f"RESULTADO: {resultado}")

    except ValueError as e:

        print(f"ERROR CONTROLADO: {e}")