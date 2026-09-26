# Proje 1 — Buck Converter Analitik Hesap Aracı

Bu script, bir buck (step-down) converter'ın güç kademesi için gerekli
minimum endüktans, kritik endüktans ve minimum çıkış kapasitesi değerlerini
TI'nin **SLVA477** ("Basic Calculation of a Buck Converter's Power Stage")
dokümanındaki formüllere göre hesaplar.

## Kullanılan Formüller

- **Duty Cycle:** `D = Vout / Vin` (ideal, kayıpsız durum)
- **Minimum Endüktans:** `L_min = (Vin - Vout) * D / (f_sw * ΔIL)`
- **Kritik Endüktans (CCM/DCM sınırı):** `L_crit = (1 - D) * R_load / (2 * f_sw)`
- **Minimum Çıkış Kapasitesi:** `C_min = ΔIL / (8 * f_sw * ΔVout)`

## Kullanım

```bash
python3 buck_hesap.py
```

Script, `Proje 2` (Simulink) modelinde kullanılan parametrelerle
(Vin=12V, Vout=5V, f=100kHz, R=5Ω) çalışacak şekilde ayarlanmıştır.

## Sonuçlar ve Proje 2 (Simulink) ile Karşılaştırma

| Parametre | Simulink'te Kullanılan | Bu Script'ten Hesaplanan | Yorum |
|---|---|---|---|
| Duty Cycle (D) | ≈ 0.417 | 0.4167 | Birebir uyuşuyor |
| Endüktans (L) | 100 µH | L_min = 97.22 µH | Seçilen 100 µH, minimumun az üstünde — CCM'de kalmak için güvenlik payı |
| Kritik Endüktans | — | 14.58 µH | 100 µH, kritik değerin ~7 katı üstünde → CCM'de rahat çalışılıyor (Proje 2'de DCM'e ancak R=100Ω gibi yüksek yükte geçilmesiyle tutarlı) |
| Kapasitans (C) | 220 µF | C_min = 7.50 µF | Simulink'te seçilen değer, minimumun oldukça üstünde — daha sıkı bir ripple toleransı/geçici-durum davranışı hedeflendiği için konservatif seçilmiş |

## Kaynak

TI SLVA477 — *Basic Calculation of a Buck Converter's Power Stage*
