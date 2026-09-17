# App Store Connect — Gizlilik Etiketleri (App Privacy)

Skill'in kuralı: beyan gözlenen davranışla uyuşmalı. `index.html` içindeki
tüm `http(s)://` referansları ve WebRTC yapılandırması denetlenerek
doldurulmuştur.

## "Data Collection" sorusu

**Cevap: No, we do not collect data from this app.**

Gerekçe: uygulama hiçbir veriyi geliştiriciye veya üçüncü tarafa
iletmiyor. Kalıcı ilerleme yalnızca cihazda, bir dosyada duruyor.

## Dikkat — bu bir "veri toplama" değil ama sorulursa açıklaması var

Çok oyunculu mod WebRTC kullanıyor. Apple'ın tanımına göre bu bir veri
TOPLAMA değil (geliştiriciye hiçbir şey ulaşmıyor), ama incelemeci sorarsa
doğru cevap şu:

- Eşleşme için PeerJS bulut hizmeti (`0.peerjs.com`) kullanılıyor.
- NAT geçişi için Google ve Twilio STUN sunucuları kullanılıyor.
- Eşler arasında oyun durumu (kule/düşman konumları, altın, can) gidiyor.
- WebRTC'nin doğası gereği eşler birbirinin IP adresini görebiliyor. Bu
  gizlilik politikasında açıkça yazıyor.

## Export Compliance

`app.json` içinde `ITSAppUsesNonExemptEncryption: false`.

Gerekçe: uygulama kendi şifreleme algoritmasını uygulamıyor. WebRTC'nin
zorunlu DTLS/SRTP katmanı işletim sisteminin sağladığı standart şifreleme
olduğu için muafiyet kapsamında.

## Yetenek (Capability) bayrakları

App Store Connect'te **hiçbir ek yetenek açılmamalı** — binary'de karşılığı
olmayan bir yetenek gönderimi bloke eder. Şu an binary'de yok:
- Game Center — YOK (eklenirse hem entitlement hem ASC bayrağı gerekir)
- Push Notifications — YOK
- In-App Purchase — YOK
- Sign in with Apple — YOK
