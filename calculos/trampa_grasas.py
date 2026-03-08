def calcular_trampa(Q_lps, T):
    Q_m3d = Q_lps * 86.4
    volumen = Q_lps * 60 * 20 / 1000
    area = volumen / 1.0
    return {
        "Caudal (m³/día)": round(Q_m3d, 2),
        "Volumen (m³)": round(volumen, 2),
        "Área (m²)": round(area, 2),
        "Temperatura (°C)": T
    }
