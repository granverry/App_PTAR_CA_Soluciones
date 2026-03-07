import streamlit as st
from calculos.trampa_grasas import calcular_trampa
from calculos.sedimentador import calcular_sedimentador
from calculos.reactor_mbbr import calcular_reactor
from utils.generador_docx import generar_docx

st.set_page_config(page_title="Diseño PTAR", page_icon="💧")

st.title("💧 Aplicativo de Diseño de Planta de Tratamiento de Aguas Residuales")

# Selección de unidad
unidad = st.selectbox(
    "Selecciona la unidad de tratamiento a diseñar:",
    ["Trampa de Grasas", "Sedimentador Primario", "Reactor MBBR"]
)

if unidad == "Trampa de Grasas":
    Q = st.number_input("Caudal (L/s):", min_value=0.1, step=0.1)
    T = st.number_input("Temperatura (°C):", min_value=0.0, step=0.5)
    if st.button("Calcular Trampa de Grasas"):
        resultados = calcular_trampa(Q, T)
        st.write("### Resultados", resultados)
        generar_docx(resultados, "Trampa de Grasas")
        st.success("Documento generado: resumen_trampa.docx")

elif unidad == "Sedimentador Primario":
    Q = st.number_input("Caudal (L/s):", min_value=0.1)
    v = st.number_input("Velocidad de sedimentación (m/h):", min_value=0.1)
    if st.button("Calcular Sedimentador"):
        resultados = calcular_sedimentador(Q, v)
        st.write("### Resultados", resultados)
        generar_docx(resultados, "Sedimentador Primario")

elif unidad == "Reactor MBBR":
    Q = st.number_input("Caudal (L/s):", min_value=0.1)
    TRH = st.number_input("Tiempo de Retención (h):", min_value=0.1)
    if st.button("Calcular Reactor MBBR"):
        resultados = calcular_reactor(Q, TRH)
        st.write("### Resultados", resultados)
        generar_docx(resultados, "Reactor MBBR")
