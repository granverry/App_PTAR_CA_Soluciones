def seleccionar_tren_tratamiento(
    tipo_agua,
    caudal_lps,
    dbo,
    sst,
    grasas,
    temperatura,
    area_disponible,
    energia_disponible,
    nivel_operacion,
    requiere_remocion_alta
):
    tren = []
    justificacion = []
    alternativas = []

    # 1. Pretratamiento básico
    tren.extend(["Rejillas", "Desarenador"])

    if grasas >= 100:
        tren.append("Trampa de Grasas")
        justificacion.append("Se incluye trampa de grasas por concentración elevada de grasas y aceites.")

    # 2. Igualación
    if caudal_lps > 20:
        tren.append("Tanque de Igualación")
        justificacion.append("Se recomienda tanque de igualación por caudal medio/alto y posible variabilidad hidráulica.")

    # 3. Selección del tratamiento biológico principal
    if tipo_agua == "Doméstica":
        if area_disponible == "Amplia" and energia_disponible in ["Baja", "Media"] and nivel_operacion == "Básico":
            tren.extend(["Laguna Facultativa", "Humedal Construido"])
            justificacion.append("Se recomienda sistema natural por amplia disponibilidad de área y baja complejidad operativa.")
            alternativas.append("UASB + Humedal Construido")
        elif temperatura >= 20 and dbo >= 250 and energia_disponible in ["Media", "Alta"]:
            tren.extend(["Sedimentador Primario", "Reactor UASB", "Lodos Activados", "Sedimentador Secundario"])
            justificacion.append("Se recomienda tren anaerobio-aerobio por temperatura favorable y carga orgánica media/alta.")
            alternativas.append("UASB + Filtro Percolador + Sedimentador Secundario")
            alternativas.append("MBBR + Sedimentador Secundario")
        elif area_disponible == "Limitada" and energia_disponible == "Alta":
            tren.extend(["Sedimentador Primario", "Lodos Activados", "Sedimentador Secundario"])
            justificacion.append("Se recomienda sistema compacto por área limitada y buena disponibilidad de energía.")
            alternativas.append("MBBR + Sedimentador Secundario")
        else:
            tren.extend(["Sedimentador Primario", "Filtro Percolador", "Sedimentador Secundario"])
            justificacion.append("Se recomienda filtro percolador como alternativa robusta de operación intermedia.")
            alternativas.append("Lodos Activados + Sedimentador Secundario")

    elif tipo_agua == "Doméstica con alta grasa":
        tren.extend(["Trampa de Grasas", "Sedimentador Primario"])
        if area_disponible == "Amplia":
            tren.extend(["Laguna Facultativa", "Humedal Construido"])
            justificacion.append("Por presencia de grasas y disponibilidad de área, se favorece tratamiento natural con operación simple.")
            alternativas.append("UASB + Humedal Construido")
        else:
            tren.extend(["Reactor UASB", "Lodos Activados", "Sedimentador Secundario"])
            justificacion.append("Se propone línea combinada para controlar carga orgánica y grasas remanentes.")
            alternativas.append("Filtro Percolador + Sedimentador Secundario")

    elif tipo_agua == "Industrial biodegradable":
        if dbo > 500 and temperatura >= 20:
            tren.extend(["Ecualización", "Reactor UASB", "Lodos Activados", "Sedimentador Secundario"])
            justificacion.append("Se recomienda pretratamiento hidráulico y etapa anaerobia por alta carga biodegradable.")
            alternativas.append("UASB + MBBR")
        else:
            tren.extend(["Ecualización", "Lodos Activados", "Sedimentador Secundario"])
            justificacion.append("Se recomienda línea aerobia por carga moderada y necesidad de control más estable.")
            alternativas.append("MBBR + Sedimentador Secundario")

    else:
        tren.extend(["Sedimentador Primario", "Lodos Activados", "Sedimentador Secundario"])
        justificacion.append("Se propone tren aeróbico convencional como solución base.")
        alternativas.append("Filtro Percolador + Sedimentador Secundario")

    # 4. Tratamiento terciario / desinfección
    if requiere_remocion_alta:
        tren.extend(["Filtración Mixta", "Desinfección"])
        justificacion.append("Se adiciona pulimiento terciario por exigencia alta en la calidad del efluente.")
    else:
        tren.append("Desinfección")
        justificacion.append("Se incluye desinfección final como barrera sanitaria.")

    # 5. Manejo de lodos
    tren.append("Lechos de Secado")
    justificacion.append("Se incorpora manejo de lodos mediante lechos de secado como solución base.")

    return {
        "tren_recomendado": tren,
        "justificacion": justificacion,
        "alternativas": alternativas
    }