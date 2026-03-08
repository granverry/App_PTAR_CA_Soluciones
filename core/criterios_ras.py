criterios_lodos_activados = {

    "F_M_min": 0.05,
    "F_M_max": 0.20,

    "MLSS_min": 2000,
    "MLSS_max": 4000,

    "TRH_min": 4,
    "TRH_max": 8,

    "SRT_min": 8,
    "SRT_max": 20
}


def validar_criterios_lodos(fm, mlss):

    advertencias = []

    if fm < criterios_lodos_activados["F_M_min"]:
        advertencias.append("Relación F/M demasiado baja")

    if fm > criterios_lodos_activados["F_M_max"]:
        advertencias.append("Relación F/M demasiado alta")

    if mlss < criterios_lodos_activados["MLSS_min"]:
        advertencias.append("MLSS por debajo del rango recomendado")

    if mlss > criterios_lodos_activados["MLSS_max"]:
        advertencias.append("MLSS demasiado alto")

    return advertencias