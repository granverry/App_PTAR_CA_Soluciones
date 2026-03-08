import math


def _redondear_arriba_1_decimal(valor):
    return math.ceil(valor * 10) / 10 if valor > 0 else 0


def _cs_oxigeno_20():
    # Valor de referencia usado por tu Excel (celda B16 del anexo)
    return 9.2


def _cs_saturacion_agua_limpia(temp_c):
    """
    Tabla interna para reemplazar el VLOOKUP del anexo.
    Valores típicos de saturación de O2 (mg/L) a presión atmosférica estándar.
    Se interpola linealmente.
    """
    tabla = {
        0: 14.6, 1: 14.2, 2: 13.8, 3: 13.5, 4: 13.1, 5: 12.8,
        6: 12.5, 7: 12.2, 8: 11.9, 9: 11.6, 10: 11.3, 11: 11.1,
        12: 10.8, 13: 10.6, 14: 10.4, 15: 10.2, 16: 10.0, 17: 9.7,
        18: 9.5, 19: 9.4, 20: 9.2, 21: 9.0, 22: 8.9, 23: 8.7,
        24: 8.5, 25: 8.4, 26: 8.2, 27: 8.1, 28: 7.9, 29: 7.8, 30: 7.6
    }

    if temp_c <= 0:
        return tabla[0]
    if temp_c >= 30:
        return tabla[30]

    t1 = math.floor(temp_c)
    t2 = math.ceil(temp_c)

    if t1 == t2:
        return tabla[t1]

    return tabla[t1] + (tabla[t2] - tabla[t1]) * (temp_c - t1) / (t2 - t1)


def calcular_lodos_activados_excel_v3(
    poblacion_servida,
    q_entrada_lps,
    numero_reactores,
    altitud_m,
    temperatura_c,
    dbo_afluente_mg_l,
    st_afluente_mg_l,
    ntk_afluente_mg_l,
    fraccion_volatil_st,
    fraccion_biodegradable_efluente,
    factor_dbol_dbo5,
    st_lodo_sedimentado_mg_l,
    dbo_efluente_esperada_mg_l,
    sst_efluente_esperado_mg_l,
    Ks,
    k,
    Y,
    kd,
    trh_supuesto_d,
    relacion_fm_referencia,
    porcentaje_recirculacion_referencia,
    edad_lodo_d,
    fb_prima,
    altura_util_tanque_m,
    borde_libre_m,
    relacion_ancho_largo,
    od_reactor_mg_l,
    factor_correcion_caracteristicas_agua,
    factor_correcion_contaminantes,
    coef_temp,
    eficiencia_transferencia_difusor_por_m,
    perdida_carga_m,
    cantidad_equipos_aireacion,
    blower_caudal_max_cfm,
    blower_presion_max_inH2O,
    blower_potencia_hp,
    difusor_caudal_nm3_h
):
    # -------------------------------------------------
    # DATOS BASE
    # -------------------------------------------------
    q_por_reactor_lps = q_entrada_lps / numero_reactores if numero_reactores > 0 else 0
    q_por_reactor_m3_d = q_por_reactor_lps * 86.4

    carga_dbo_kg_d = dbo_afluente_mg_l * q_por_reactor_lps * 0.0864
    carga_st_kg_d = st_afluente_mg_l * q_por_reactor_lps * 0.0864

    # -------------------------------------------------
    # PASO 1. ESTIMACIÓN DE LA DBO SOLUBLE EN EL EFLUENTE
    # Excel filas 52 a 57
    # -------------------------------------------------
    fraccion_biodegradable_solidos_efluente = sst_efluente_esperado_mg_l * fraccion_biodegradable_efluente
    dbo_ultima_solidos_biodegradables_efluente = fraccion_biodegradable_solidos_efluente * 1.42
    dbo_solidos_suspendidos_efluente = dbo_ultima_solidos_biodegradables_efluente * factor_dbol_dbo5
    dbo_soluble_escapa_mg_l = dbo_efluente_esperada_mg_l - dbo_solidos_suspendidos_efluente

    eficiencia_tratamiento_biologico = (
        (dbo_afluente_mg_l - dbo_soluble_escapa_mg_l) / dbo_afluente_mg_l
        if dbo_afluente_mg_l > 0 else 0
    )
    eficiencia_conjunta_planta = (
        (dbo_afluente_mg_l - dbo_efluente_esperada_mg_l) / dbo_afluente_mg_l
        if dbo_afluente_mg_l > 0 else 0
    )

    # -------------------------------------------------
    # PASO 2. CÁLCULO DEL VOLUMEN DEL REACTOR
    # Excel filas 61 a 81
    # -------------------------------------------------
    theta_c_min_d = 1 / ((Y * k) - kd) if ((Y * k) - kd) != 0 else 0
    s_min_mg_l = Ks * kd * theta_c_min_d

    dbo_salida_recalculada_mg_l = (
        Ks * (1 + kd * edad_lodo_d) / ((Y * k * edad_lodo_d) - (1 + kd * edad_lodo_d))
        if ((Y * k * edad_lodo_d) - (1 + kd * edad_lodo_d)) != 0 else 0
    )

    fraccion_biodegradable_ssv = fb_prima / (1 + (1 - fb_prima) * kd * edad_lodo_d)

    # Concentración MLVSS
    ssvlm_mg_l = math.ceil(
        Y * (dbo_afluente_mg_l - dbo_soluble_escapa_mg_l) * edad_lodo_d
        / (trh_supuesto_d * (1 + kd * fraccion_biodegradable_ssv * edad_lodo_d))
    ) if trh_supuesto_d > 0 else 0

    # Volumen reactor
    volumen_reactor_m3 = (
        Y * q_por_reactor_lps * edad_lodo_d * 86.4 * (dbo_afluente_mg_l - dbo_salida_recalculada_mg_l)
        / (ssvlm_mg_l * (1 + (kd * fraccion_biodegradable_ssv * edad_lodo_d)))
        if ssvlm_mg_l > 0 else 0
    )

    # Carga Organica
    carga_organica_volumetrica = carga_dbo_kg_d / volumen_reactor_m3 if volumen_reactor_m3 > 0 else 0
    relacion_fm_calculada = carga_organica_volumetrica / (ssvlm_mg_l / 1000) if ssvlm_mg_l > 0 else 0
    trh_recalculado_h = volumen_reactor_m3 / (q_por_reactor_lps * 3.6) if q_por_reactor_lps > 0 else 0

    # Dimensiones del Reactor
    altura_total_tanque_m = altura_util_tanque_m + borde_libre_m
    area_tanque_m2 = volumen_reactor_m3 / altura_util_tanque_m if altura_util_tanque_m > 0 else 0
    ancho_tanque_m = _redondear_arriba_1_decimal(math.sqrt(area_tanque_m2 / relacion_ancho_largo)) if relacion_ancho_largo > 0 else 0
    longitud_tanque_m = _redondear_arriba_1_decimal(area_tanque_m2 / ancho_tanque_m) if ancho_tanque_m > 0 else 0

    diametro_tanque_cil_m = altura_util_tanque_m
    longitud_tanque_cil_m = _redondear_arriba_1_decimal(
        4 * volumen_reactor_m3 / (math.pi * diametro_tanque_cil_m ** 2)
    ) if diametro_tanque_cil_m > 0 else 0

    # -------------------------------------------------
    # PASO 3. PRODUCCIÓN DE LODOS
    # Excel filas 85 a 97
    # -------------------------------------------------
    fraccion_biomasa_activa = (
        (edad_lodo_d / trh_recalculado_h / 24)
        * (Y * (dbo_afluente_mg_l - dbo_salida_recalculada_mg_l) / (1 + kd * edad_lodo_d))
        if trh_recalculado_h > 0 else 0
    )

    relacion_biomasa_activa_ssv = fraccion_biomasa_activa / ssvlm_mg_l if ssvlm_mg_l > 0 else 0
    fraccion_inorganica_biomasa = (1 / 9) * ssvlm_mg_l
    concentracion_solidos_inorganicos_afluente = (1 - fraccion_volatil_st) * st_afluente_mg_l
    concentracion_solidos_totales_reactor = (
        ssvlm_mg_l + fraccion_inorganica_biomasa + concentracion_solidos_inorganicos_afluente
    )

    rendimiento_observado = Y / (1 + (kd * fraccion_biodegradable_ssv * edad_lodo_d))
    masa_lodo_volatil_purgado_kg_d = (
        rendimiento_observado * q_por_reactor_m3_d * (dbo_afluente_mg_l - dbo_soluble_escapa_mg_l) / 1000
    )
    masa_lodo_total_kg_d = masa_lodo_volatil_purgado_kg_d / fraccion_volatil_st if fraccion_volatil_st > 0 else 0
    masa_lodo_purgar_kg_d = masa_lodo_total_kg_d - (q_por_reactor_m3_d * sst_efluente_esperado_mg_l) / 1000

    caudal_purga_lodos_m3_d = volumen_reactor_m3 / edad_lodo_d if edad_lodo_d > 0 else 0
    caudal_recirculacion_m3_d = (
        q_por_reactor_m3_d * ssvlm_mg_l / ((st_lodo_sedimentado_mg_l * fraccion_volatil_st) - ssvlm_mg_l)
        if ((st_lodo_sedimentado_mg_l * fraccion_volatil_st) - ssvlm_mg_l) != 0 else 0
    )
    relacion_recirculacion = caudal_recirculacion_m3_d / q_por_reactor_m3_d if q_por_reactor_m3_d > 0 else 0
    concentracion_solidos_recirculados_mg_l = (
        ssvlm_mg_l * (relacion_recirculacion + 1) / relacion_recirculacion
        if relacion_recirculacion > 0 else 0
    )

    # -------------------------------------------------
    # PASO 4. NUTRIENTES Y OXÍGENO
    # Excel filas 101 a 130
    # -------------------------------------------------
    requerimiento_nitrogeno_kg_d = (
        (0.123 * (fraccion_biodegradable_ssv / fb_prima) * masa_lodo_volatil_purgado_kg_d)
        + (0.07 * (1 - (fraccion_biodegradable_ssv / fb_prima)) * masa_lodo_volatil_purgado_kg_d)
    )
    requerimiento_fosforo_kg_d = (
        (0.026 * (fraccion_biodegradable_ssv / fb_prima) * masa_lodo_volatil_purgado_kg_d)
        + (0.01 * (1 - (fraccion_biodegradable_ssv / fb_prima)) * masa_lodo_volatil_purgado_kg_d)
    )

    dbo_removida_proceso_kg_d = q_por_reactor_m3_d * (dbo_afluente_mg_l - dbo_salida_recalculada_mg_l) / 1000

    demanda_sintesis_kg_o2_d = (
        q_por_reactor_m3_d * 0.001 * (dbo_afluente_mg_l - dbo_salida_recalculada_mg_l)
        * (1.46 - (1.42 * Y / (1 + kd * fraccion_biodegradable_ssv * edad_lodo_d)))
    )

    demanda_endogena_kg_o2_d = (
        1.42 * fraccion_biodegradable_ssv * kd * ssvlm_mg_l * volumen_reactor_m3 / 1000
    )

    demanda_nitrificacion_kg_o2_d = 4.57 * q_por_reactor_m3_d * ntk_afluente_mg_l / 1000

    requerimiento_oxigeno_kg_o2_d = (
        demanda_sintesis_kg_o2_d + demanda_endogena_kg_o2_d + demanda_nitrificacion_kg_o2_d
    )

    factor_correcion_cs_altitud = 1 - (altitud_m / 9450)
    cs_saturacion_mg_l = _cs_saturacion_agua_limpia(temperatura_c)

    tasa_transferencia_oxigeno_estandar_kg_o2_h = (
        requerimiento_oxigeno_kg_o2_d
        / (
            (((factor_correcion_contaminantes * factor_correcion_cs_altitud * cs_saturacion_mg_l) - od_reactor_mg_l)
             / _cs_oxigeno_20())
            * 24
            * factor_correcion_caracteristicas_agua
            * (coef_temp ** (temperatura_c - 20))
        )
    )

    caudal_aire_nm3_h = requerimiento_oxigeno_kg_o2_d / (0.23 * 1.21 * 24)

    profundidad_difusores_m = altura_util_tanque_m - 0.2
    eficiencia_transferencia_difusor = profundidad_difusores_m * eficiencia_transferencia_difusor_por_m / 100

    caudal_aire_corregido_nm3_h = (
        caudal_aire_nm3_h / eficiencia_transferencia_difusor
        if eficiencia_transferencia_difusor > 0 else 0
    )

    presion_relativa_bar = altura_util_tanque_m * 10000 / 100000

    caudal_aire_volumetrico_m3_h = (
        caudal_aire_corregido_nm3_h
        * ((1.01325 + presion_relativa_bar) / 1.01325)
        * (273.15 / (273.15 + temperatura_c))
    )

    razon_utilizacion_oxigeno = (
        tasa_transferencia_oxigeno_estandar_kg_o2_h / caudal_aire_nm3_h
        if caudal_aire_nm3_h > 0 else 0
    )

    razon_utilizacion_oxigeno_por_m = (
        razon_utilizacion_oxigeno / profundidad_difusores_m
        if profundidad_difusores_m > 0 else 0
    )

    eficiencia_transferencia_oxigeno = 0.334 * razon_utilizacion_oxigeno

    potencia_requerida_kw = (
        caudal_aire_corregido_nm3_h * 1000 * 9.81 * (profundidad_difusores_m + perdida_carga_m)
        / (0.7 * 3600 * 1000)
    )

    potencia_requerida_hp = potencia_requerida_kw / 0.735
    eficiencia_oxigenacion_proceso = (
        tasa_transferencia_oxigeno_estandar_kg_o2_h * 1.5 / potencia_requerida_kw
        if potencia_requerida_kw > 0 else 0
    )
    densidad_potencia_w_m3 = (
        potencia_requerida_kw * 1000 / volumen_reactor_m3
        if volumen_reactor_m3 > 0 else 0
    )

    # -------------------------------------------------
    # PASO 5. SELECCIÓN DE AIREADOR Y DIFUSORES
    # Excel filas 134 a 144
    # -------------------------------------------------
    caudal_aire_por_equipo_nm3_h = (
        caudal_aire_corregido_nm3_h / cantidad_equipos_aireacion
        if cantidad_equipos_aireacion > 0 else 0
    )

    caudal_air_lift_nm3_h = caudal_aire_por_equipo_nm3_h * 0.25
    potencia_por_equipo_hp = (
        potencia_requerida_hp / cantidad_equipos_aireacion
        if cantidad_equipos_aireacion > 0 else 0
    )

    caudal_max_equipo_propuesto_nm3_h = blower_caudal_max_cfm * 1.699
    presion_max_equipo_propuesto_m = blower_presion_max_inH2O * 0.0254

    numero_difusores = math.ceil(caudal_aire_volumetrico_m3_h / difusor_caudal_nm3_h) if difusor_caudal_nm3_h > 0 else 0

    volumen_aire_por_dbo_aplicada = (
        caudal_aire_corregido_nm3_h * 24 / carga_dbo_kg_d
        if carga_dbo_kg_d > 0 else 0
    )

    volumen_aire_por_dbo_removida = (
        caudal_aire_corregido_nm3_h * 24 / (q_entrada_lps * (dbo_afluente_mg_l - dbo_efluente_esperada_mg_l) * 0.0864)
        if (q_entrada_lps * (dbo_afluente_mg_l - dbo_efluente_esperada_mg_l) * 0.0864) > 0 else 0
    )

    return {
        # Datos base
        "Población servida": round(poblacion_servida, 2),
        "Caudal total de entrada (L/s)": round(q_entrada_lps, 2),
        "Número de reactores": round(numero_reactores, 2),
        "Caudal por reactor (L/s)": round(q_por_reactor_lps, 2),
        "Caudal por reactor (m3/d)": round(q_por_reactor_m3_d, 2),
        "Carga DBO afluente (kg/d)": round(carga_dbo_kg_d, 2),
        "Carga ST afluente (kg/d)": round(carga_st_kg_d, 2),

        # Paso 1
        "Fracción biodegradable de sólidos del efluente (mg/L)": round(fraccion_biodegradable_solidos_efluente, 4),
        "DBO última de sólidos biodegradables del efluente (mg/L)": round(dbo_ultima_solidos_biodegradables_efluente, 4),
        "DBO de SST del efluente (mg/L)": round(dbo_solidos_suspendidos_efluente, 4),
        "DBO soluble que escapa del tratamiento (mg/L)": round(dbo_soluble_escapa_mg_l, 4),
        "Eficiencia tratamiento biológico": round(eficiencia_tratamiento_biologico, 6),
        "Eficiencia conjunta de planta": round(eficiencia_conjunta_planta, 6),

        # Paso 2
        "Tiempo de retención celular mínima (d)": round(theta_c_min_d, 6),
        "Concentración mínima de sustrato (mg/L)": round(s_min_mg_l, 6),
        "DBO salida recalculada (mg/L)": round(dbo_salida_recalculada_mg_l, 6),
        "Fracción biodegradable de SSV generados": round(fraccion_biodegradable_ssv, 6),
        "SSVLM (mg/L)": round(ssvlm_mg_l, 2),
        "Volumen del reactor (m3)": round(volumen_reactor_m3, 6),
        "Carga orgánica volumétrica (kg DBO/m3.d)": round(carga_organica_volumetrica, 6),
        "Relación F/M calculada": round(relacion_fm_calculada, 6),
        "TRH recalculado (h)": round(trh_recalculado_h, 6),
        "Altura útil tanque (m)": round(altura_util_tanque_m, 2),
        "Borde libre (m)": round(borde_libre_m, 2),
        "Altura total tanque (m)": round(altura_total_tanque_m, 2),
        "Área tanque (m2)": round(area_tanque_m2, 6),
        "Ancho tanque rectangular (m)": round(ancho_tanque_m, 2),
        "Longitud tanque rectangular (m)": round(longitud_tanque_m, 2),
        "Diámetro tanque cilíndrico (m)": round(diametro_tanque_cil_m, 2),
        "Longitud tanque cilíndrico (m)": round(longitud_tanque_cil_m, 2),

        # Paso 3
        "Fracción de biomasa activa": round(fraccion_biomasa_activa, 6),
        "Relación biomasa activa / SSV": round(relacion_biomasa_activa_ssv, 6),
        "Fracción inorgánica biomasa (mg/L)": round(fraccion_inorganica_biomasa, 6),
        "Sólidos inorgánicos afluente (mg/L)": round(concentracion_solidos_inorganicos_afluente, 6),
        "Sólidos totales reactor (mg/L)": round(concentracion_solidos_totales_reactor, 6),
        "Rendimiento observado": round(rendimiento_observado, 6),
        "Masa lodo volatil purgado (kg/d)": round(masa_lodo_volatil_purgado_kg_d, 6),
        "Masa lodo total (kg/d)": round(masa_lodo_total_kg_d, 6),
        "Masa lodo a purgar (kg/d)": round(masa_lodo_purgar_kg_d, 6),
        "Caudal de purga de lodos (m3/d)": round(caudal_purga_lodos_m3_d, 6),
        "Caudal de recirculación (m3/d)": round(caudal_recirculacion_m3_d, 6),
        "Relación de recirculación": round(relacion_recirculacion, 6),
        "Concentración sólidos recirculados (mg/L)": round(concentracion_solidos_recirculados_mg_l, 6),

        # Paso 4
        "Requerimiento de N (kg/d)": round(requerimiento_nitrogeno_kg_d, 6),
        "Requerimiento de P (kg/d)": round(requerimiento_fosforo_kg_d, 6),
        "DBO removida en el proceso (kg/d)": round(dbo_removida_proceso_kg_d, 6),
        "Demanda por síntesis (kg O2/d)": round(demanda_sintesis_kg_o2_d, 6),
        "Demanda endógena (kg O2/d)": round(demanda_endogena_kg_o2_d, 6),
        "Demanda por nitrificación (kg O2/d)": round(demanda_nitrificacion_kg_o2_d, 6),
        "Requerimiento de oxígeno (kg O2/d)": round(requerimiento_oxigeno_kg_o2_d, 6),
        "Factor corrección Cs por altitud": round(factor_correcion_cs_altitud, 6),
        "Cs saturación (mg/L)": round(cs_saturacion_mg_l, 6),
        "OD a mantener en reactor (mg/L)": round(od_reactor_mg_l, 6),
        "Tasa transferencia estándar O2 (kg O2/h)": round(tasa_transferencia_oxigeno_estandar_kg_o2_h, 6),
        "Caudal de aire normal (Nm3/h)": round(caudal_aire_nm3_h, 6),
        "Eficiencia transferencia difusor": round(eficiencia_transferencia_difusor, 6),
        "Caudal de aire corregido (Nm3/h)": round(caudal_aire_corregido_nm3_h, 6),
        "Presión relativa (bar)": round(presion_relativa_bar, 6),
        "Caudal de aire volumétrico (m3/h)": round(caudal_aire_volumetrico_m3_h, 6),
        "Razón utilización O2": round(razon_utilizacion_oxigeno, 6),
        "Razón utilización O2 por m": round(razon_utilizacion_oxigeno_por_m, 6),
        "Eficiencia transferencia O2": round(eficiencia_transferencia_oxigeno, 6),
        "Potencia requerida (kW)": round(potencia_requerida_kw, 6),
        "Potencia requerida (HP)": round(potencia_requerida_hp, 6),
        "Eficiencia oxigenación proceso": round(eficiencia_oxigenacion_proceso, 6),
        "Densidad de potencia (W/m3)": round(densidad_potencia_w_m3, 6),

        # Paso 5
        "Cantidad equipos aireación": round(cantidad_equipos_aireacion, 2),
        "Caudal de aire por equipo (Nm3/h)": round(caudal_aire_por_equipo_nm3_h, 6),
        "Caudal air lift (Nm3/h)": round(caudal_air_lift_nm3_h, 6),
        "Potencia por equipo (HP)": round(potencia_por_equipo_hp, 6),
        "Caudal máximo equipo propuesto (Nm3/h)": round(caudal_max_equipo_propuesto_nm3_h, 6),
        "Presión máxima equipo propuesto (m)": round(presion_max_equipo_propuesto_m, 6),
        "Potencia equipo propuesto (HP)": round(blower_potencia_hp, 6),
        "Caudal por difusor (Nm3/h)": round(difusor_caudal_nm3_h, 6),
        "Número de difusores": numero_difusores,
        "Volumen aire por DBO aplicada": round(volumen_aire_por_dbo_aplicada, 6),
        "Volumen aire por DBO removida": round(volumen_aire_por_dbo_removida, 6),
    }