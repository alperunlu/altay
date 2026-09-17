# Altay — Gizlilik Politikası

Son güncelleme: 2026-09-17

## Kısa hâli

Altay hiçbir kişisel veri toplamaz, saklamaz veya iletmez. Hesap yok,
analitik yok, reklam yok, izleme yok. Tek oyunculu mod hiçbir ağ bağlantısı
kurmaz.

## Cihazında kalan veriler

**Kalıcı ilerleme.** Kazandığın Şan ve aldığın kalıcı yükseltmeler
cihazındaki bir dosyada tutulur. Hiçbir yere gönderilmez. Uygulamayı
silersen bu veri de silinir.

## Yalnızca çok oyunculu modda kurulan bağlantılar

Bir odaya girdiğinde veya oda kurduğunda oyun, cihazları doğrudan
birbirine bağlamak için WebRTC kullanır. Bunun için üç tür sunucuya
başvurulur:

1. **Eşleşme sunucusu** (PeerJS bulut hizmeti, `0.peerjs.com`) — sadece iki
   cihazın birbirini bulmasını sağlayan oda kodunu ve bağlantı bilgisini
   aktarır. Oyun verisi buradan geçmez.
2. **STUN sunucuları** (`stun.l.google.com`, `global.stun.twilio.com`) —
   cihazının internetten görünen IP adresini öğrenmek için kullanılır.
3. **TURN aktarma sunucuları** (PeerJS) — doğrudan bağlantı kurulamadığında
   trafiği aktarır.

Bu mekanizma gereği **odaya katılan oyuncular birbirinin IP adresini
görebilir.** Bu, doğrudan cihazdan cihaza bağlantı kuran her uygulama için
geçerlidir. Tanımadığın kişilerle oda kodu paylaşırken bunu bil.

Aktarılan oyun verisi yalnızca oyun durumundan ibarettir: kule konumları,
düşman konumları, altın, can. İsim, e-posta, konum veya cihaz kimliği
iletilmez.

## Paylaşım

Bir koşu bittiğinde skorunu paylaşmayı seçebilirsin. Bu, cihazının kendi
paylaşım penceresini açar; nereye göndereceğine sen karar verirsin. Uygulama
kendiliğinden hiçbir yere bir şey göndermez.

## Çocuklar

Uygulama çocuklara yönelik olarak pazarlanmıyor ve kimseden yaş bilgisi
istemiyor, çünkü hiçbir kişisel veri toplamıyor.

## Değişiklikler

Bu politika değişirse bu sayfa güncellenir ve üstteki tarih değişir.

## İletişim

Sorular için: (BURAYA BİR E-POSTA ADRESİ YAZ)
