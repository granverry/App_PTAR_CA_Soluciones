import os
import streamlit as st

from calculos.lodos_activados import calcular_lodos_activados_excel_v3
from core.selector_tren import seleccionar_tren_tratamiento
from diagrams.pfd import generar_pfd_tren, exportar_pfd_tren_png
from diagrams.pfd_lodos import generar_pfd_lodos_activados, exportar_pfd_lodos_png
from reports.memoria_docx import generar_memoria

st.set_page_config(page_title="PTAR Designer", page_icon="💧", layout="wide")

# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------

if "tren_recomendado" not in st.session_state:
    st.session_state["tren_recomendado"] = None

if "justificacion_tren" not in st.session_state:
    st.session_state["justificacion_tren"] = None

if "alternativas_tren" not in st.session_state:
    st.session_state["alternativas_tren"] = None

if "tipo_agua" not in st.session_state:
    st.session_state["tipo_agua"] = None

if "caudal_lps" not in st.session_state:
    st.session_state["caudal_lps"] = None

if "dbo_afluente" not in st.session_state:
    st.session_state["dbo_afluente"] = None

if "resultados_lodos" not in st.session_state:
    st.session_state["resultados_lodos"] = None

if "q_lodos_lps" not in st.session_state:
    st.session_state["q_lodos_lps"] = None

if "q_recirculacion_m3d" not in st.session_state:
    st.session_state["q_recirculacion_m3d"] = None

if "q_purga_m3d" not in st.session_state:
    st.session_state["q_purga_m3d"] = None

if "q_aire_nm3h" not in st.session_state:
    st.session_state["q_aire_nm3h"] = None

if "datos_proyecto" not in st.session_state:
    st.session_state["datos_proyecto"] = None

# -----------------------------
# TITULO PRINCIPAL
# -----------------------------

st.title("💧 PTAR Designer")
st.subheader("Software de Diseño de Plantas de Tratamiento de Aguas Residuales")

# -----------------------------
# MENU LATERAL
# -----------------------------

menu = st.sidebar.selectbox(
"Menú",
[
    "Inicio",
    "Nuevo Proyecto",
    "Diagnóstico de Agua Residual",
    "Recomendación de Tren de Tratamiento",
    "PFD del Tren de Tratamiento",
    "PFD - Lodos Activados",
    "06 - Reactores Aeróbicos - Lodos Activados",
    "Resumen del Proyecto"
]
)

# -------------------------------------------------
# PANTALLA DE INICIO
# -------------------------------------------------

if menu == "Inicio":

    st.title("💧 PTAR Designer")
    st.subheader("Software de Diseño de Plantas de Tratamiento de Aguas Residuales")

    st.write("""
Bienvenido a **PTAR Designer**.

Este software permite:

- Diagnóstico del agua residual
- Selección inteligente del tren de tratamiento
- Diagramas de proceso tipo PFD
- Diseño de unidades de tratamiento
- Generación de memorias de cálculo
""")

    st.info("Seleccione una opción del menú lateral para comenzar.")

# -------------------------------------------------
# NUEVO PROYECTO
# -------------------------------------------------

elif menu == "Nuevo Proyecto":

    st.header("Datos Generales del Proyecto")

    col1, col2 = st.columns(2)

    with col1:
        proyecto = st.text_input("Nombre del Proyecto")
        ubicacion = st.text_input("Ubicación")
        poblacion = st.number_input("Población servida", value=450.0)

    with col2:
        caudal = st.number_input("Caudal medio (L/s)", value=35.0)
        temperatura = st.number_input("Temperatura promedio (°C)", value=26.0)
        area_disponible = st.selectbox(
            "Área disponible para la PTAR",
            ["Limitada", "Moderada", "Amplia"]
        )

    st.session_state["datos_proyecto"] = {
        "Nombre del proyecto": proyecto,
        "Ubicación": ubicacion,
        "Población": poblacion,
        "Caudal de entrada (L/s)": caudal,
        "Temperatura de diseño (°C)": temperatura,
        "Área disponible": area_disponible
    }

    st.success("Proyecto configurado correctamente")

# -------------------------------------------------
# DIAGNÓSTICO DE AGUA RESIDUAL
# -------------------------------------------------

elif menu == "Diagnóstico de Agua Residual":

    st.header("Caracterización del Agua Residual")

    col1, col2 = st.columns(2)

    with col1:
        dbo = st.number_input("DBO5 afluente (mg/L)", value=260.0)
        sst = st.number_input("SST afluente (mg/L)", value=260.0)
        grasas = st.number_input("Grasas y aceites (mg/L)", value=50.0)

    with col2:
        ntk = st.number_input("NTK (mg/L)", value=75.0)
        ph = st.number_input("pH", value=7.0)
        temperatura = st.number_input("Temperatura del agua (°C)", value=26.0)

    st.success("Caracterización registrada")

# -------------------------------------------------
# RECOMENDACIÓN DE TREN DE TRATAMIENTO
# -------------------------------------------------

elif menu == "Recomendación de Tren de Tratamiento":

    st.header("Motor Inteligente de Selección del Tren de Tratamiento")

    col1, col2 = st.columns(2)

    with col1:
        tipo_agua = st.selectbox(
            "Tipo de agua residual",
            ["Doméstica", "Doméstica con alta grasa", "Industrial biodegradable", "Otra"]
        )

        caudal_lps = st.number_input("Caudal de diseño (L/s)", value=35.0)
        dbo = st.number_input("DBO afluente (mg/L)", value=260.0)
        sst = st.number_input("SST afluente (mg/L)", value=260.0)
        grasas = st.number_input("Grasas y aceites (mg/L)", value=50.0)

    with col2:
        temperatura = st.number_input("Temperatura del agua (°C)", value=26.0)

        area_disponible = st.selectbox(
            "Área disponible",
            ["Limitada", "Moderada", "Amplia"]
        )

        energia_disponible = st.selectbox(
            "Disponibilidad de energía",
            ["Baja", "Media", "Alta"]
        )

        nivel_operacion = st.selectbox(
            "Nivel operativo esperado",
            ["Básico", "Intermedio", "Avanzado"]
        )

        requiere_remocion_alta = st.checkbox(
            "¿Se requiere alta calidad de efluente?",
            value=True
        )

    if st.button("Recomendar tren de tratamiento"):

        resultado_tren = seleccionar_tren_tratamiento(
            tipo_agua=tipo_agua,
            caudal_lps=caudal_lps,
            dbo=dbo,
            sst=sst,
            grasas=grasas,
            temperatura=temperatura,
            area_disponible=area_disponible,
            energia_disponible=energia_disponible,
            nivel_operacion=nivel_operacion,
            requiere_remocion_alta=requiere_remocion_alta
        )

        # Guardar en session_state
        st.session_state["tren_recomendado"] = resultado_tren["tren_recomendado"]
        st.session_state["justificacion_tren"] = resultado_tren["justificacion"]
        st.session_state["alternativas_tren"] = resultado_tren["alternativas"]

        st.session_state["tipo_agua"] = tipo_agua
        st.session_state["caudal_lps"] = caudal_lps
        st.session_state["dbo_afluente"] = dbo

        st.subheader("Tren recomendado")
        st.write(" → ".join(resultado_tren["tren_recomendado"]))

        st.subheader("Justificación técnica")
        for item in resultado_tren["justificacion"]:
            st.write(f"- {item}")

        st.subheader("Alternativas sugeridas")
        if resultado_tren["alternativas"]:
            for alt in resultado_tren["alternativas"]:
                st.write(f"- {alt}")
        else:
            st.write("No se generaron alternativas para este caso.")

        st.subheader("Diagrama de proceso tipo PFD")
        pfd = generar_pfd_tren(
            resultado_tren["tren_recomendado"],
            titulo="PFD del Tren de Tratamiento"
        )
        st.graphviz_chart(pfd)

# -------------------------------------------------
# PFD GENERAL DEL TREN
# -------------------------------------------------

elif menu == "PFD del Tren de Tratamiento":

    st.header("Diagrama de Proceso del Tren de Tratamiento")

    if st.session_state["tren_recomendado"]:

        st.subheader("Resumen del caso analizado")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Tipo de agua", st.session_state["tipo_agua"])

        with col2:
            st.metric("Caudal de diseño", f"{st.session_state['caudal_lps']} L/s")

        with col3:
            st.metric("DBO afluente", f"{st.session_state['dbo_afluente']} mg/L")

        st.subheader("Tren actualmente seleccionado")
        st.write(" → ".join(st.session_state["tren_recomendado"]))

        if st.session_state["justificacion_tren"]:
            st.subheader("Justificación técnica")
            for item in st.session_state["justificacion_tren"]:
                st.write(f"- {item}")

        if st.session_state["alternativas_tren"]:
            st.subheader("Alternativas sugeridas")
            for alt in st.session_state["alternativas_tren"]:
                st.write(f"- {alt}")

        st.subheader("PFD del tren real recomendado")
        pfd = generar_pfd_tren(
            st.session_state["tren_recomendado"],
            titulo="PFD del Tren de Tratamiento"
        )
        st.graphviz_chart(pfd)

    else:
        st.warning("Aún no has generado un tren de tratamiento desde el motor inteligente.")
        st.info("Primero ve a 'Recomendación de Tren de Tratamiento', ejecuta el análisis y luego vuelve a esta pantalla.")

# -------------------------------------------------
# PFD LODOS ACTIVADOS
# -------------------------------------------------

elif menu == "PFD - Lodos Activados":

    st.header("Diagrama de Proceso - Lodos Activados")

    if st.session_state["resultados_lodos"]:

        st.subheader("Resumen del cálculo biológico")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Q entrada", f"{st.session_state['q_lodos_lps']:.2f} L/s")

        with col2:
            st.metric("Q recirculación", f"{st.session_state['q_recirculacion_m3d']:.2f} m³/d")

        with col3:
            st.metric("Q purga", f"{st.session_state['q_purga_m3d']:.2f} m³/d")

        with col4:
            st.metric("Q aire", f"{st.session_state['q_aire_nm3h']:.2f} Nm³/h")

        pfd_lodos = generar_pfd_lodos_activados(
            q_lps=st.session_state["q_lodos_lps"],
            q_recirculacion_m3d=st.session_state["q_recirculacion_m3d"],
            q_purga_m3d=st.session_state["q_purga_m3d"],
            q_aire_nm3h=st.session_state["q_aire_nm3h"]
        )

        st.subheader("PFD dinámico del proceso de lodos activados")
        st.graphviz_chart(pfd_lodos)

        st.subheader("Variables principales del proceso")
        tabla_resumen = {
            "Volumen reactor (m³)": st.session_state["resultados_lodos"]["Volumen del reactor (m3)"],
            "TRH (h)": st.session_state["resultados_lodos"]["TRH recalculado (h)"],
            "SSVLM (mg/L)": st.session_state["resultados_lodos"]["SSVLM (mg/L)"],
            "Requerimiento O₂ (kg/d)": st.session_state["resultados_lodos"]["Requerimiento de oxígeno (kg O2/d)"],
            "Número de difusores": st.session_state["resultados_lodos"]["Número de difusores"]
        }
        st.table(tabla_resumen)

    else:
        st.warning("Aún no has calculado el módulo de Lodos Activados.")
        st.info("Primero ve a '06 - Reactores Aeróbicos - Lodos Activados', ejecuta el cálculo y luego vuelve a esta pantalla.")

# -------------------------------------------------
# LODOS ACTIVADOS - VERSIÓN 3
# -------------------------------------------------

elif menu == "06 - Reactores Aeróbicos - Lodos Activados":

    st.header("Diseño de Lodos Activados - Versión 3 alineada con Excel")

    st.subheader("Datos de entrada")

    col1, col2, col3 = st.columns(3)

    with col1:
        poblacion = st.number_input("Población servida", value=450.0)
        q_entrada = st.number_input("Caudal de entrada QMM (L/s)", value=35.0)
        numero_reactores = st.number_input("Número de reactores biológicos", value=1.0)
        altitud = st.number_input("Altitud (m s.n.m.)", value=150.0)
        temperatura = st.number_input("Temperatura de diseño (°C)", value=26.0)
        dbo_afluente = st.number_input("DBO afluente (mg/L)", value=260.0)
        st_afluente = st.number_input("Sólidos totales afluente (mg/L)", value=260.0)
        ntk_afluente = st.number_input("NTK afluente (mg/L)", value=75.0)

    with col2:
        fraccion_volatil = st.number_input("Fracción volátil ST", value=0.80)
        fraccion_biodegradable_efluente = st.number_input("Fracción biodegradable en efluente", value=0.65)
        factor_dbol_dbo5 = st.number_input("Factor DBOL a DBO5", value=0.68)
        st_lodo_sedimentado = st.number_input("ST del lodo sedimentado (mg/L)", value=10000.0)
        dbo_efluente = st.number_input("DBO efluente esperada (mg/L)", value=15.0)
        sst_efluente = st.number_input("SST efluente esperado (mg/L)", value=15.0)
        Ks = st.number_input("Ks", value=60.0)
        k = st.number_input("k", value=5.0)
        Y = st.number_input("Y", value=0.60)
        kd = st.number_input("kd", value=0.04)

    with col3:
        trh_supuesto = st.number_input("TRH supuesto (d)", value=18/24)
        fm_ref = st.number_input("Relación F/M de referencia", value=0.10)
        recirculacion_ref = st.number_input("Porcentaje de recirculación", value=0.75)
        edad_lodo = st.number_input("Edad del lodo (d)", value=22.0)
        fb_prima = st.number_input("fb prima", value=0.80)
        altura_util = st.number_input("Altura útil tanque (m)", value=2.2)
        borde_libre = st.number_input("Borde libre (m)", value=0.2)
        relacion_bl = st.number_input("Relación ancho/largo", value=2.0)
        od_reactor = st.number_input("OD en reactor (mg/L)", value=1.5)
        factor_caracteristicas = st.number_input("Factor corrección características agua", value=0.95)
        factor_contaminantes = st.number_input("Factor corrección contaminantes", value=0.80)
        coef_temp = st.number_input("Coeficiente de temperatura", value=1.02)
        efic_difusor_m = st.number_input("Eficiencia difusor por m (%)", value=6.5)
        perdida_carga = st.number_input("Pérdida de carga (m)", value=2.0)
        cant_equipos = st.number_input("Cantidad de equipos de aireación", value=2.0)
        blower_q_max = st.number_input("Caudal máximo soplador (cfm)", value=70.0)
        blower_p_max = st.number_input("Presión máxima soplador (inH2O)", value=140.0)
        blower_hp = st.number_input("Potencia soplador (HP)", value=2.0)
        difusor_q = st.number_input("Caudal por difusor (Nm3/h)", value=2.5)

    if st.button("Calcular Versión 3"):

        resultados = calcular_lodos_activados_excel_v3(
            poblacion_servida=poblacion,
            q_entrada_lps=q_entrada,
            numero_reactores=numero_reactores,
            altitud_m=altitud,
            temperatura_c=temperatura,
            dbo_afluente_mg_l=dbo_afluente,
            st_afluente_mg_l=st_afluente,
            ntk_afluente_mg_l=ntk_afluente,
            fraccion_volatil_st=fraccion_volatil,
            fraccion_biodegradable_efluente=fraccion_biodegradable_efluente,
            factor_dbol_dbo5=factor_dbol_dbo5,
            st_lodo_sedimentado_mg_l=st_lodo_sedimentado,
            dbo_efluente_esperada_mg_l=dbo_efluente,
            sst_efluente_esperado_mg_l=sst_efluente,
            Ks=Ks,
            k=k,
            Y=Y,
            kd=kd,
            trh_supuesto_d=trh_supuesto,
            relacion_fm_referencia=fm_ref,
            porcentaje_recirculacion_referencia=recirculacion_ref,
            edad_lodo_d=edad_lodo,
            fb_prima=fb_prima,
            altura_util_tanque_m=altura_util,
            borde_libre_m=borde_libre,
            relacion_ancho_largo=relacion_bl,
            od_reactor_mg_l=od_reactor,
            factor_correcion_caracteristicas_agua=factor_caracteristicas,
            factor_correcion_contaminantes=factor_contaminantes,
            coef_temp=coef_temp,
            eficiencia_transferencia_difusor_por_m=efic_difusor_m,
            perdida_carga_m=perdida_carga,
            cantidad_equipos_aireacion=cant_equipos,
            blower_caudal_max_cfm=blower_q_max,
            blower_presion_max_inH2O=blower_p_max,
            blower_potencia_hp=blower_hp,
            difusor_caudal_nm3_h=difusor_q
        )

        # Guardar resultados del módulo en session_state
        st.session_state["resultados_lodos"] = resultados
        st.session_state["q_lodos_lps"] = q_entrada
        st.session_state["q_recirculacion_m3d"] = resultados["Caudal de recirculación (m3/d)"]
        st.session_state["q_purga_m3d"] = resultados["Caudal de purga de lodos (m3/d)"]
        st.session_state["q_aire_nm3h"] = resultados["Caudal de aire corregido (Nm3/h)"]

        st.header("Resultados del Diseño")

        st.subheader("1️⃣ Estimación de DBO en el efluente")
        tabla1 = {
            "DBO soluble que escapa (mg/L)": resultados["DBO soluble que escapa del tratamiento (mg/L)"],
            "Eficiencia tratamiento biológico": resultados["Eficiencia tratamiento biológico"],
            "Eficiencia total de planta": resultados["Eficiencia conjunta de planta"]
        }
        st.table(tabla1)

        st.subheader("2️⃣ Diseño del Reactor Biológico")
        tabla2 = {
            "Volumen del reactor (m³)": resultados["Volumen del reactor (m3)"],
            "TRH (h)": resultados["TRH recalculado (h)"],
            "SSVLM (mg/L)": resultados["SSVLM (mg/L)"],
            "Relación F/M": resultados["Relación F/M calculada"],
            "Carga volumétrica (kg DBO/m³·d)": resultados["Carga orgánica volumétrica (kg DBO/m3.d)"],
            "Área del reactor (m²)": resultados["Área tanque (m2)"],
            "Ancho tanque (m)": resultados["Ancho tanque rectangular (m)"],
            "Largo tanque (m)": resultados["Longitud tanque rectangular (m)"]
        }
        st.table(tabla2)

        st.subheader("3️⃣ Producción de Lodos")
        tabla3 = {
            "Rendimiento observado": resultados["Rendimiento observado"],
            "Masa de lodo purgado (kg/d)": resultados["Masa lodo volatil purgado (kg/d)"],
            "Caudal de purga (m³/d)": resultados["Caudal de purga de lodos (m3/d)"],
            "Caudal de recirculación (m³/d)": resultados["Caudal de recirculación (m3/d)"],
            "Relación de recirculación": resultados["Relación de recirculación"]
        }
        st.table(tabla3)

        st.subheader("4️⃣ Requerimiento de Oxígeno")
        tabla4 = {
            "Demanda por síntesis (kg O₂/d)": resultados["Demanda por síntesis (kg O2/d)"],
            "Demanda endógena (kg O₂/d)": resultados["Demanda endógena (kg O2/d)"],
            "Demanda nitrificación (kg O₂/d)": resultados["Demanda por nitrificación (kg O2/d)"],
            "Requerimiento total O₂ (kg/d)": resultados["Requerimiento de oxígeno (kg O2/d)"],
            "Tasa transferencia estándar (kg O₂/h)": resultados["Tasa transferencia estándar O2 (kg O2/h)"]
        }
        st.table(tabla4)

        st.subheader("5️⃣ Sistema de Aireación")
        tabla5 = {
            "Caudal de aire normal (Nm³/h)": resultados["Caudal de aire normal (Nm3/h)"],
            "Caudal de aire corregido (Nm³/h)": resultados["Caudal de aire corregido (Nm3/h)"],
            "Caudal volumétrico (m³/h)": resultados["Caudal de aire volumétrico (m3/h)"],
            "Potencia requerida (kW)": resultados["Potencia requerida (kW)"],
            "Potencia requerida (HP)": resultados["Potencia requerida (HP)"],
            "Número de difusores": resultados["Número de difusores"]
        }
        st.table(tabla5)

        st.header("Verificación de criterios de diseño")

        advertencias = []

        if resultados["Relación F/M calculada"] < 0.05:
            advertencias.append("Relación F/M muy baja")

        if resultados["Relación F/M calculada"] > 0.25:
            advertencias.append("Relación F/M muy alta")

        if resultados["TRH recalculado (h)"] < 4:
            advertencias.append("TRH demasiado bajo")

        if resultados["TRH recalculado (h)"] > 24:
            advertencias.append("TRH excesivo")

        if resultados["SSVLM (mg/L)"] > 5000:
            advertencias.append("Concentración de sólidos muy alta")

        if advertencias:
            for a in advertencias:
                st.warning(a)
        else:
            st.success("Todos los parámetros dentro de rangos típicos de diseño")

        st.subheader("PFD del módulo de Lodos Activados")
        pfd_lodos = generar_pfd_lodos_activados(
            q_lps=q_entrada,
            q_recirculacion_m3d=resultados["Caudal de recirculación (m3/d)"],
            q_purga_m3d=resultados["Caudal de purga de lodos (m3/d)"],
            q_aire_nm3h=resultados["Caudal de aire corregido (Nm3/h)"]
        )
        st.graphviz_chart(pfd_lodos)

        if st.button("Generar memoria de cálculo"):
            datos_proyecto = {
                "Población": poblacion,
                "Caudal": q_entrada,
                "DBO afluente": dbo_afluente
            }

            generar_memoria(datos_proyecto, resultados, ruta_pfd_tren=None, ruta_pfd_lodos=None)
            st.success("Memoria de cálculo generada")

# -------------------------------------------------
# RESUMEN DEL PROYECTO
# -------------------------------------------------

elif menu == "Resumen del Proyecto":

    import os

    st.header("Resumen del Proyecto")

    # -------------------------------------------------
    # VALIDACIONES PREVIAS
    # -------------------------------------------------

    if not st.session_state["datos_proyecto"]:
        st.warning("Aún no has configurado los datos generales del proyecto.")
        st.info("Primero ve a 'Nuevo Proyecto' y registra la información básica.")
    else:
        st.subheader("1️⃣ Datos generales del proyecto")
        st.table(st.session_state["datos_proyecto"])

        # -------------------------------------------------
        # TREN RECOMENDADO
        # -------------------------------------------------

        st.subheader("2️⃣ Tren de tratamiento recomendado")

        if st.session_state["tren_recomendado"]:
            st.write(" → ".join(st.session_state["tren_recomendado"]))

            if st.session_state["justificacion_tren"]:
                st.markdown("**Justificación técnica**")
                for item in st.session_state["justificacion_tren"]:
                    st.write(f"- {item}")

            if st.session_state["alternativas_tren"]:
                st.markdown("**Alternativas sugeridas**")
                for alt in st.session_state["alternativas_tren"]:
                    st.write(f"- {alt}")

            pfd_tren = generar_pfd_tren(
                st.session_state["tren_recomendado"],
                titulo="PFD del Tren de Tratamiento"
            )
            st.graphviz_chart(pfd_tren)

        else:
            st.info("Todavía no has generado el tren recomendado desde el motor inteligente.")

        # -------------------------------------------------
        # RESULTADOS DE LODOS ACTIVADOS
        # -------------------------------------------------

        st.subheader("3️⃣ Resumen del módulo de Lodos Activados")

        if st.session_state["resultados_lodos"]:

            resultados = st.session_state["resultados_lodos"]

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Volumen reactor", f"{resultados['Volumen del reactor (m3)']:.2f} m³")
                st.metric("TRH", f"{resultados['TRH recalculado (h)']:.2f} h")

            with col2:
                st.metric("SSVLM", f"{resultados['SSVLM (mg/L)']:.2f} mg/L")
                st.metric("Relación F/M", f"{resultados['Relación F/M calculada']:.4f}")

            with col3:
                st.metric("Oxígeno requerido", f"{resultados['Requerimiento de oxígeno (kg O2/d)']:.2f} kg/d")
                st.metric("Difusores", f"{resultados['Número de difusores']}")

            st.markdown("**PFD del proceso de lodos activados**")

            pfd_lodos = generar_pfd_lodos_activados(
                q_lps=st.session_state["q_lodos_lps"],
                q_recirculacion_m3d=st.session_state["q_recirculacion_m3d"],
                q_purga_m3d=st.session_state["q_purga_m3d"],
                q_aire_nm3h=st.session_state["q_aire_nm3h"]
            )
            st.graphviz_chart(pfd_lodos)

        else:
            st.info("Todavía no has ejecutado el cálculo del módulo de Lodos Activados.")

        # -------------------------------------------------
        # EXPORTACIÓN
        # -------------------------------------------------

        st.subheader("4️⃣ Exportación del proyecto")

        if st.button("Generar memoria completa del proyecto"):

            os.makedirs("outputs", exist_ok=True)

            ruta_pfd_tren = None
            ruta_pfd_lodos = None

            if st.session_state["tren_recomendado"]:
                ruta_pfd_tren = exportar_pfd_tren_png(
                    st.session_state["tren_recomendado"],
                    ruta_sin_extension="outputs/pfd_tren_resumen",
                    titulo="PFD del Tren de Tratamiento"
                )

            if st.session_state["resultados_lodos"]:
                ruta_pfd_lodos = exportar_pfd_lodos_png(
                    q_lps=st.session_state["q_lodos_lps"],
                    q_recirculacion_m3d=st.session_state["q_recirculacion_m3d"],
                    q_purga_m3d=st.session_state["q_purga_m3d"],
                    q_aire_nm3h=st.session_state["q_aire_nm3h"],
                    ruta_sin_extension="outputs/pfd_lodos_resumen"
                )

            resultados_exportar = st.session_state["resultados_lodos"] if st.session_state["resultados_lodos"] else {}

            ruta_docx = generar_memoria(
                datos_proyecto=st.session_state["datos_proyecto"],
                resultados=resultados_exportar,
                ruta_pfd_tren=ruta_pfd_tren,
                ruta_pfd_lodos=ruta_pfd_lodos
            )

            st.success(f"Memoria completa generada: {ruta_docx}")