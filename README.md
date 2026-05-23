# 📚 Program Planlama Sistemi (FastAPI & Leitner Flashcard)

**Program Planlama Sistemi**, üniversite öğrencilerinin yoğun sınav dönemlerini daha verimli, planlı ve bilimsel yöntemlerle yönetebilmeleri için geliştirilmiş, **Yapay Zeka (AI) destekli** bir akademik asistan ve akıllı öğrenme platformudur.

Proje, modern yazılım mühendisliği standartlarına uygun olarak **Clean Architecture (Temiz Mimari)** prensipleriyle yapılandırılmış olup; güçlü bir FastAPI backend mimarisini, Tailwind CSS ile güçlendirilmiş kullanıcı dostu ve akıcı bir frontend arayüzüyle birleştirir.

---

## 🎯 Projenin Amacı ve Çözdüğü Problemler

Geleneksel sınav hazırlık süreçlerinde öğrenciler iki büyük problemle karşılaşırlar: **"Sınava kadar günde kaç soru/kart çalışmalıyım?"** belirsizliği ve **"Öğrenilen bilgilerin hızla unutulması"**. Bu sistem, geliştirdiği iki temel mekanizmayla bu problemlere çözüm üretir:

1. **Dinamik Günlük Hedef Algoritması:** Sistem, sınav tarihine kalan gün sayısını ve o derse ait toplam çalışma kartı (flashcard) miktarını anlık olarak analiz eder. Sınav yaklaştıkça veya kart sayısı arttıkça günlük çalışma hedefini otomatik olarak yeniden hesaplayarak öğrenciye dengeli bir yol haritası sunar.
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

### 🤖 Groq (Llama 3.3 70B) ile Yapay Zeka Entegrasyonu
* Öğrencilerin manuel kart hazırlama yükünü azaltmak amacıyla tek tıkla **AI Destekli Soru Üretimi**.
* Sistem, ders adını alarak arka planda Groq API mimarisiyle konuşur ve o konuya ait en popüler akademik teknik soruları otomatik olarak üreterek doğrudan öğrencinin havuzuna ekler.
* **Çift Modlu Çalışma Altyapısı:** API anahtarı kısıtlamaları veya çevrimdışı sunum senaryoları için dahili **Demo Modu** barındırır. Demo modu açıkken sistem yerel kütüphaneden anında kararlı örnek teknik sorular besleyerek kesintisiz bir deneyim sunar.

---

## 🏗️ Mimari Tasarım ve Teknoloji Yığını

Proje, kodun sürdürülebilir, test edilebilir ve genişletilebilir olması amacıyla katmanlı mimari (Clean Architecture) standartlarında yazılmıştır. İş mantığı (Domain), veri erişimi (Infrastructure) ve sunum (Presenter) katmanları birbirinden tamamen izoledir.

### 🛠️ Kullanılan Teknolojiler

| Katman | Teknoloji | Görevi / Rolü |
| :--- | :--- | :--- |
| **Backend Framework** | `FastAPI (Python)` | Yüksek performanslı, asenkron ve tip güvenli RESTful API altyapısı. |
| **Yapay Zeka (AI)** | `Groq / Llama 3.3 70B Versatile` | Ders adlarına uygun yapılandırılmış JSON formatında teknik soru üretimi (Groq Cloud API üzerinden). |
| **Veri Tabanı & ORM** | `SQLite 3` & `SQLAlchemy` | Hafif, sunucusuz ilişkisel veritabanı yönetimi ve model haritalama. |
| **Veri Doğrulama** | `Pydantic v2` | Girdi ve çıktı verilerinin çalışma zamanında (runtime) katı şema kontrolü. |
| **Arayüz (Frontend)** | `Tailwind CSS` & `Vanilla JS` | Responsive (mobil uyumlu), tek sayfa (SPA) mimarisi ve 3D flip animasyonları. |
| **Test Standartları** | `Pytest` | İş mantığının ve API uç noktalarının doğrulanması için otomatik birim testleri. |

---

## 🔒 Güvenlik ve Geliştirme Standartları

* **API Anahtarı Güvenliği:** Projede `.env` ortam değişkenleri yapısı kullanılarak API anahtarları kaynak koddan tamamen soyutlanmıştır. Gelişmiş `.gitignore` konfigürasyonu sayesinde kritik kimlik bilgileri asla uzak Git depolarına (GitHub vb.) sızdırılmaz.
* **Hafif ve Taşınabilir Yapı:** Proje SQLite kullandığı için harici bir veritabanı sunucusu kurulumu gerektirmez; klonlandığı andan itibaren sanal ortam (`.venv`) üzerinden saniyeler içinde ayağa kalkacak esnekliktedir.

---

## 🚀 Hızlı Başlangıç (Kurulum)

```bash
# 1. Depoyu klonlayın
git clone https://github.com/<kullanici>/Program-Planlama-Sistemi.git
cd Program-Planlama-Sistemi

# 2. Sanal ortam oluşturun ve aktifleştirin
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS / Linux

# 3. Bağımlılıkları yükleyin
pip install -r requirements.txt

# 4. Ortam değişkenlerini yapılandırın
# .env dosyasını düzenleyerek GROQ_API_KEY değerinizi girin.
# Demo modunu açmak için: DEMO_MODE=true

# 5. Uygulamayı başlatın
uvicorn main:app --reload

# 6. Tarayıcıda açın
# http://127.0.0.1:8000
```

---

## 📡 API Endpoint Referansı

| Metod | Yol | Açıklama |
| :--- | :--- | :--- |
| `POST` | `/api/exams/` | Yeni sınav oluşturur |
| `GET` | `/api/exams/` | Tüm sınavları listeler |
| `GET` | `/api/exams/{exam_id}` | Belirli sınavı getirir |
| `PATCH` | `/api/exams/{exam_id}` | Sınav tarihini günceller |
| `DELETE` | `/api/exams/{exam_id}` | Sınavı ve kartlarını siler |
| `GET` | `/api/exams/{exam_id}/flashcards` | Sınava ait kartları listeler |
| `POST` | `/api/exams/{exam_id}/generate-ai-cards` | AI ile otomatik kart üretir |
| `POST` | `/api/flashcards/` | Manuel flashcard oluşturur |
| `PATCH` | `/api/flashcards/{card_id}/leitner` | Kart durumunu günceller (Bildim/Bilemedim) |
| `DELETE` | `/api/flashcards/{card_id}` | Flashcard'ı siler |

> 📝 Detaylı API dokümantasyonu uygulama çalışırken `/docs` (Swagger UI) veya `/redoc` adresinden erişilebilir.