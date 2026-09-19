# OTA güncelleme (EAS Update)

Oyun, uygulamanın içine **asset** olarak gömülü. Yani `index.html`'de yapılan
her değişiklik — denge ayarı, yeni dalga, hata düzeltmesi — App Store
incelemesinden geçmeden OTA ile gönderilebilir.

```bash
cd app
npm run sync-game                      # kök index.html'i asset'e kopyala
npx eas update --branch production -m "denge ayarı"
```

## Ne OTA ile gider, ne gitmez

| değişiklik | OTA yeter mi |
|---|---|
| `index.html` (oyunun tamamı) | **Evet** |
| `App.js`, JS tarafı | **Evet** |
| Yeni native paket eklemek | Hayır — yeni build |
| SDK yükseltmek | Hayır — yeni build |
| `app.json`'daki native alanlar (entitlement, izin) | Hayır — yeni build |

## runtimeVersion neden `fingerprint`

Güncelleme sadece **native katmanı eşleşen** build'lere verilir. Bir JS
bundle'ı, yüklü binary'de olmayan bir native modül beklerse sonuç güncelleme
değil çökme olur. `fingerprint` politikası native parmak izini hesaplayıp
uyuşmayan build'lere o güncellemeyi hiç göndermez.

Native bir şey eklediğinde parmak izi değişir, yani o build'ler eski
güncellemeleri almaz — doğru davranış budur.

## Güncelleme ne zaman uygulanır

`expo-updates`'in varsayılanı: arka planda indir, **bir sonraki** açılışta
uygula. Bu, oyuncuya "kapatıp aç" dediğinde iki kez kapatıp açması gerektiği
anlamına gelirdi.

`App.js` bunu tek sefere indiriyor: açılışta, splash zaten sanat üretimi için
ayaktayken güncelleme kontrol ediliyor; gerçekten bekleyen bir güncelleme
varsa indirilip **oracıkta** uygulanıyor (`reloadAsync`). Kontrol 3sn, indirme
12sn ile sınırlı; sunucuya ulaşılamazsa veya cihaz çevrimdışıysa mevcut
build'le devam ediliyor. Yani güncelleme yokken maliyeti sıfıra yakın.

## Çok oyunculu ile ilişkisi — önemli

`NET_PROTOCOL` tel formatının sürümü. OTA ile iki oyuncu bir süre **farklı
bundle'larda** kalabilir; bu normaldir ve el sıkışma bunu yakalayıp düzgün
reddeder ("Sürümler uyuşmuyor"). Mesaj, uygulama içinde "kapatıp yeniden aç",
tarayıcıda "sayfayı yenile" diyor — ikisi farklı, çünkü bir uygulamada
yenilenecek sayfa yok.

**Tel formatını her değiştirdiğinde `NET_PROTOCOL`'ü artır.** Artırmazsan
güncellemeyi almış ve almamış iki oyuncu bağlanır ve sessizce bozulur.

## Doldurulması gereken

`app/app.json` → `updates.url` içindeki `REPLACE_WITH_EAS_PROJECT_ID`.
`eas init` bunu kendisi yazar.
