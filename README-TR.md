# shtcrop

shtcrop, videolardaki siyah, beyaz veya bulanık kenarlıkları algılayan ve kırpan, ardından düzenlenmiş videoyu yeniden yükleyen bir Telegram botudur.


## Özellikler
- **Kenarlık Algılama**: Siyah, beyaz veya bulanık kenarları tespit eder.
- **Video Kırpma**: İstenmeyen kenarları videodan kaldırır.
- **Telegram Entegrasyonu**: Videoları doğrudan Telegram üzerinden işleyip tekrar yükler.
- **Çoklu Mod**: Siyah, beyaz ve bulanık (deneysel) kenarlıkları destekler.


## Kurulum

1. **Venv Oluşturma ve Bağımlılık Yükleme**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Ortam Değişkenlerini Ayarlama**:
   ```
   mv env.example .env
   ```

3. **Botu Çalıştırma**:
   ```bash
   python cropper.py
   ```


## Kullanım

Bot'a Telegram üzerinden bir video gönderin. Bot, videoyu otomatik olarak işleyip kırpılmış sürümünü yeniden yükleyecektir.


## Lisans
Bu proje [GNU Affero General Public License v3.0](https://www.gnu.org/licenses/agpl-3.0.html) ile lisanslanmıştır.
