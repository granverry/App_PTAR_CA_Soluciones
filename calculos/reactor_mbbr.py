def calcular_reactor(Q_lps, TRH_h):
    Q_m3h = Q_lps / 1000 * 3600
    volumen = Q_m3h * TRH_h
    return {
        "Caudal (m³/h)": round(Q_m3h, 2),
        "TRH (h)": TRH_h,
        "Volumen (m³)": round(volumen, 2)
    }
