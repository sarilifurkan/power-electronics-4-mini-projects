"""
Buck Converter Analitik Hesap Araci
Kaynak: TI SLVA477 - "Basic Calculation of a Buck Converter's Power Stage"

Bu script, Proje 2'de (Simulink) kullanilan devre degerlerini
(L=100uH, C=220uF, D≈0.417) analitik formullerle dogrulamak icin yazildi.
"""

def buck_hesapla(Vin, Vout, f_sw, Iout_max, delta_IL_percent=0.3, delta_Vout_percent=0.01):
    """
    Vin              : Giris gerilimi (V)
    Vout             : Cikis gerilimi (V)
    f_sw             : Anahtarlama frekansi (Hz)
    Iout_max         : Maksimum cikis akimi (A)
    delta_IL_percent : Endüktans ripple akiminin Iout_max'a orani (SLVA477 tipik: 0.2-0.4)
    delta_Vout_percent: Cikis gerilimi ripple'inin Vout'a orani (tipik: %1)
    """

    # 1) Duty Cycle (volt-saniye dengesinden: Vout = D * Vin, ideal/kayipsiz kabul)
    D = Vout / Vin

    # 2) Endüktans ripple akimi hedefi
    delta_IL = delta_IL_percent * Iout_max

    # 3) Minimum endüktans (SLVA477 Eq.)
    #    L = (Vin - Vout) * D / (f_sw * delta_IL)
    L_min = (Vin - Vout) * D / (f_sw * delta_IL)

    # 4) Kritik endüktans (CCM/DCM sinir kosulu, delta_IL = 2*Iout oldugu ozel durum)
    #    Load R = Vout / Iout_max uzerinden kritik direnc/akim hesaplanabilir
    R_load = Vout / Iout_max
    L_critical = (1 - D) * R_load / (2 * f_sw)

    # 5) Cikis kondansatoru (SLVA477 Eq.)
    #    C = delta_IL / (8 * f_sw * delta_Vout)
    delta_Vout = delta_Vout_percent * Vout
    C_min = delta_IL / (8 * f_sw * delta_Vout)

    return {
        "D": D,
        "delta_IL_A": delta_IL,
        "L_min_H": L_min,
        "L_critical_H": L_critical,
        "R_load_ohm": R_load,
        "C_min_F": C_min,
    }


def yazdir(sonuc):
    print("----- Buck Converter Analitik Sonuclar -----")
    print(f"Duty Cycle (D)              : {sonuc['D']:.4f}")
    print(f"Endüktans ripple akimi (ΔIL) : {sonuc['delta_IL_A']*1000:.2f} mA")
    print(f"Minimum Endüktans (L_min)   : {sonuc['L_min_H']*1e6:.2f} uH")
    print(f"Kritik Endüktans (L_crit)   : {sonuc['L_critical_H']*1e6:.2f} uH")
    print(f"Yuk direnci (R_load)         : {sonuc['R_load_ohm']:.2f} ohm")
    print(f"Minimum Cikis Kapasitesi (C) : {sonuc['C_min_F']*1e6:.2f} uF")
    print("---------------------------------------------")


if __name__ == "__main__":
    # Proje 2 (Simulink) ile ayni parametreler:
    # Vin=12V, Vout=5V, f=100kHz, R=5 ohm  ->  Iout_max = Vout/R = 1A
    Vin = 12
    Vout = 5
    f_sw = 100e3
    R = 5
    Iout_max = Vout / R  # 1 A

    print(f"Girdi parametreleri: Vin={Vin}V, Vout={Vout}V, f_sw={f_sw/1e3:.0f}kHz, R={R} ohm, Iout_max={Iout_max}A\n")

    sonuc = buck_hesapla(Vin, Vout, f_sw, Iout_max)
    yazdir(sonuc)

    print("\nProje 2 (Simulink) ile karsilastirma:")
    print(f"  Simulink'te kullanilan L = 100 uH   ->  Buradan hesaplanan L_min = {sonuc['L_min_H']*1e6:.2f} uH")
    print(f"  Simulink'te kullanilan C = 220 uF   ->  Buradan hesaplanan C_min = {sonuc['C_min_F']*1e6:.2f} uF")
    print(f"  Simulink'te kullanilan D ≈ 0.417    ->  Buradan hesaplanan D      = {sonuc['D']:.4f}")
