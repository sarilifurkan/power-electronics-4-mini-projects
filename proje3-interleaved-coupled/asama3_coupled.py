"""
Aşama 3: Coupled endüktans — direct ve inverse coupling

Model (simulasyon.py):
    v1 = L * di1/dt + M * di2/dt
    v2 = M * di1/dt + L * di2/dt       M = k * L
  k > 0 -> direct coupling  (sargılar aynı yönde, DC akılar toplanır)
  k < 0 -> inverse coupling (sargılar ters yönde, DC akılar birbirini götürür)
  k = 0 -> uncoupled (Aşama 2)

Deney A: Öz endüktans aynı (L = 100 µH), |k| taranıyor.
         Faz ripple'ı, toplam ripple ve ortak çekirdeğin gördüğü DC akım ölçülüyor.
Deney B: "Adil" karşılaştırma. Inverse coupling'de toplam (çıkış) ripple'ı
         uncoupled ile AYNI kalacak şekilde L seçiliyor, faz ripple'ına bakılıyor.
Deney C: k = 0 ve k = -0.5 için dalga şekilleri.
"""

import numpy as np
import matplotlib.pyplot as plt

from simulasyon import dengeli_simule_et, olc

L0 = 100e-6                          # Proje 2'deki endüktans
K_LISTESI = np.round(np.arange(0.0, 0.91, 0.05), 2)


def elle_kontrol():
    """k = -0.5 için dün elle yaptığımız hesabı simülasyonla karşılaştır."""
    print("=== Elle hesap kontrolü: inverse, k = 0.5, L = 100 µH, D = 0.417 ===")
    Vin, Vo, f = 12.0, 5.0, 100e3
    D = Vo / Vin
    k = 0.5
    # Faz 1 açık, Faz 2 kapalı: v1 = +7 V, v2 = -5 V, M = -k L
    #   di1/dt = (v1 - (M/L) v2) / (L (1 - k^2))
    hiz_acik = ((Vin - Vo) - k * Vo) / (L0 * (1 - k ** 2))
    print(f"Faz 1'in açıkken yükselme hızı: {hiz_acik * 1e-6:.3f} A/µs "
          f"(uncoupled: {(Vin - Vo) / L0 * 1e-6:.3f} A/µs)")
    print(f"Beklenen faz ripple'ı: {hiz_acik * D / f:.3f} A")
    o = olc(dengeli_simule_et(k=-k))
    print(f"Simülasyon faz ripple'ı: {o['faz1_ripple']:.3f} A, "
          f"toplam ripple: {o['toplam_ripple']:.3f} A\n")


def deney_a():
    print("=== Deney A: aynı öz endüktans (L = 100 µH), k taraması ===")
    sonuc = {"direct": [], "inverse": []}
    for tur, isaret in [("direct", +1), ("inverse", -1)]:
        for k in K_LISTESI:
            o = olc(dengeli_simule_et(k=isaret * k, n_periyot=120))
            # Ortak çekirdekte DC akı ~ (i1 ort) + isaret * (i2 ort)  (eşit sarım sayısı)
            dc_aki = abs(o["faz1_ort"] + isaret * o["faz2_ort"])
            sonuc[tur].append((o["faz1_ripple"], o["toplam_ripple"], dc_aki, o["faz1_min"]))
            print(f"{tur:8s} k={k:.2f}: faz ripple {o['faz1_ripple']:.3f} A | "
                  f"toplam ripple {o['toplam_ripple']:.3f} A | "
                  f"çekirdek DC akımı {dc_aki:.3f} A | faz min {o['faz1_min']:.3f} A")

    fig, axlar = plt.subplots(1, 3, figsize=(15, 4.3))
    for tur, renk in [("direct", "tab:red"), ("inverse", "tab:blue")]:
        veri = np.array(sonuc[tur])
        axlar[0].plot(K_LISTESI, veri[:, 0], "o-", color=renk, ms=4, label=tur)
        axlar[1].plot(K_LISTESI, veri[:, 1], "o-", color=renk, ms=4, label=tur)
        axlar[2].plot(K_LISTESI, veri[:, 2], "o-", color=renk, ms=4, label=tur)

    axlar[0].set_title("Faz ripple'ı (her endüktans)")
    axlar[1].set_title("Toplam ripple (C_OUT'a giden)")
    axlar[2].set_title("Ortak çekirdeğin gördüğü DC akım")
    for ax, birim in zip(axlar, ["A (tepeden tepeye)", "A (tepeden tepeye)", "A"]):
        ax.set_xlabel("|k| (coupling katsayısı)")
        ax.set_ylabel(birim)
        ax.grid(alpha=0.3)
        ax.legend()
    axlar[0].axhline(sonuc["inverse"][0][0], color="gray", ls="--", lw=1)
    axlar[1].axhline(sonuc["inverse"][0][1], color="gray", ls="--", lw=1)
    axlar[0].text(0.01, sonuc["inverse"][0][0] + 0.01, "uncoupled", color="gray", fontsize=9)
    axlar[1].text(0.01, sonuc["inverse"][0][1] + 0.005, "uncoupled", color="gray", fontsize=9)
    fig.suptitle("Deney A: öz endüktans sabit (L = 100 µH), D = 0.417", y=1.02)
    fig.tight_layout()
    fig.savefig("sonuclar/asama3_deneyA_ayni_L.png", dpi=150, bbox_inches="tight")
    print("Grafik kaydedildi: sonuclar/asama3_deneyA_ayni_L.png\n")


def deney_b():
    print("=== Deney B: inverse, toplam ripple uncoupled ile eşit tutuluyor ===")
    # Toplam akımın hızı: d(i1+i2)/dt = (v1+v2) / (L + M) = (v1+v2) / (L (1-k))
    # Uncoupled ile aynı olması için L (1-k) = L0  ->  L = L0 / (1-k)
    faz, toplam = [], []
    for k in K_LISTESI:
        L = L0 / (1 - k)
        o = olc(dengeli_simule_et(L=L, k=-k, n_periyot=120))
        faz.append(o["faz1_ripple"])
        toplam.append(o["toplam_ripple"])
        print(f"k={k:.2f}  L={L*1e6:6.1f} µH: faz ripple {o['faz1_ripple']:.3f} A | "
              f"toplam ripple {o['toplam_ripple']:.3f} A")

    fig, ax = plt.subplots(figsize=(7, 4.3))
    ax.plot(K_LISTESI, faz, "o-", color="tab:blue", ms=4, label="Faz ripple'ı")
    ax.plot(K_LISTESI, toplam, "s-", color="tab:orange", ms=4, label="Toplam ripple")
    ax.set_title("Deney B: inverse coupling, toplam ripple sabit\n(L = 100 µH / (1 - k))")
    ax.set_xlabel("|k| (coupling katsayısı)")
    ax.set_ylabel("A (tepeden tepeye)")
    ax.set_ylim(0, None)
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig("sonuclar/asama3_deneyB_esit_cikis_ripple.png", dpi=150)
    print("Grafik kaydedildi: sonuclar/asama3_deneyB_esit_cikis_ripple.png\n")


def deney_c():
    fig, axlar = plt.subplots(2, 1, figsize=(10, 6.5), sharex=True)
    for ax, k, baslik in [(axlar[0], 0.0, "Uncoupled (k = 0)"),
                          (axlar[1], -0.5, "Inverse coupled (k = 0.5), aynı L")]:
        s = dengeli_simule_et(k=k)
        n = 2 * s["adim_sayisi"]
        t = (s["t"][-n:] - s["t"][-n]) * 1e6
        i1, i2 = s["i1"][-n:], s["i2"][-n:]
        ax.plot(t, i1, color="tab:green", label="Faz 1")
        ax.plot(t, i2, color="tab:purple", label="Faz 2")
        ax.plot(t, i1 + i2, color="tab:orange", lw=2, label="Toplam")
        ax.set_title(f"{baslik}   |   faz ripple {np.ptp(i1):.3f} A, "
                     f"toplam ripple {np.ptp(i1 + i2):.3f} A")
        ax.set_ylabel("Akım (A)")
        ax.grid(alpha=0.3)
        ax.legend(loc="center right", fontsize=9)
    axlar[1].set_xlabel("Zaman (µs)")
    fig.tight_layout()
    fig.savefig("sonuclar/asama3_dalga_sekilleri.png", dpi=150)
    print("Grafik kaydedildi: sonuclar/asama3_dalga_sekilleri.png")


if __name__ == "__main__":
    elle_kontrol()
    deney_a()
    deney_b()
    deney_c()
