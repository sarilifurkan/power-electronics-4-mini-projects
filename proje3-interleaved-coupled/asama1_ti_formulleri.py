"""
Aşama 1: TI makalelerindeki grafikleri kendi kodumla yeniden üretmek

Kaynak: TI SLVA882B, "Multiphase Buck Design From Start to Finish (Part 1)"
  - Denklem 1: Giriş kondansatörü (C_IN) normalize RMS akımı   -> Şekil 3-2
  - Denklem 2: Çıkış kondansatörü (C_OUT) normalize ripple akımı -> Şekil 3-4
Aynı formüller SLYT449'da (Denklem 1-2) da geçiyor.

Değişkenler:
  D = Vout / Vin           (duty cycle)
  n = faz sayısı
  m = floor(n * D)         (aynı anda EN AZ kaç faz açık)
"""

import numpy as np
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------------
# 1) Formüller
# ---------------------------------------------------------------------------

def cin_rms_norm(D, n):
    """C_IN RMS akımı / çıkış akımı  (SLVA882B Denklem 1).

    İki parantez, D'nin alttaki ve üstteki "sıfır noktasına" (k/n) uzaklığı.
    D tam bir k/n noktasındaysa parantezlerden biri 0 olur -> sonuç 0.
    """
    m = np.floor(n * D)
    alt_uzaklik = D - m / n              # D, alttaki k/n noktasından ne kadar uzakta?
    ust_uzaklik = (1 + m) / n - D        # D, üstteki k/n noktasından ne kadar uzakta?
    return np.sqrt(alt_uzaklik * ust_uzaklik)


def cout_ripple_norm(D, n):
    """Toplam ripple / tek fazın ripple'ı  (SLVA882B Denklem 2).

    1 = hiç iptal yok, 0 = tam iptal.
    Paydadaki D*(1-D), tek bir fazın ripple'ının D'ye bağlı kısmı.
    """
    m = np.floor(n * D)
    alt_uzaklik = D - m / n
    ust_uzaklik = (1 + m) / n - D
    return n / (D * (1 - D)) * alt_uzaklik * ust_uzaklik


# ---------------------------------------------------------------------------
# 2) Makalelerin verdiği sayılarla doğrulama
# ---------------------------------------------------------------------------

def dogrulama():
    print("=== Aşama 1: Makale sayılarıyla doğrulama ===")

    # (a) Giriş RMS tepeleri 1/(2n) olmalı (tepe, iki sıfırın tam ortasında: D = 1/(2n))
    for n in [1, 2, 3, 4]:
        tepe = cin_rms_norm(1 / (2 * n), n)
        print(f"C_IN tepe, n={n}: {tepe:.4f}   (beklenen 1/(2n) = {1/(2*n):.4f})")

    # (b) SLYT449: D = %20, 2 faz -> ripple %25 azalır, yani oran 0.75
    print(f"C_OUT oranı, n=2, D=0.20: {cout_ripple_norm(0.20, 2):.4f}   (beklenen 0.75)")

    # (c) SLYT449: D = %25, faz ripple'ı 2.2 A -> kondansatör ~1.5 A görür
    print(f"C_OUT ripple, n=2, D=0.25: 2.2 A x {cout_ripple_norm(0.25, 2):.3f} "
          f"= {2.2 * cout_ripple_norm(0.25, 2):.2f} A   (beklenen ~1.5 A)")

    # (d) Kendi devrem: Vin = 12 V, Vout = 5 V
    D = 5 / 12
    print(f"\nKendi devrem, D = {D:.3f}")
    for n in [1, 2, 3, 4]:
        print(f"  n={n}:  C_IN RMS / Iout = {cin_rms_norm(D, n):.3f}   "
              f"C_OUT oranı = {cout_ripple_norm(D, n):.3f}")


# ---------------------------------------------------------------------------
# 3) Grafikler
# ---------------------------------------------------------------------------

def grafikler():
    # 0 ve 1'i dışarıda bırakıyoruz: Denklem 2'de D*(1-D) paydası orada sıfır olur
    D = np.linspace(0.001, 0.999, 2000)
    renkler = {1: "tab:blue", 2: "tab:green", 3: "tab:red", 4: "tab:cyan"}
    D_benim = 5 / 12

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

    # Şekil 3-2'nin karşılığı
    for n in [1, 2, 3, 4]:
        ax1.plot(D, cin_rms_norm(D, n), color=renkler[n], label=f"n={n}")
    ax1.axvline(D_benim, color="gray", ls="--", lw=1)
    ax1.text(D_benim + 0.01, 0.46, "benim D'm\n(0.417)", fontsize=9, color="gray")
    ax1.set_title("C_IN normalize RMS akımı (SLVA882B Şekil 3-2)")
    ax1.set_xlabel("Duty cycle (D)")
    ax1.set_ylabel("I_CIN,RMS / I_OUT")
    ax1.set_ylim(0, 0.52)
    ax1.grid(alpha=0.3)
    ax1.legend()

    # Şekil 3-4'ün karşılığı (n=1 her yerde 1, makale de onu çizmiyor)
    for n in [2, 3, 4]:
        ax2.plot(D, cout_ripple_norm(D, n), color=renkler[n], label=f"n={n}")
    ax2.axvline(D_benim, color="gray", ls="--", lw=1)
    ax2.set_title("C_OUT normalize ripple (SLVA882B Şekil 3-4)")
    ax2.set_xlabel("Duty cycle (D)")
    ax2.set_ylabel("Toplam ripple / tek faz ripple'ı")
    ax2.set_ylim(0, 1.02)
    ax2.grid(alpha=0.3)
    ax2.legend()

    fig.tight_layout()
    fig.savefig("sonuclar/asama1_ti_grafikleri.png", dpi=150)
    print("\nGrafik kaydedildi: sonuclar/asama1_ti_grafikleri.png")


if __name__ == "__main__":
    dogrulama()
    grafikler()
