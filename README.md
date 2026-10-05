# Güç Elektroniği: 4 Mini Proje

Bu repo, güç elektroniği laboratuvarı için birikimimi artırmak amacıyla hazırladığım dört mini projeyi içeriyor. Proje yolunu seçmemin iki sebebi var: konuları uygulayarak öğrenmek ve bu alana olan ilgimi somut çalışmalarla gösterebilmek.

Projeler birbirinin üzerine kuruluyor. Tek fazlı buck dönüştürücünün elle hesabından başlayıp simülasyona, oradan çok fazlı ve coupled bobinli yapılara, son olarak da laboratuvarda karşılaşılan gerçek bir probleme yönelik bir izleme sistemi fikrine uzanıyor.

```mermaid
flowchart LR
    P1["Proje 1<br/>Analitik hesap"] --> P2["Proje 2<br/>Simülasyon: CCM / DCM"]
    P2 --> P3["Proje 3<br/>Çok fazlı + coupled bobin"]
    P3 --> P4["Proje 4<br/>Batarya izleme arayüzü"]
```

## Projeler

| # | Proje | Araçlar | Ana kaynak | Durum |
|---|---|---|---|---|
| 1 | [Buck dönüştürücü hesap aracı](proje1-python-hesap-araci/) | Python | TI SLVA477 | ✅ Tamamlandı |
| 2 | [Buck dönüştürücü simülasyonu: CCM ve DCM](proje2-buck-converter/) | MATLAB Online, Simulink | Proje 1'in hesapları | ✅ Tamamlandı |
| 3 | [İki fazlı interleaved buck: coupled ve uncoupled bobin](proje3-interleaved-coupled/) | Python (NumPy, Matplotlib) | TI SLVA882B, SLYT449, SLYY072 | ✅ Tamamlandı |
| 4 | Seri bataryalarda arızalı hücre tespiti için izleme arayüzü | Kavramsal tasarım | Marini vd., 2026 | 🛠️ Hazırlanıyor |

Her projenin kendi klasöründe, yöntemi ve sonuçları anlatan ayrıntılı bir README bulunuyor.

---

## Proje 1: Buck dönüştürücü hesap aracı

**Klasör:** [`proje1-python-hesap-araci/`](proje1-python-hesap-araci/)

TI'nin *Basic Calculation of a Buck Converter's Power Stage* (SLVA477) uygulama notundaki formülleri kullanan analitik bir hesap aracı. Giriş/çıkış gerilimi, yük akımı ve anahtarlama frekansı verildiğinde güç katının temel büyüklüklerini (görev oranı, endüktans, bobin ripple akımı, çıkış kondansatörü gibi) hesaplıyor.

**Neden önemli:** Sonraki bütün projelerde kullandığım temel ilişkiler (D = V_OUT / V_IN, Δi = V_L · Δt / L) burada oturdu. Proje 2'deki simülasyon sonuçlarını bu hesaplarla doğruladım.

## Proje 2: Buck dönüştürücü simülasyonu, CCM ve DCM

**Klasör:** [`proje2-buck-converter/`](proje2-buck-converter/)

Tek fazlı buck dönüştürücünün Simulink modeli. İki aşamadan oluşuyor:

- **Aşama 1, CCM doğrulaması:** Kararlı durumdaki çıkış gerilimi (V_OUT), bobin akımı (i_L) ve ikisinin ripple değerleri, elle hesaplanan teorik değerlerle karşılaştırıldı ve tuttuğu görüldü.
- **Aşama 2, DCM:** Bobin akımı integratörüne sıfır alt sınır (lower saturation limit) eklenerek diyot benzeri bir davranış modellendi. R = 5 Ω (CCM) ve R = 100 Ω (DCM) durumları karşılaştırıldı; sonuçlar kritik direnç R_krit = 2·L·f / (1 − D) ile doğrulandı.

**Yöntem notu:** MATLAB Online'ın temel sürümünde Simscape Electrical bulunmadığı için devreyi denklemlerden, integratör bloklarıyla kurdum. Modeli elle blok sürükleyerek değil, `add_block` / `add_line` komutlarıyla bir MATLAB script'i üzerinden oluşturdum; böylece model tekrar üretilebilir.

**Parametreler:** V_OUT = 5 V, L = 100 µH, C = 220 µF, f_SW = 100 kHz. Aynı değerler Proje 3'te faz başına kullanıldı.

## Proje 3: İki fazlı interleaved buck, coupled ve uncoupled bobin

**Klasör:** [`proje3-interleaved-coupled/`](proje3-interleaved-coupled/)

Hocamın tavsiye ettiği üç TI dokümanını (SLVA882B, SLYT449, SLYY072) temel alan bir çalışma. Amaç, çok fazlı buck dönüştürücülerin grafiklerinin arkasındaki formülleri bileşen bileşen anlamaktı.

- **Aşama 1:** SLVA882B'deki normalize C_IN RMS akımı (Denklem 1) ve C_OUT ripple akımı (Denklem 2) formüllerinin grafikleri.
- **Aşama 2:** Bağımsız bobinli 2 fazlı buck. 180° ve 0° faz kaydırma karşılaştırması ve formüllerin simülasyonla yeniden üretilmesi. D = 0.417'de faz kaydırma, C_OUT'a giden ripple'ı 7 kat azaltıyor.
- **Aşama 3:** Makalelerde bulunmayan, hocamın talebiyle eklediğim coupled bobin karşılaştırması. Direct ve inverse kuplaj incelendi. Inverse kuplajda L − M sabit tutulduğunda, C_OUT'un gördüğü ripple değişmeden faz ripple'ı k = 0.5'te %57 azalıyor.

Klasördeki README, her formülü ilgili makalenin bölüm, denklem ve şekil numarasıyla eşleştiren bir tablo içeriyor.

## Proje 4: Seri bataryalarda arızalı hücre tespiti için izleme arayüzü (hazırlanıyor)

Laboratuvardaki bir problemden doğan bir fikir: deneylerde 28 batarya seri bağlanıyor ve biri arızalandığında hangisi olduğunu bulmanın tek yolu bataryaları tek tek kontrol etmek.

Bu proje, Marini vd. (2026) tarafından önerilen hücre seviyesinde tanı (cell-level diagnostics) platformundan uyarlanmış kavramsal bir sistem tasarımı olacak. Planlanan içerik:

- HPPC (Hybrid Pulse Power Characterization) testinin mantığı ve arıza tespitinde nasıl kullanılabileceği
- Sistemin blok yapısı ve izleme arayüzü paneli (sözde kod / pseudocode ile)
- Maliyet analizi

Batarya tipi bilinmediği için proje belirli bir donanım ya da entegre devre seçimine girmeden, fikir seviyesinde kalacak.

---

## Kullanılan araçlar

| Araç | Proje |
|---|---|
| Python (NumPy, Matplotlib) | 1, 3 |
| MATLAB Online, Simulink | 2 |

## Yapay zekâ kullanımı hakkında

Kodlar yapay zekâ desteğiyle yazıldı. Formüllerin nereden geldiğini ve ne için kullanıldığını, kodlardaki yaklaşımları ve sonuç grafiklerini kendim inceledim; sonuçları elle yaptığım hesaplarla ve kaynak dokümanlarla karşılaştırarak doğruladım.

## Kaynaklar

1. B. Hauke, *Basic Calculation of a Buck Converter's Power Stage*, Texas Instruments, SLVA477. https://www.ti.com/lit/pdf/slva477
2. C. Parisi, *Multiphase Buck Design From Start to Finish (Part 1)*, Texas Instruments, SLVA882B, 2017 (rev. 2021). https://www.ti.com/lit/pdf/slva882
3. D. Baba, *Benefits of a multiphase buck converter*, Texas Instruments Analog Applications Journal, SLYT449, 2012. https://www.ti.com/lit/pdf/slyt449
4. K. Wong, D. Evans, *Merits of multiphase buck DC/DC converters in small form factor applications*, Texas Instruments, SLYY072, 2015. https://www.ti.com/lit/pdf/slyy072
5. Marini vd., hücre seviyesinde batarya tanı platformu, arXiv:2603.29107, 2026.
