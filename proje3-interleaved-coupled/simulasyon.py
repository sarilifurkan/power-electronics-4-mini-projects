"""
2 fazlı interleaved buck converter'ın zaman simülasyonu (Aşama 2 ve 3 bunu kullanır)

Temel fikir, iki gündür konuştuğumuz kalıp:
    akımdaki değişim = (gerilim / L) x süre

Çok küçük bir süre adımı (dt) seçip her adımda:
  1) Her fazın anahtarı açık mı kapalı mı? -> anahtarlama düğümü gerilimi (Vin ya da 0)
  2) Her endüktansın üzerindeki gerilim = düğüm gerilimi - Vout
  3) Endüktans akımlarını güncelle:  i += (di/dt) * dt
  4) Kondansatörü güncelle:  Vout += (i_toplam - i_yük) / C * dt

Coupled endüktans (Aşama 3) için 3. adımda karşılıklı endüktans (M) da var:
    v1 = L * di1/dt + M * di2/dt
    v2 = M * di1/dt + L * di2/dt
  M > 0  -> direct coupling
  M < 0  -> inverse coupling
  M = 0  -> uncoupled (Aşama 2)

Varsayımlar (README'de de yazılı):
  - İdeal anahtarlar (senkron buck): düğüm ya Vin'e ya 0 V'a bağlı, kayıp yok,
    dead time yok. Senkron olduğu için akım eksiye inebilir, DCM'ye girmez.
  - Endüktans ve kondansatörde direnç (DCR, ESR) yok.
  - Yük, sabit bir direnç (R).
"""

import numpy as np


def simule_et(Vin=12.0, Vout_hedef=5.0, L=100e-6, k=0.0, C=220e-6, R=5.0,
              f=100e3, faz_kaydirma_derece=180.0, n_periyot=300, adim_sayisi=1000,
              baslangic=None):
    """İki fazlı buck'ı simüle eder, zaman dalga şekillerini döndürür.

    k : coupling katsayısı. M = k * L.
        k > 0 direct, k < 0 inverse, k = 0 uncoupled.
    adim_sayisi : bir periyottaki zaman adımı sayısı (dt = T / adim_sayisi)
    baslangic : (i1, i2, vout) başlangıç değerleri. None ise ideal ortalamalar.
    """
    T = 1 / f
    dt = T / adim_sayisi
    D = Vout_hedef / Vin                       # ideal duty cycle (kayıpsız devre)
    kayma = faz_kaydirma_derece / 360 * T      # Faz 2'nin gecikmesi (180° -> T/2)

    # Endüktans matrisi ve tersi:  [v1, v2] = Lmat @ [di1/dt, di2/dt]
    M = k * L
    Lmat = np.array([[L, M],
                     [M, L]])
    Lters = np.linalg.inv(Lmat)                # di/dt = Lters @ v
    a, b = float(Lters[0, 0]), float(Lters[0, 1])   # simetrik: Lters = [[a, b], [b, a]]

    # Başlangıç: kararlı duruma yakın başlat ki oturması kısa sürsün
    if baslangic is None:
        Io = Vout_hedef / R
        baslangic = (Io / 2, Io / 2, Vout_hedef)   # her faz yükün yarısını taşır
    i1, i2, vout = baslangic

    N = n_periyot * adim_sayisi
    t_kayit = np.empty(N)
    i1_kayit = np.empty(N)
    i2_kayit = np.empty(N)
    vout_kayit = np.empty(N)
    iin_kayit = np.empty(N)                    # girişten (Vin'den) çekilen akım

    for adim in range(N):
        t = adim * dt

        # 1) Anahtarlar: periyodun ilk D kısmında açık
        acik1 = (t % T) < D * T
        acik2 = ((t - kayma) % T) < D * T

        # 2) Anahtarlama düğümü gerilimleri ve endüktans gerilimleri
        vsw1 = Vin if acik1 else 0.0
        vsw2 = Vin if acik2 else 0.0
        vL1 = vsw1 - vout
        vL2 = vsw2 - vout

        # 3) Akımların değişim hızı (coupled ise diğer fazın etkisi de burada)
        di1 = a * vL1 + b * vL2
        di2 = b * vL1 + a * vL2
        i1 += di1 * dt
        i2 += di2 * dt

        # 4) Kondansatör: giren (i1 + i2) - çıkan (yük akımı)
        i_yuk = vout / R
        vout += (i1 + i2 - i_yuk) / C * dt

        # Girişten akım sadece üst MOSFET açıkken çekilir ("pencere")
        iin = (i1 if acik1 else 0.0) + (i2 if acik2 else 0.0)

        t_kayit[adim] = t
        i1_kayit[adim] = i1
        i2_kayit[adim] = i2
        vout_kayit[adim] = vout
        iin_kayit[adim] = iin

    return {"t": t_kayit, "i1": i1_kayit, "i2": i2_kayit, "vout": vout_kayit,
            "iin": iin_kayit, "T": T, "adim_sayisi": adim_sayisi, "D": D,
            "baslangic": baslangic}


def dengeli_simule_et(tur_sayisi=3, **parametreler):
    """Akım dengeleme yapılmış simülasyon.

    Neden gerekli? Modelde endüktansların direnci yok. Başlangıçta iki fazın
    ortalama akımı arasında küçük bir fark oluşursa, bunu düzeltecek hiçbir şey
    yok ve fark sonsuza kadar kalıyor (bir faz 0.6 A, diğeri 0.4 A taşıyor).
    Gerçek devrede bunu controller'ın akım dengeleme döngüsü düzeltir
    (SLVA882B Bölüm 4: "en büyük zorluk akım dengeleme").

    Burada aynı etkiyi basitçe elde ediyoruz: simülasyonu çalıştır, iki fazın
    ortalamaları arasındaki farkı ölç, başlangıç akımlarını farkın yarısı kadar
    birbirine yaklaştır, tekrar çalıştır. Devre doğrusal olduğu için 2-3 turda
    fazlar eşitleniyor.
    """
    baslangic = None

    for _ in range(tur_sayisi):
        sonuc = simule_et(baslangic=baslangic, **parametreler)
        n = 10 * sonuc["adim_sayisi"]                     # son 10 periyot
        fark = sonuc["i1"][-n:].mean() - sonuc["i2"][-n:].mean()
        i1_0, i2_0, v_0 = sonuc["baslangic"]
        baslangic = (i1_0 - fark / 2, i2_0 + fark / 2, v_0)

    return sonuc


def _periyotlara_bol(x, adim, son_periyot):
    """Sinyalin son 'son_periyot' periyodunu satır satır ayırır: (periyot, adım)."""
    parca = x[-(son_periyot * adim + 1):]           # +1: son periyodun bitiş noktası
    satirlar = parca[:-1].reshape(son_periyot, adim)
    bitisler = parca[adim::adim]                     # her periyodun bitiş değeri
    return satirlar, bitisler


def _periyot_ripple(x, adim, son_periyot):
    """Her periyodun tepeden tepeye dalgalanmasını ölçüp ortalamasını alır.

    Neden bu kadar dikkatli? L ve C birlikte ~1.5 kHz'lik yavaş bir salınım
    (LC rezonansı) yapıyor ve modelde bunu sönümleyecek direnç çok az. Bu yavaş
    salınım, ölçtüğümüz 100 kHz'lik ripple'ın üstüne bindiğinde tepeden tepeye
    değeri büyütüyor. Her periyotta, başlangıç ile bitiş arasındaki farkı
    (yavaş kaymayı) düz bir çizgi olarak çıkarıyoruz. Gerçek ripple periyodik
    olduğu için başlangıç ve bitiş değerleri zaten eşit, ona dokunmuyor.
    """
    satirlar, bitisler = _periyotlara_bol(x, adim, son_periyot)
    oran = np.arange(adim) / adim                    # periyot içindeki konum: 0 -> 1
    kayma = (bitisler - satirlar[:, 0])[:, None] * oran
    duz = satirlar - kayma
    return np.mean(duz.max(axis=1) - duz.min(axis=1))


def olc(sonuc, son_periyot=10):
    """Son birkaç periyot üzerinden (kararlı durum) ölçüm yapar."""
    adim = sonuc["adim_sayisi"]
    n = son_periyot * adim
    i1 = sonuc["i1"]
    i2 = sonuc["i2"]
    toplam = i1 + i2

    # C_IN'in RMS akımı: Vin sadece ortalamayı verir, farkı C_IN karşılar.
    # Her periyot için ayrı hesaplayıp ortalıyoruz (yavaş salınımdan etkilenmesin).
    iin_satirlar, _ = _periyotlara_bol(sonuc["iin"], adim, son_periyot)
    cin_rms = np.sqrt(np.mean(iin_satirlar.var(axis=1)))

    return {
        "faz1_ort": i1[-n:].mean(),
        "faz2_ort": i2[-n:].mean(),
        "toplam_ort": toplam[-n:].mean(),          # = yük akımı (kondansatör ort. 0)
        "faz1_ripple": _periyot_ripple(i1, adim, son_periyot),     # tepeden tepeye
        "faz1_min": i1[-n:].min(),                 # < 0 ise akım tersine dönmüş demek
        "toplam_ripple": _periyot_ripple(toplam, adim, son_periyot),
        "vout_ort": sonuc["vout"][-n:].mean(),
        "vout_ripple": _periyot_ripple(sonuc["vout"], adim, son_periyot),
        "cin_rms": cin_rms,
    }
