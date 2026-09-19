# Altay — iOS/Android kabuğu

Oyunun kendisi depo kökündeki tek dosyada: `../index.html`. Burası onu
saran Expo uygulaması.

## Oyun dosyası nasıl giriyor

`scripts/sync-game.js` kökteki `index.html`'i `assets/game/index.html`'e
kopyalar. Metro kendi proje kökünün dışına çıkamadığı ve sembolik bağları
güvenilir şekilde izlemediği için kopyalanıyor. **Kaynak her zaman kök
dosyadır**; buradaki kopya üretilmiş çıktıdır, elle düzenlenmez.

Üretilmiş olmasına rağmen **git'e commit edilir**: EAS çalışma dizininden
değil git ağacından build alır, dosya izlenmiyorsa prebuild `ENOENT` ile
düşer. Yani kök `index.html` değişince `npm run sync-game` çalıştırıp
kopyayı da commit et.

Betik aynı zamanda bir kapı görevi görüyor: sayfa uzaktan script veya font
çekiyorsa senkronizasyon hata verip durur. Bu, hem çevrimdışı çalışmayı hem
de App Store 2.5.2 (uzaktan kod yükleme) riskini önler.

## Build öncesi yerel doğrulama

EAS build'leri ücretli ve yavaş. Kredi harcamadan önce:

```bash
npm run verify      # sync-game + expo-doctor + expo export
```

Sonra üretilen bundle'ı denetle (Hermes ASCII olmayan metni UTF-16 saklar,
düz grep yanıltır):

```bash
python3 ../tools/inspect_bundle.py /tmp/expo-check \
  --require registerRootComponent --require __altayNative \
  --forbid unpkg.com --forbid fonts.googleapis.com
```

## Build

```bash
npx eas build --platform ios --profile production
npx eas submit --platform ios --profile production --latest
```

`eas submit` build kredisi harcamaz; TestFlight'a giden binary ile incelemeye
gönderilen aynıdır, test sonrası yeniden build gerekmez.

## OTA güncelleme

`expo-updates` kurulu ve yapılandırılmış. Oyun asset olarak gömülü olduğu
için `index.html` değişiklikleri App Store incelemesi olmadan gönderilebilir:
`npm run sync-game && npx eas update --branch production`.
Ayrıntı ve uyarılar: `../store/ota.md`.

## Game Center

Kurulum ve leaderboard ID'leri: `../store/game-center.md`.
Entitlement `app.json` içinde; App Store Connect'te Game Center'ı açmayı
unutma — biri olup diğeri olmazsa ya gönderim bloke olur ya leaderboard
çalışmaz.

## Doldurulması gerekenler

`app.json` ve `eas.json` içinde `REPLACE_WITH_...` yazan alanlar: EAS proje
kimliği, Apple ID, App Store Connect uygulama kimliği, takım kimliği.

## Sürüm notu

`react-native` sürümü SDK 57'nin `bundledNativeModules.json` dosyasındaki
pin ile aynı olmalı (şu an 0.86.3). Bir patch sapma bile Metro'yu kırıyor —
denendi. `babel-preset-expo` üst seviye devDependency olarak durmalı, aksi
halde Metro "Cannot find module" hatasını `transformFile` TypeError'ı
altında gizliyor.
