def calcular_sedimentador(Q_lps, v_sed):
    Q_m3s = Q_lps / 1000
    Q_m3h = Q_m3s * 3600
    area = Q_m3h / v_sed
    return {
        "Caudal (m³/h)": round(Q_m3h, 2),
        "Velocidad de sedimentación (m/h)": v_sed,
        "Área requerida (m²)": round(area, 2)
    }
