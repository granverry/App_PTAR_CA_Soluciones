import pandas as pd

def leer_datos_excel(ruta_archivo):

    hoja = pd.read_excel(ruta_archivo, sheet_name="Diseño - Lodos Activados")

    datos = {}

    for i in range(len(hoja)):
        parametro = hoja.iloc[i,0]
        valor = hoja.iloc[i,2]

        if pd.notna(parametro):
            datos[parametro] = valor

    return datos