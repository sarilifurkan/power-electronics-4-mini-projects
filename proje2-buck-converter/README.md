# Proje 2: Buck Converter — CCM/DCM Simülasyonu

Açık çevrim buck converter'ın Simulink'te durum-uzay (averaged) modeliyle
kurulması, CCM ve DCM modlarının simüle edilip karşılaştırılması.

MATLAB Online (basic) ortamında, Simscape Electrical olmadığı için model
`add_block` / `add_line` ile programatik olarak kurulmuştur.


## Aşama 1: CCM Doğrulaması

### Parametreler
| Vin | Vout (hedef) | D | L | C | R | f_sw |
|---|---|---|---|---|---|---|
| 12 V | 5 V | 0,4167 | 100 µH | 220 µF | 5 Ω | 100 kHz |

### Model
Durum değişkenleri iL ve Vout, iki diferansiyel denklemle tanımlanır:

    L · diL/dt   = s·Vin − Vout
    C · dVout/dt = iL − Vout/R

s(t), anahtarın PWM durumu (0 veya 1). Bloklar bu denklemleri
Gain/Sum/Integrator kombinasyonuyla çözer.

### Doğrulama
| Büyüklük | Teorik | Simülasyon | Fark |
|---|---|---|---|
| Vout (kararlı durum) | 5,000 V | 5,0000 V | ~0 |
| iL (ortalama) | 1,000 A | 0,999 A | ~%0,1 |
| Vout ripple (pp) | ~1,65 mV | 1,65 mV | ~0 |
| iL ripple (pp) | ~0,29 A | 0,292 A | ~%0,7 |

### Dosyalar
- `asama1-ccm/build_buck_model.m` — modeli kuran script
- `asama1-ccm/BuckConverterModel_v2.slx` — kurulan model
- `asama1-ccm/buck_vout_iL.png` — Vout ve iL dalga şekilleri
![Vout ve iL](buck_vout_iL.png)
### Bilinen sınır
Model idealdir (anahtar/diyot kaybı, ESR yok) ve indüktör akımının
sıfırın altına inmesini engelleyen bir diyot kısıtı içermez. Bu yüzden
şu an yalnızca CCM davranışı gösterir; yük ne kadar hafifletilirse
hafifletilsin Vout = D·Vin'de sabit kalır. DCM, Aşama 2'de eklenecektir.

## Aşama 2: DCM Davranışı 

Planlanan: iL'nin sıfırın altına inmesini engelleyen bir kısıt eklemek,
yükü kritik direncin (R_kritik ≈ 34,3 Ω) üstüne çıkarıp DCM'ye geçişi
göstermek, CCM ile DCM'de Vout ve iL dalga şekillerini karşılaştırmak.
