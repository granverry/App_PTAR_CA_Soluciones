from graphviz import Digraph


def generar_pfd_lodos_activados(q_lps, q_recirculacion_m3d, q_purga_m3d, q_aire_nm3h):

    dot = Digraph(comment="PFD Lodos Activados")

    dot.attr(rankdir="LR")
    dot.attr(label="PFD - Lodos Activados", labelloc="t", fontsize="20")

    dot.node("A", "Afluente", shape="box", style="rounded,filled", fillcolor="lightyellow")
    dot.node("B", "Reactor Biológico", shape="box", style="rounded,filled", fillcolor="honeydew")
    dot.node("C", "Sedimentador Secundario", shape="box", style="rounded,filled", fillcolor="lightcyan")
    dot.node("D", "Desinfección", shape="box", style="rounded,filled", fillcolor="lavender")
    dot.node("E", "Efluente", shape="box")
    dot.node("F", "Lechos de Secado", shape="box", style="rounded,filled", fillcolor="linen")

    dot.edge("A", "B", label=f"Q = {q_lps:.2f} L/s")
    dot.edge("B", "C", label=f"Qa = {q_aire_nm3h:.2f} Nm³/h")
    dot.edge("C", "D")
    dot.edge("D", "E")

    dot.edge("C", "B", label=f"Qr = {q_recirculacion_m3d:.2f} m³/d")
    dot.edge("C", "F", label=f"Qp = {q_purga_m3d:.2f} m³/d")

    return dot


def exportar_pfd_lodos_png(q_lps, q_recirculacion_m3d, q_purga_m3d, q_aire_nm3h, ruta_sin_extension):

    dot = generar_pfd_lodos_activados(
        q_lps,
        q_recirculacion_m3d,
        q_purga_m3d,
        q_aire_nm3h
    )

    ruta = dot.render(
        filename=ruta_sin_extension,
        format="png",
        cleanup=True
    )

    return ruta