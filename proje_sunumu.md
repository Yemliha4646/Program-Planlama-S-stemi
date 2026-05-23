# Program Planlama Sistemi: Proje Yapısı ve Mimari Sunumu

Bu sunum, projenin dizin yapısını, kullanılan teknolojileri, dosya işlevlerini ve mimari tasarımı detaylı bir şekilde açıklamaktadır. Aşağıdaki interaktif slayt gösterisini kullanarak projeyi adım adım inceleyebilirsiniz.

````carousel
### 📊 Slayt 1: Giriş ve Proje Özeti

**Program Planlama Sistemi**, öğrencilerin sınav tarihlerine göre günlük kart çalışma hedeflerini dinamik olarak planlayan ve **Leitner Sistemi (Spaced Repetition)** kullanarak öğrenmeyi pekiştiren bir web uygulamasıdır.

#### 🛠️ Teknolojik Altyapı
*   **Backend:** Python, FastAPI (Yüksek performanslı, asenkron ve otomatik Swagger dokümantasyonlu web framework)
*   **Veritabanı:** SQLite & SQLAlchemy 2.0 (ORM)
*   **Yapay Zekâ (AI):** Groq API (Llama 3.3 70B modeli ile otomatik flashcard üretimi)
*   **Frontend:** Vanilla HTML5, CSS3, JavaScript ve modern arayüz tasarımı için Tailwind CSS
*   **Test:** Pytest ve in-memory SQLite veritabanı

#### 📁 Ana Dizin Yapısı
```text
📁 Program-Planlama-Sistemi
├── 📁 app              # Backend uygulama kodları (Clean Architecture katmanları)
├── 📁 static           # Önyüz (Frontend) dosyaları (HTML, JS, CSS)
├── 📁 tests            # Birim ve entegrasyon testleri
├── 📄 main.py          # FastAPI uygulama giriş noktası
├── 📄 requirements.txt # Python bağımlılıkları listesi
└── 📄 pyproject.toml   # Test ve araç konfigürasyonları
```

<!-- slide -->
### 🏛️ Slayt 2: Clean Architecture (Temiz Mimari) Yaklaşımı

Proje, bağımlılıkların yönünü kontrol altında tutarak test edilebilirliği ve sürdürülebilirliği artıran **Clean Architecture (Temiz Mimari)** prensibine göre tasarlanmıştır.

```mermaid
graph TD
    subgraph Sunum ve Dış Katmanlar (Dış Çember)
        Presenters[app/presenters - Routerlar ve Şemalar]
        Infrastructure[app/infrastructure - Veritabanı ve Repolar]
        Services[app/services - Groq AI Servisi]
    end
    subgraph Uygulama Mantığı (Orta Çember)
        UseCases[app/use_cases - İş Mantığı Servisleri]
    end
    subgraph Çekirdek Domain (Merkez)
        Domain[app/domain - Modeller ve Enumlar]
    end

    Presenters --> UseCases
    Infrastructure --> UseCases
    Services --> UseCases
    UseCases --> Domain
```

#### 🔄 Bağımlılık Kuralı (Dependency Rule)
Tüm bağımlılıklar dışarıdan içeriye doğrudur. İş mantığı (`use_cases`) ve veri modelleri (`domain`), veritabanı teknolojisinden veya web framework'ünden bağımsızdır.

<!-- slide -->
### 🎯 Slayt 3: Domain Katmanı (`app/domain/`)

Uygulamanın çekirdek iş kurallarını ve veri modellerini barındıran en iç katmandır. Hiçbir dış kütüphaneye veya veritabanı bağlantısına bağımlı değildir.

#### 📁 Dosyalar ve İşlevleri:
*   [models.py](file:///c:/Users/karak/Desktop/Program-Planlama-S-1stemi%20-%20Kopya/app/domain/models.py): Domain modellerini içerir.
    *   **Exam (Aggregate Root):** Sınavı temsil eder. Ders adı ve sınav tarihi bilgilerini tutar. Kendisine bağlı flashcard'ların yaşam döngüsünü kontrol eder.
    *   **Flashcard (Entity):** Çalışma kartını temsil eder. Bir soru (FrontSide), bir cevap (BackSide) ve bir kutu aşaması (Status) içerir.
    *   **StudySession (Value Object):** Günlük çalışma istatistiklerini dinamik hesaplayan kimliksiz bir değer nesnesidir.
*   [enums.py](file:///c:/Users/karak/Desktop/Program-Planlama-S-1stemi%20-%20Kopya/app/enums.py): Kartların Leitner kutu durumlarını tanımlar.
    *   `Box1` (Her gün çalışılacak), `Box2` (2 günde bir), `Box3` (5 günde bir) ve `Mastered` (Öğrenildi).

<!-- slide -->
### ⚙️ Slayt 4: Use Cases (İş Mantığı) & Services Katmanı

Domain kurallarını uygulayan ve dış servislerle haberleşen katmanlardır.

#### 📁 `app/use_cases/` Dizin Dosyaları:
*   [exam_service.py](file:///c:/Users/karak/Desktop/Program-Planlama-S-1stemi%20-%20Kopya/app/use_cases/exam_service.py):
    *   Sınav oluşturma ve silme kurallarını yönetir.
    *   `build_study_session()` metoduyla dinamik günlük çalışma hedefini hesaplar:
        $$\text{Günlük Hedef} = \lceil \frac{\text{Aktif Kart Sayısı}}{\text{Sınava Kalan Gün}} \rceil$$
*   [flashcard_service.py](file:///c:/Users/karak/Desktop/Program-Planlama-S-1stemi%20-%20Kopya/app/use_cases/flashcard_service.py):
    *   Kart oluşturma/silme ve Leitner kutu geçiş mantığını uygular.
    *   Kart bilinirse kutu atlar (`Box1 -> Box2 -> Box3 -> Mastered`), bilinmezse her zaman `Box1`'e sıfırlanır.

#### 📁 `app/services/` Dizin Dosyaları:
*   [ai_service.py](file:///c:/Users/karak/Desktop/Program-Planlama-S-1stemi%20-%20Kopya/app/services/ai_service.py): Groq API aracılığıyla Llama modeline bağlanarak girilen derse ait popüler 3 teknik soru-cevap çiftini JSON formatında asenkron olarak üretir. API anahtarı yoksa otomatik olarak "Demo modu" ile yerel şablon kartlar döner.

<!-- slide -->
### 🔌 Slayt 5: Presenters Katmanı (`app/presenters/`)

Uygulamanın HTTP API uç noktalarını (endpoints) ve veri doğrulama şemalarını barındıran katmandır.

#### 📁 Dosyalar ve İşlevleri:
*   [exam_router.py](file:///c:/Users/karak/Desktop/Program-Planlama-S-1stemi%20-%20Kopya/app/presenters/exam_router.py): Sınav işlemlerini yürüten API uç noktalarını barındırır.
    *   `POST /api/exams/` - Sınav oluşturma
    *   `GET /api/exams/` - Sınavları ve çalışma metriklerini listeleme
    *   `PATCH /api/exams/{id}` - Sınav tarihini güncelleme
    *   `POST /api/exams/{id}/generate-ai-cards` - Groq AI ile otomatik kart üretme
*   [flashcard_router.py](file:///c:/Users/karak/Desktop/Program-Planlama-S-1stemi%20-%20Kopya/app/presenters/flashcard_router.py): Kart ve Leitner işlemleri API uç noktaları.
    *   `POST /api/flashcards/` - El ile kart ekleme
    *   `PATCH /api/flashcards/{id}/leitner` - Bildim/Bilemedim durum güncellemesi
    *   `DELETE /api/flashcards/{id}` - Kartı silme
*   [schemas.py](file:///c:/Users/karak/Desktop/Program-Planlama-S-1stemi%20-%20Kopya/app/presenters/schemas.py): API istek ve yanıtlarının yapısını belirleyen ve Pydantic kütüphanesini kullanan doğrulama (validation) modelleridir.

<!-- slide -->
### 💾 Slayt 6: Infrastructure & Core Katmanları

Sistemin çalışması için gerekli teknik detayları, veritabanı bağlantılarını ve konfigürasyonları sağlar.

#### 📁 `app/infrastructure/` (Veri Erişim Katmanı)
*   [database.py](file:///c:/Users/karak/Desktop/Program-Planlama-S-1stemi%20-%20Kopya/app/infrastructure/database.py): Veritabanı tablolarını otomatik oluşturan `init_db()` metodunu barındırır.
*   [repositories.py](file:///c:/Users/karak/Desktop/Program-Planlama-S-1stemi%20-%20Kopya/app/infrastructure/repositories.py): SQL sorgularını iş katmanından soyutlayan **Repository Pattern** uygulanmıştır.
    *   `ExamRepository` ve `FlashcardRepository` sınıfları doğrudan SQLAlchemy oturumu (Session) kullanarak veri okuma ve yazma işlemlerini gerçekleştirir.

#### 📁 `app/core/` (Çekirdek Yapılandırma)
*   [config.py](file:///c:/Users/karak/Desktop/Program-Planlama-S-1stemi%20-%20Kopya/app/core/config.py): SQLite veritabanı bağlantısını (`DATABASE_URL`), SQLAlchemy Engine yapısını ve oturum havuzunu (`SessionLocal`) oluşturur. Bağımlılık enjeksiyonu için `get_db()` üreticisini sunar.

<!-- slide -->
### 💻 Slayt 7: Frontend (Önyüz) Katmanı (`static/`)

Kullanıcının etkileşime girdiği modern, tek sayfalık web uygulaması (SPA) arayüzüdür.

#### 📁 Dosyalar ve İşlevleri:
*   [index.html](file:///c:/Users/karak/Desktop/Program-Planlama-S-1stemi%20-%20Kopya/static/index.html): Uygulamanın görsel iskeletidir. Tailwind CSS yardımıyla responsive (mobil uyumlu) tasarlanmıştır. Sınav listesi paneli, kart ekleme modalları ve Leitner çalışma ekranı bu dosyada yer alır.
*   [app.js](file:///c:/Users/karak/Desktop/Program-Planlama-S-1stemi%20-%20Kopya/static/app.js): Tüm dinamik kullanıcı etkileşimlerini yönetir.
    *   FastAPI endpoints'lerine asenkron HTTP (Fetch API) istekleri atar.
    *   Flashcard'ların dönme animasyonunu (flip effect) CSS class'ları aracılığıyla sağlar.
    *   Kullanıcı "Bildim" veya "Bilemedim" dediğinde arayüzü anlık günceller.

<!-- slide -->
### 🧪 Slayt 8: Test Katmanı (`tests/`)

Uygulamanın doğru çalıştığını doğrulamak amacıyla yazılmış birim (unit) ve entegrasyon testlerini barındırır.

#### 📁 Dosyalar ve İşlevleri:
*   [conftest.py](file:///c:/Users/karak/Desktop/Program-Planlama-S-1stemi%20-%20Kopya/tests/conftest.py): Testlerin izole çalışabilmesi için geçici bir **in-memory (bellek içi) SQLite** veritabanı motoru (`memory_engine`) oluşturur ve FastAPI bağımlılıklarını bu test veritabanına yönlendirir.
*   [test_exams.py](file:///c:/Users/karak/Desktop/Program-Planlama-S-1stemi%20-%20Kopya/tests/test_exams.py) & [test_flashcards.py](file:///c:/Users/karak/Desktop/Program-Planlama-S-1stemi%20-%20Kopya/tests/test_flashcards.py): İş mantığı katmanındaki (use cases) kuralları test eder.
*   [test_api_exams.py](file:///c:/Users/karak/Desktop/Program-Planlama-S-1stemi%20-%20Kopya/tests/test_api_exams.py) & [test_api_flashcards.py](file:///c:/Users/karak/Desktop/Program-Planlama-S-1stemi%20-%20Kopya/tests/test_api_flashcards.py): HTTP API rotalarının girdi doğrulamalarını ve çıktılarının doğruluğunu test eder.
*   [test_ai_service.py](file:///c:/Users/karak/Desktop/Program-Planlama-S-1stemi%20-%20Kopya/tests/test_ai_service.py): AI servisi bağımlılığını taklit (mock) ederek test eder.
````
