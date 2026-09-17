# Game Center kurulumu

Kod tarafı hazır. Kalan iş App Store Connect'te.

## 1. Leaderboard tanımla

App Store Connect → uygulaman → **Services → Game Center → Leaderboards**.
Üç tane oluştur, **ID'ler birebir bunlar olmalı**:

| Leaderboard ID | Adı (öneri) |
|---|---|
| `altay.score.easy` | Acemi — Puan |
| `altay.score.normal` | Normal — Puan |
| `altay.score.hard` | Zor — Puan |

Ayarlar:
- **Score Format:** Integer
- **Sort Order:** High to Low
- **Score Range:** 0 – 999999 (isteğe bağlı ama spam'i keser)
- En az bir dil için görünen ad girmek zorunlu

ID'ler `app/App.js` içindeki `LEADERBOARDS` sabitinde duruyor. Değiştirirsen
iki tarafı da değiştir — **var olmayan bir ID'ye gönderim sessizce başarısız
olur**, bir leaderboard'ın "çalışmamasının" en yaygın sebebi budur.

## 2. Zorluk seviyesi başına ayrı liste — neden

Zor modda 32 dalgayı bitiren biri, Acemi'de bitirenle aynı listede
yarışmamalı. Sıralama **puana** göre (koşunun topladığı ödül toplamı), dalga
sayısına göre değil: pek çok oyuncu 32'yi bitirecek ve puan bu beraberlikleri
çözüyor.

## 3. Yetenek bayrağı — dikkat

Binary'de entitlement zaten var (`app/app.json` → `ios.entitlements`):

```json
"com.apple.developer.game-center": true
```

App Store Connect'te Game Center'ı **açmak zorundasın**. İkisi birlikte
gitmeli:
- ASC'de açık + binary'de entitlement yok → **gönderim bloke olur**
- Binary'de entitlement var + ASC'de kapalı → leaderboard hiç çalışmaz

## 4. Oyunda ne oluyor

- Açılışta sessizce Game Center'a giriş denenir. Oyuncu girmemişse veya
  reddederse **hiçbir şey olmaz** — oyuna girişi asla engellemez.
- Koşu bitince puan ilgili listeye **sessizce** gönderilir. Ekrana modal
  atılmaz.
- Bitiş ekranındaki **SIRALAMA** butonu Game Center panelini açar,
  **PAYLAŞ** sistem paylaşım penceresini. İkisi de sadece uygulama içinde
  görünür; tarayıcıda hiç çizilmezler.

## 5. Test

Simulator'da Game Center çalışmaz; **gerçek cihazda** Settings → Game Center
üzerinden bir Sandbox hesabıyla giriş yapıp TestFlight build'iyle dene.

## Bilinen sınır

Kullanılan paket (`react-native-game-services`) **başarım (achievement)
desteklemiyor**, sadece leaderboard. Başarım istenirse ya paket
genişletilmeli ya da yerel bir Expo modülü yazılmalı.
