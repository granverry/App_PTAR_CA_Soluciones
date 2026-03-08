def calcular_perfil_hidraulico(cota_inicial, unidades):
    """
    unidades: lista de diccionarios con:
    {
        "unidad": "Rejillas",
        "perdida_m": 0.05
    }
    """

    resultados = []
    cota_actual = cota_inicial

    for item in unidades:
        unidad = item["unidad"]
        perdida = item["perdida_m"]

        cota_entrada = cota_actual
        cota_salida = cota_entrada - perdida

        resultados.append({
            "Unidad": unidad,
            "Cota entrada (m)": round(cota_entrada, 3),
            "Pérdida (m)": round(perdida, 3),
            "Cota salida (m)": round(cota_salida, 3)
        })

        cota_actual = cota_salida

    return resultados