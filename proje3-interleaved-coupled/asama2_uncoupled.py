"""
Aşama 2: Uncoupled (bağımsız endüktanslı) 2 fazlı interleaved buck

Deney A: D = 0.417'de 180° kaydırma (interleaved) ile 0° kaydırma (aynı anda) karşılaştırması
Deney B: Farklı D değerlerinde simülasyon yapıp ölçülen noktaları
         Aşama 1'deki TI formül eğrisinin üstüne koymak

Parametreler Proje 2 ile aynı: Vout = 5 V, L = 100 µH (faz başına), C = 220 µF,
R = 5 Ω (1 A), f = 100 kHz
"""

import numpy as np
import matplotlib.pyplot as plt

from simulasyon import dengeli_simule_et, olc
from asama1_ti_formulleri import cin_rms_norm, cout_ripple_norm


# ---------------------------------------------------------------------------
# Deney A: 180° ve 0°
# ---------------------------------------------------------------------------

def deney_a():
    print("=== Deney A: Vin = 12 V, D = 0.417 ===")

    # Elle hesapladığımız beklenen değerler
    Vin, Vo, L, f = 12.0, 5.0, 100e-6, 100e3
    D = Vo / Vin
    faz_ripple_beklenen = (Vin - Vo) / L * D / f             # hız x süre
    toplam_ripple_beklenen = (Vin - 2 * Vo) / L * D / f      # D < 1/2 iken
    print(f"Beklenen: faz ripple = {faz_ripple_beklenen:.3f} A, "
          f"toplam ripple (180°) = {toplam_ripple_beklenen:.3f} A, "
          f"toplam ripple (0°) = {2 * faz_ripple_beklenen:.3f} A")

    sonuclar = {}
    for aci in [180, 0]:
        s = dengeli_simule_et(faz_kaydirma_derece=aci)
        o = olc(s)
        sonuclar[aci] = s
        print(f"\nKaydırma {aci}°:")
        print(f"  faz ortalamaları   : {o['faz1_ort']:.3f} A, {o['faz2_ort']:.3f} A")
        print(f"  faz ripple         : {o['faz1_ripple']:.3f} A")
        print(f"  toplam ripple      : {o['toplam_ripple']:.3f} A")
        print(f"  Vout ort / ripple  : {o['vout_ort']:.3f} V / {o['vout_ripple']*1e3:.2f} mV")
        print(f"  C_IN RMS / Io      : {o['cin_rms'] / o['toplam_ort']:.3f}")

    # Son 2 periyodun dalga şekilleri
    fig, axlar = plt.subplots(2, 1, figsize=(10, 6.5), sharex=True)
    for ax, aci in zip(axlar, [180, 0]):
        s = sonuclar[aci]
        n = 2 * s["adim_sayisi"]
        t = (s["t"][-n:] - s["t"][-n]) * 1e6          # µs, 0'dan başlat
        i1, i2 = s["i1"][-n:], s["i2"][-n:]
        ax.plot(t, i1, color="tab:green", label="Faz 1 (i_L1)")
        ax.plot(t, i2, color="tab:purple", label="Faz 2 (i_L2)")
        ax.plot(t, i1 + i2, color="tab:orange", lw=2, label="Toplam (C_OUT'a giden)")
        ax.set_title(f"Faz kaydırma {aci}°   |   toplam ripple = "
                     f"{np.ptp(i1 + i2):.3f} A")
        ax.set_ylabel("Akım (A)")
        ax.grid(alpha=0.3)
        ax.legend(loc="center right", fontsize=9)
    axlar[1].set_xlabel("Zaman (µs)")
    fig.tight_layout()
    fig.savefig("sonuclar/asama2_dalga_sekilleri.png", dpi=150)
    print("\nGrafik kaydedildi: sonuclar/asama2_dalga_sekilleri.png")


# ---------------------------------------------------------------------------
# Deney B: D taraması, simülasyon noktaları + TI formül eğrisi
# ---------------------------------------------------------------------------

def deney_b():
    print("\n=== Deney B: D taraması (Vout = 5 V sabit, Vin = 5 / D) ===")
    D_listesi = [0.15, 0.20, 0.25, 0.30, 0.35, 5 / 12, 0.45, 0.50,
                 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85]

    olcum = {"D": [], "cout_180": [], "cin_180": [], "cin_0": []}
    for D in D_listesi:
        Vin = 5.0 / D
        o180 = olc(dengeli_simule_et(Vin=Vin, faz_kaydirma_derece=180, n_periyot=150))
        o0 = olc(dengeli_simule_et(Vin=Vin, faz_kaydirma_derece=0, n_periyot=150))
        olcum["D"].append(D)
        olcum["cout_180"].append(o180["toplam_ripple"] / o180["faz1_ripple"])
        # Normalize ederken ölçülen yük akımını kullanıyoruz (1 A'e çok yakın)
        olcum["cin_180"].append(o180["cin_rms"] / o180["toplam_ort"])
        olcum["cin_0"].append(o0["cin_rms"] / o0["toplam_ort"])
        print(f"D={D:.3f}  C_OUT oranı: sim {olcum['cout_180'][-1]:.3f} / "
              f"formül {cout_ripple_norm(D, 2):.3f}   |   C_IN/Io: sim "
              f"{olcum['cin_180'][-1]:.3f} / formül {cin_rms_norm(D, 2):.3f}")

    D = np.linspace(0.001, 0.999, 2000)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

    ax1.plot(D, cin_rms_norm(D, 1), color="tab:blue", label="Formül n=1")
    ax1.plot(D, cin_rms_norm(D, 2), color="tab:green", label="Formül n=2")
    ax1.plot(olcum["D"], olcum["cin_0"], "s", color="tab:blue", mfc="white",
             label="Simülasyon, 0° kaydırma")
    ax1.plot(olcum["D"], olcum["cin_180"], "o", color="tab:green", mfc="white",
             label="Simülasyon, 180° kaydırma")
    ax1.set_title("C_IN RMS akımı: formül ve simülasyon")
    ax1.set_xlabel("Duty cycle (D)")
    ax1.set_ylabel("I_CIN,RMS / I_OUT")
    ax1.grid(alpha=0.3)
    ax1.legend(fontsize=8)

    ax2.plot(D, cout_ripple_norm(D, 2), color="tab:green", label="Formül n=2")
    ax2.plot(olcum["D"], olcum["cout_180"], "o", color="tab:green", mfc="white",
             label="Simülasyon, 180° kaydırma")
    ax2.set_title("C_OUT ripple oranı: formül ve simülasyon")
    ax2.set_xlabel("Duty cycle (D)")
    ax2.set_ylabel("Toplam ripple / faz ripple'ı")
    ax2.set_ylim(0, 1.02)
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig("sonuclar/asama2_formul_vs_simulasyon.png", dpi=150)
    print("\nGrafik kaydedildi: sonuclar/asama2_formul_vs_simulasyon.png")


if __name__ == "__main__":
    deney_a()
    deney_b()
