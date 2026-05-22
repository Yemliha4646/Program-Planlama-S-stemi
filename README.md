# 📚 Program Planlama Sistemi (FastAPI & Leitner Flashcard)

**Program Planlama Sistemi**, üniversite öğrencilerinin yoğun sınav dönemlerini daha verimli, planlı ve bilimsel yöntemlerle yönetebilmeleri için geliştirilmiş, **Yapay Zeka (AI) destekli** bir akademik asistan ve akıllı öğrenme platformudur.

Proje, modern yazılım mühendisliği standartlarına uygun olarak **Clean Architecture (Temiz Mimari)** prensipleriyle yapılandırılmış olup; güçlü bir FastAPI backend mimarisini, Tailwind CSS ile güçlendirilmiş kullanıcı dostu ve akıcı bir frontend arayüzüyle birleştirir.

---

## 🎯 Projenin Amacı ve Çözdüğü Problemler

Geleneksel sınav hazırlık süreçlerinde öğrenciler iki büyük problemle karşılaşırlar: **"Sınava kadar günde kaç soru/kart çalışmalıyım?"** belirsizliği ve **"Öğrenilen bilgilerin hızla unutulması"**. Bu sistem, geliştirdiği iki temel mekanizmayla bu problemlere çözüm üretir:

1. **Dinamik Günlük Hedef Algoritması:** Sistem, sınav tarihine kalan gün sayısını ve o derse ait toplam çalışma kartı (flashcard) miktarını anlık olarak analiz eder. Sınav yaklaştıkça veya kart sayısı arttıkça günlük çalışma hedefini otomatik olarak yeniden hesaplayarak öğrenciye dengeli bir yol haritası sunur.
2. **Leitner Hafıza Sistemi:** Kalıcı öğrenmeyi sağlamak amacıyla, tıp ve dil eğitiminde sıklıkla kullanılan bilimsel *Aralıklı Tekrar (Spaced Repetition)* metodunu dijitalleştirir. Öğrenci kartları bildikçe kartlar uzun süreli hafıza kutularına taşınır; bilemedikçe tekrar edilmek üzere ilk kutuya geri döner.

---

## 🚀 Temel Modüller ve Yetenekler

Platform, öğrencilerin tüm çalışma ekosistemini tek bir ekrandan yönetebileceği modüllerden oluşur:

### 📅 Sınav ve Müfredat Yönetimi
* Sınav başlıkları, ders adları ve sınav tarihlerinin kolayca sisteme kaydedilmesi, güncellenmesi veya silinmesi.
* Sınavlara kalan sürelerin ve ders bazlı ilerleme istatistiklerinin görsel takibi.

### 🧠 Akıllı Flashcard (Leitner) Sistemi
* Her ders için özel Ön Yüz (Soru) ve Arka Yüz (Cevap) içeren çalışma kartlarının manuel olarak oluşturulması.
* Kartların öğrenilme durumlarına göre 4 farklı aşamada takibi:
    * **Kutu 1 (Yeni / Zorlanılanlar):** Her gün tekrar edilmesi gereken, henüz taze veya sıkça unutulan bilgiler.
    * **Kutu 2 & Kutu 3 (Orta Seviye):** Belirli aralıklarla hatırlatılan, kalıcı hafızaya geçiş aşamasındaki bilgiler.
    * **Mastered (Öğrenilenler):** Tamamen hafızaya alınmış, sınavda başarı oranı kesinleşmiş olgun bilgiler.

### 🤖 Gemini 1.5 Flash ile Yapay Zeka Entegrasyonu
* Öğrencilerin manuel kart hazırlama yükünü azaltmak amacıyla tek tıkla **AI Destekli Soru Üretimi**.
* Sistem, ders adını alarak arka planda Google Gemini API mimarisiyle konuşur ve o konuya ait en popüler akademik teknik soruları otomatik olarak üreterek doğrudan öğrencinin havuzuna ekler.
* **Çift Modlu Çalışma Altyapısı:** API anahtarı kısıtlamaları veya çevrimdışı sunum senaryoları için dahili **Demo Modu** barındırır. Demo modu açıkken sistem yerel kütüphaneden anında kararlı örnek teknik sorular besleyerek kesintisiz bir deneyim sunar.

---

## 🏗️ Mimari Tasarım ve Teknoloji Yığını

Proje, kodun sürdürülebilir, test edilebilir ve genişletilebilir olması amacıyla katmanlı mimari (Clean Architecture) standartlarında yazılmıştır. İş mantığı (Domain), veri erişimi (Infrastructure) ve sunum (Presenter) katmanları birbirinden tamamen izoledir.

### 🛠️ Kullanılan Teknolojiler

| Katman | Teknoloji | Görevi / Rolü |
| :--- | :--- | :--- |
| **Backend Framework** | `FastAPI (Python)` | Yüksek performanslı, asenkron ve tip güvenli RESTful API altyapısı. |
| **Yapay Zeka (AI)** | `Google Gemini 1.5 Flash` | Ders adlarına uygun yapılandırılmış JSON formatında teknik soru üretimi. |
| **Veri Tabanı & ORM** | `SQLite 3` & `SQLAlchemy` | Hafif, sunucusuz ilişkisel veritabanı yönetimi ve model haritalama. |
| **Veri Doğrulama** | `Pydantic v2` | Girdi ve çıktı verilerinin çalışma zamanında (runtime) katı şema kontrolü. |
| **Arayüz (Frontend)** | `Tailwind CSS` & `Vanilla JS` | Responsive (mobil uyumlu), tek sayfa (SPA) mimarisi ve 3D flip animasyonları. |
| **Test Standartları** | `Pytest` | İş mantığının ve API uç noktalarının doğrulanması için otomatik birim testleri. |

---

## 🔒 Güvenlik ve Geliştirme Standartları

* **API Anahtarı Güvenliği:** Projede `.env` ortam değişkenleri yapısı kullanılarak API anahtarları kaynak koddan tamamen soyutlanmıştır. Gelişmiş `.gitignore` konfigürasyonu sayesinde kritik kimlik bilgileri asla uzak Git depolarına (GitHub vb.) sızdırılmaz.
* **Hafif ve Taşınabilir Yapı:** Proje SQLite kullandığı için harici bir veritabanı sunucusu kurulumu gerektirmez; klonlandığı andan itibaren sanal ortam (`.venv`) üzerinden saniyeler içinde ayağa kalkacak esnekliktedir.