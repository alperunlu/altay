# App Store gönderim dosyaları

- `listing-tr.md` / `listing-en.md` — App Store Connect metin alanları,
  karakter sınırlarıyla birlikte
- `privacy.md` — gizlilik politikası (bir yere yayınlanıp URL'si ASC'ye
  girilmeli, zorunlu alan)
- `privacy-labels.md` — App Privacy formu nasıl doldurulacak + export
  compliance + yetenek bayrakları
- `screenshots/` — gerçek oyundan, Apple'ın tam piksel ölçülerinde

## Ekran görüntüsü ölçüleri

| dosya öneki | ölçü | cihaz sınıfı |
|---|---|---|
| `phone-*` | 2868×1320 | 6.9" iPhone, yatay |
| `ipad-*` | 2752×2064 | 13" iPad, yatay |

App Store Connect tam ölçü dışındaki her şeyi reddeder. Yeniden üretmek
için: oyunu `localhost:9003`'te servis et ve
`tools/shots_store.js` benzeri bir betikle sürücü olarak Playwright kullan
(bu oturumda kullanılan betik scratchpad'deydi; mantığı: gerçek oyunu
ilginç bir duruma sür, sahte kurgu yapma).

## Doldurulması gerekenler

`app/app.json` ve `app/eas.json` içinde `REPLACE_WITH_...`:
- EAS proje kimliği
- Apple ID
- App Store Connect uygulama kimliği
- Apple takım kimliği

`store/privacy.md` içinde iletişim e-postası.
`listing-tr.md` içinde Support URL.
