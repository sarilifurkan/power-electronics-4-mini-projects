# Proje 4: Seri Bağlı Bataryalarda Arızalı Bataryayı Bulma (Fikir Aşaması)

> Bu proje bir **fikir ve tasarım taslağı**. Sistemi henüz kurmadım. Laboratuvarda karşılaştığım bir soruna nasıl bir çözüm olabileceğini düşündüm ve bu süreçte HPPC testini öğrendim.

## Problem

Bu problemi laboratuvarda hocamdan duydum. Deneylerde seri bağlı bataryalar kullanılıyor, sayılarının 28 olduğunu hatırlıyorum. Bataryalardan biri boşaldığında ya da arızalandığında hangisi olduğunu bulmanın tek yolu her bataryayı tek tek ölçmek. Hocam bunu üretici firmaya sormuş, firma böyle bir sistemleri olmadığını söylemiş.

Benim sorum şuydu: **Arızalı bataryayı otomatik olarak bulan bir sistem nasıl tasarlanabilir?**

## Neden yazılım yetmiyor?

İlk aklıma gelen, bunu sadece yazılımla çözmekti. Ama seri bağlı bataryalarda dışarıdan sadece toplam gerilim görülebiliyor:

$$V_{toplam} = V_1 + V_2 + \dots + V_{28}$$

Bu, 1 denklem ve 28 bilinmeyen demek. Hangi bataryanın sorunlu olduğu bu tek sayıda yok. Yani her bataryayı ayrı ölçen bir **donanım** gerekiyor.

## HPPC'den öğrendiğim

Laboratuvardaki testler HPPC (Hybrid Pulse Power Characterization) ile yapılıyor. Kısaca: bataryaya kısa bir akım darbesi veriliyor, gerilimin nasıl tepki verdiğine bakılıyor.

Darbe başladığı an gerilim aniden düşüyor. Bu düşüş bataryanın **iç direncinden** kaynaklanıyor:

$$R = \frac{\Delta V}{I}$$

Örneğin 10 A'lik darbede sağlam batarya 50 mV düşüyorsa R = 5 mΩ. Arızalı batarya 120 mV düşüyorsa R = 12 mΩ. Bataryalar yaşlandıkça ya da arızalandıkça iç dirençleri artıyor.

## Fikrim

Seri bağlı bataryaların **hepsinden aynı akım geçiyor.** Yani HPPC darbesi geldiğinde 28 batarya aynı yükü taşıyor. O anda her bataryanın gerilim düşüşünü ayrı ölçersem, **en çok düşen batarya iç direnci en yüksek, yani arızalı olandır.**

Tek darbe, 28 batarya, tek seferde teşhis. Akımı bilmeme bile gerek yok, çünkü akım hepsi için aynı. Düşüşleri kıyaslamak yeterli.

## Referans aldığım çalışma

Benzer bir ölçümü Stanford'dan bir ekip Audi e-tron batarya modüllerinde yapmış (Marini vd., 2026, arXiv ön baskısı). Her hücrenin gerilimini basit bir kartla ölçmüşler: gerilim bölücü + filtre + ADS1115 (ADC) + Raspberry Pi Pico. HPPC darbelerinden her hücrenin iç direncini hesaplamışlar.

Ben bu ölçüm fikrini kendi problemime uyarladım. Aradaki fark: onlar 3 hücrelik modülleri **tek tek** test etmiş, gerilim en fazla 12,6 V. Bizde ise 28 batarya **aynı anda** seri bağlı. Toplam gerilim yüksek olduğu için ölçüm kartlarını **izole** etmem gerekiyor. Bu da benim tasarıma eklediğim kısım.

## Tasarım

```mermaid
flowchart LR
    B["28 seri batarya<br/>(7 grup × 4)"] --> K["7 ölçüm kartı<br/>(her biri 4 batarya)"]
    K -->|"izole I2C"| P["Raspberry Pi Pico"]
    P -->|USB| PC["Bilgisayar<br/>analiz + panel"]
```

- **Gruplama:** 28 bataryayı 4'erli 7 gruba ayırdım. Her grubun kendi ölçüm kartı var. Böylece hiçbir kart 4 bataryadan fazla gerilim görmüyor. 4'ü seçtim çünkü ADS1115'in 4 kanalı var.
- **Ölçüm kartı (7 tane, hepsi aynı):** Gerilim bölücü (gerilimi küçültür), filtre (gürültüyü temizler), ADS1115 (gerilimi sayıya çevirir), izolatör (veriyi güvenli tarafa geçirir) ve izole DC-DC (kartı besler).
- **Ana kart:** Raspberry Pi Pico 7 kartı sırayla okuyup verileri USB ile bilgisayara yolluyor.
- **Kutu:** Kartlar 3D baskı bir kutuda, her biri kendi plastik bölmesinde duruyor.

**Pico yerine STM32:** Ana kartta Pico yerine STM32 de kullanılabilir. STM32'nin bazı serilerinde yerleşik CAN desteği var. Bu sayede bataryalar laboratuvarda dağınık durursa kartlar ayrı kutulara konup uzun mesafede CAN ile haberleşebilir. Ayrıca STM32'de birden fazla I2C hattı var. ADS1115 4 farklı adres alabildiği için 2 hatta 8 karta kadar bağlanabiliyor, bu da 7 kart için yeterli. Geçen dönem mikroişlemciler dersini aldım ve STM32 ile kod yazdım, bu yüzden bu seçenek bana yakın geliyor.

Varsayım: Batarya türünü bilmediğim için Li-ion (hücre başına en fazla 4,2 V) varsaydım. Tür farklıysa sadece bölücü dirençleri değişir.

## Teşhis nasıl yapılıyor?

1. HPPC darbesi başlıyor.
2. Her bataryanın darbe öncesi ve sonrası gerilimi karşılaştırılıyor, ΔV bulunuyor.
3. Her batarya için R = ΔV / I hesaplanıyor (birkaç darbenin ortalaması).
4. R'si diğerlerinden belirgin şekilde yüksek olan batarya işaretleniyor.

Ek kural: Boşaltma sırasında kesme gerilimine **ilk ulaşan** batarya en zayıf batarya.

### Sözde kod

```
her ölçümde:
    7 kartın her birinden 4 kanalı oku
    ardışık farkları alarak 28 batarya gerilimini bul
    bilgisayara gönder

her HPPC darbesinde:
    her batarya için:
        ΔV = darbe öncesi gerilim − darbe sonrası gerilim
        R = ΔV / I
    ortanca R'yi bul
    R'si ortancadan çok yüksek olanları "ARIZALI" işaretle
    paneli güncelle
```

### Panel taslağı (terminalde)

```
Grup 5 | [17] 3.62V 12.1mΩ !! | [18] 3.70V 5.0mΩ OK | [19] 3.71V 5.1mΩ OK | [20] 3.70V 4.8mΩ OK
UYARI: Batarya 17 → iç direnç diğerlerinin yaklaşık 2,4 katı
```

(Değerler örnektir.)

## Bir fikrim daha: 28 yerine 5 ölçüm

Grup testi (group testing) diye bir yöntem okudum. Çok sayıda örnek içinden kusurlu olanı, hepsini tek tek test etmek yerine gruplar halinde test ederek bulmaya dayanıyor. Bunu bataryalara uygulamak aklıma geldi.

İki uç arasındaki gerilim, aradaki bataryaların toplamı. Yani:

1. 28 bataryayı ikiye bölüp 1–14 ve 15–28 aralıklarının toplam düşüşünü ölçersem, arızalı batarya hangi yarıdaysa o tarafın düşüşü daha büyük çıkar.
2. O yarıyı tekrar ikiye bölerim: 14 → 7 → 4 → 2 → 1.

Böylece tek bir arızalı bataryayı **yaklaşık 5 ölçümde** bulabilirim (log₂28 ≈ 5). HPPC zaten birden fazla darbe verdiği için her darbede farklı bir aralık ölçülebilir. Bu durumda 7 izole kart yerine **tek bir izole ölçüm kanalı** ve hangi uçların ölçüleceğini seçen bir anahtar (röle) düzeni yetebilir. Bu da maliyeti ciddi şekilde düşürür.

Ama bu yöntem göründüğü kadar basit değil:
- Uzun bir aralığı (ör. 14 batarya) ölçünce gerilim büyür, bölme oranı artar ve tek bir bataryanın küçük farkını görmek zorlaşır.
- Birden fazla arızalı batarya varsa basit ikiye bölme yetmez, daha karmaşık bir yöntem gerekir.
- Yüksek gerilimde röleyle uç seçmek ayrı bir güvenlik ve tasarım sorunu.
- Ölçümler farklı darbelerde yapıldığı için darbeler arasında bataryaların durumunun değişmemesi gerekir.

Bu fikri ayrıca araştırmak istiyorum. İlk tasarımı ise her bataryayı ayrı ölçen sistem olarak bıraktım, çünkü daha güvenilir ve bu fikri test etmek için de referans olarak kullanılabilir.

## Yaklaşık maliyet (Ekim 2026)

| Parça | Adet | Yaklaşık toplam |
|---|---|---|
| Raspberry Pi Pico | 1 | 250–360 TL |
| ADS1115 modülü | 7 | 900–1.400 TL |
| ADuM1250 izolatör modülü | 7 | 2.100–3.500 TL (tahmini) |
| B0505S izole DC-DC | 7 | 850–1.600 TL |
| Direnç, kondansatör, sigorta, konnektör, pertinaks, kablo | | 1.400–3.000 TL (tahmini) |
| Kutu (PETG filament) | | 150–300 TL (tahmini) |
| **Toplam** | | **≈ 5.800–10.300 TL** |

En pahalı kalem izolatörler. Türkiye'de hazır modül bulamadım. Piyasadaki hazır "akıllı BMS" kartları daha ucuz (24 hücre için ~3.300 TL), ama en fazla 24 hücreyi destekliyorlar, sadece lityum bataryalarla çalışıyorlar ve HPPC analizi yapmıyorlar.

## Referans çalışmada açık kalan, benim de düşünmem gereken konular

Marini vd. kendi çalışmalarında bazı konuları çözemediklerini açıkça belirtiyor. Bunlar benim tasarımım için de geçerli:

- **Bağlantı direnci:** Ölçülen direnç, hücreler arasındaki bağlantı parçalarının direncini de içeriyor ve bunu hücrenin kendi direncinden ayıramıyorlar. Bizde de aynı durum olacak.
- **Sıcaklık:** İç direnç sıcaklıkla değişiyor (soğukta artıyor). Onlar sadece kutunun yüzeyinden sıcaklık ölçebilmiş, hücrelerin iç sıcaklığını bilmiyorlar. Ortadaki hücrenin direncinin neden daha düşük çıktığını kesin açıklayamıyorlar. Benim sistemimde sıcaklık ölçümü hiç yok.
- **Ölçüm gecikmesi:** Gerilim verisi akım verisinden yaklaşık 100 ms geç kaydedilmiş. Darbe anındaki düşüşü doğru ölçmek için bunu hesaba katmaları gerekmiş. Bizde de akım ile gerilim farklı cihazlardan geleceği için benzer bir sorun çıkabilir.
- **Doluluk seviyesi:** Direnç bataryanın ne kadar dolu olduğuna göre de değişiyor. Bataryalar aynı dolulukta değilse kıyaslama bozulabilir. Onlar bunu testten önce hücreleri dengeleyerek çözmüş, benim tasarımımda dengeleme yok.

## Sınırlamalar

- Sistem kurulmadı, gerçek veriyle test edilmedi.
- Batarya türü ve tam sayısı varsayım.
- Ölçülen direnç bataryalar arasındaki bağlantıların direncini de içeriyor. Kıyaslama yaptığım için arızalıyı bulmayı engellemiyor.
- Yüksek gerilim nedeniyle gerçek bataryalarla çalışmak mutlaka gözetim altında yapılmalı.

## Sonraki adımlar

1. Tek bir kartı düşük gerilimde (birkaç pille) kurup çalıştırmak.
2. İzolasyonu ekleyip doğrulamak.
3. Sağlam bir bataryaya küçük bir direnç ekleyerek yapay arıza oluşturmak ve sistemin bulup bulmadığını test etmek.
4. Sonra 7 karta çıkmak, ana kartı STM32'ye taşımak ve kendi PCB tasarımımı yapmak.
5. 5 ölçüm fikrini araştırıp tam sistemle karşılaştırmak.

## Kaynaklar

1. G. Marini, A. Colombo, A. Lanubile, W. A. Paxton, S. Onori, "Design of an embedded hardware platform for cell-level diagnostics in commercial battery modules," *arXiv preprint* arXiv:2603.29107, 2026. [Link](https://arxiv.org/abs/2603.29107)
2. Idaho National Laboratory, *Battery Test Manual for Plug-In Hybrid Electric Vehicles* (HPPC tanımı). [Link](https://inldigitallibrary.inl.gov/sites/sti/sti/6308373.pdf)
3. Arbin Instruments, "HPPC Testing with Arbin MITS Pro," Application Note AN-024. [Link](https://www.arbin.com/hybrid-pulse-power-characterization-hppc-testing-with-arbin-mits-pro.html)
4. Wikipedia, "Group testing." [Link](https://en.wikipedia.org/wiki/Group_testing)
