from graphviz import Digraph


def generar_tren(tren):

    dot = Digraph()

    for i in range(len(tren) - 1):

        dot.node(tren[i])
        dot.node(tren[i+1])

        dot.edge(tren[i], tren[i+1])

    return dot