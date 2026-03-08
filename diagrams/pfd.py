from graphviz import Digraph

def _estilo_unidad(nombre):
    nombre_l = nombre.lower()

    if "rejilla" in nombre_l or "desarenador" in nombre_l:
        return {"fillcolor": "lightyellow", "color": "goldenrod4"}

    if "sedimentador" in nombre_l:
        return {"fillcolor": "lightcyan", "color": "steelblue4"}

    if "uasb" in nombre_l:
        return {"fillcolor": "mistyrose", "color": "firebrick4"}

    if "lodos activados" in nombre_l:
        return {"fillcolor": "honeydew", "color": "darkgreen"}

    if "desinfección" in nombre_l:
        return {"fillcolor": "lavender", "color": "purple4"}

    if "lodo" in nombre_l or "lechos" in nombre_l:
        return {"fillcolor": "linen", "color": "saddlebrown"}

    return {"fillcolor": "lightgray", "color": "gray30"}


def generar_pfd_tren(tren, titulo="PFD del Tren de Tratamiento"):

    dot = Digraph(comment=titulo)

    dot.attr(rankdir="LR")
    dot.attr(label=titulo, labelloc="t", fontsize="20")

    for i, unidad in enumerate(tren):

        estilo = _estilo_unidad(unidad)

        dot.node(
            f"U{i}",
            unidad,
            shape="box",
            style="rounded,filled",
            fillcolor=estilo["fillcolor"],
            color=estilo["color"]
        )

    for i in range(len(tren)-1):
        dot.edge(f"U{i}", f"U{i+1}")

    return dot


def exportar_pfd_tren_png(tren, ruta_sin_extension, titulo="PFD del Tren de Tratamiento"):

    dot = generar_pfd_tren(tren, titulo)

    ruta = dot.render(
        filename=ruta_sin_extension,
        format="png",
        cleanup=True
    )

    return ruta