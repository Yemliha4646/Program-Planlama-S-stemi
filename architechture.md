# Mimari Doküman

Projenin mimari özellikleri aşağıdaki gibidir.

## Backend

Backend tarafı aşağıdaki teknolojileri kullanır.

| Konu | Teknoloji | Açıklama |
| :--- | :--- | :--- |
| Backend Mimarisi | Clean Architecture | Backend uygulamasında katmanlı, bağımsız test edilebilir Clean Architecture yaklaşımı kullanılır. |
| Framework | FastAPI | Performans, hızlı geliştirme süresi ve otomatik dokümantasyon (Swagger/ReDoc) desteği nedeniyle tercih edilmiştir. |
| Programlama Dili | Python | Veri işleme kolaylığı ve zengin kütüphane ekosistemi için kullanılmıştır. |
| Veritabanı | SQLite / PostgreSQL | İlişkisel veri modeli, sınav ve kart ilişkilerini ACID standartlarında tutmak için tercih edilmiştir. |
| Planlama Algoritması | Zaman ve Miktar Bazlı Optimizasyon | `Günlük Kart Hedefi = Toplam Kart Sayısı / Sınava Kalan Gün Sayısı` formülüyle dinamik planlama yapar. |
| Öğrenme Metodu | Leitner Sistemi (Spaced Repetition) | "Bildim / Bilemedim" geri bildirimine dayalı, aralıklı tekrar mantığına sahip basit algoritma. |

Mutlaka uyulması gereken prensipler:
- **SOLID ilkeleri:** Özellikle Tek Sorumluluk (SRP) ve Bağımlılıkların Tersine Çevrilmesi (DIP) prensipleri katmanlar arası geçişte zorunludur.
- **KISS (Keep It Simple, Stupid):** Projenin basitlik ve sürdürülebilirlik odağını korumak için karmaşık mimari yapılardan kaçınılır.

## FrontEnd

Önyüz uygulaması aşağıdaki gibidir.

- **Teknoloji:** HTML5, CSS3 ve Vanilla JavaScript üzerine inşa edilir.
- **Tasarım:** Modern, minimalist ve mobil uyumlu (Responsive) bir arayüz için **Tailwind CSS** kullanılır.
- **Kart Efektleri:** Flashcard döndürme animasyonları CSS `transform: rotateY()` ve `backface-visibility: hidden` özellikleri ile tarayıcı tabanlı olarak gerçekleştirilir.
- **İletişim:** Backend uygulaması ile asenkron (Fetch API) üzerinden REST API standartlarında haberleşir.

## API Tasarım Standartları

- **RESTful API:** Tüm kaynak yönetimi (Sınavlar ve Kartlar) standart HTTP metodları ile gerçekleştirilir.
- **Metod Standartları:** - Veri listeleme ve kalan gün hesaplama işlemleri için `HTTP GET`,
  - Yeni sınav veya kart oluşturma işlemleri için `HTTP POST`,
  - Kartların durum güncellemeleri ("Bildim/Bilemedim") ve sınav tarihi değişiklikleri için `HTTP PUT/PATCH`,
  - Sınav veya kart silme işlemleri için `HTTP DELETE` metodu kullanılır.
- **Hata Yönetimi:** Tüm API yanıtları standart HTTP durum kodları (200 OK, 201 Created, 400 Bad Request, 404 Not Found) ve anlamlı JSON hata mesajları döner.