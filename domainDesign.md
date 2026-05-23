# Domain Design

Projede yer alan aktörlere ait domain kurgusu aşağıda özetlenmiştir.

## Exam *(Aggregate Root)*

Öğrencinin takip ettiği sınavı ve bu sınava ait genel planlama metriklerini temsil eden ana kök nesnedir (Aggregate Root). Bünyesinde birden fazla Flashcard barındırır. Sınav silindiğinde ona bağlı kartlar da silinir *(Cascade Delete)*.

|Field|Type|Açıklama|Örnek|Kural|
|----|----|---------|-----|-----|
|ExamId|Guid/UUID|Unique/Identity alanıdır|7c9e6679-7425-40de-944b-e07fc1f90ae7|Tekrar etmemelidir, benzersiz olmalıdır.|
|CourseName|Text|Sınavın ait olduğu dersin adıdır|Veri Tabanı Yönetim Sistemleri|Boş geçilemez, maksimum 100 karakter olmalıdır.|
|ExamDate|Date|Sınavın gerçekleşeceği tarihtir|2026-06-25|Geçmiş bir tarih girilemez, bugünden ileri bir tarih olmalıdır.|

## Flashcard *(Entity)*

Bir sınava ait çalışma kartını temsil eden nesnedir. Her kart sadece bir Exam nesnesine bağlı olabilir aralarında bire-çok *(one-to-many)* ilişki vardır.

|Field|Type|Açıklama|Örnek|Kural|
|----|----|---------|-----|-----|
|CardId|Guid/UUID|Unique/Identity alanıdır|a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d|Tekrar etmemelidir, benzersiz olmalıdır.|
|ExamId|Guid/UUID|İlişkili olduğu Exam nesnesinin Id değeridir|7c9e6679-7425-40de-944b-e07fc1f90ae7|Veritabanında mevcut ve geçerli bir ExamId olmalıdır.|
|FrontSide|Text|Kartın ön yüzündeki soru, terim veya kavramdır|SQL nedir?|Boş geçilemez, maksimum 500 karakter.|
|BackSide|Text|Kartın arka yüzündeki cevap veya açıklamadır|Verileri yönetmek için kullanılan sorgu dilidir.|Boş geçilemez, maksimum 2000 karakter.|
|Status|[LeitnerBox](#leitnerbox-enum)|Kartın mevcut öğrenme/tekrar aşamasını belirtir|Box1|Varsayılan değer `Box1` (Yeni eklenen kart) olarak başlar.|

## StudySession *(Value Object)*

Öğrencinin günlük çalışma durumunu, o gün hedeflenen kart sayısını ve ilerlemesini anlık hesaplayan, veritabanında tek başına bir kimliği (Identity) olmayan hesaplama nesnesidir.

|Field|Type|Açıklama|Örnek|Kural|
|----|----|---------|-----|-----|
|RemainingDays|Integer|Bugün ile sınav tarihi arasındaki kalan gün sayısıdır|10|Sınav tarihi geçildiyse 0 döner.|
|DailyTarget|Integer|O gün çalışılması gereken kart hedefidir|5|`Toplam Kart Sayısı / Kalan Gün Sayısı` formülü ile dinamik hesaplanır. Kalan gün 0 ise toplam kart sayısını döner.|
|CompletedToday|Integer|O gün içinde "Bildim" veya "Bilemedim" olarak işaretlenen kart sayısıdır|3|Pozitif tam sayı olmalıdır, DailyTarget değerini aşabilir.|

## LeitnerBox *(Enum)*

Aralıklı tekrar (Spaced Repetition) sistemindeki kart kutularını/durumlarını ifade eder. Kartın öğrenilme seviyesine göre geçiş yaptığı aşamalardır.

- **Box1:** Henüz öğrenilmemiş / Yeni eklenmiş kartlar (Her gün gösterilir).
- **Box2:** Az öğrenilmiş kartlar (2 günde bir gösterilir).
- **Box3:** Orta seviyede öğrenilmiş kartlar (5 günde bir gösterilir).
- **Mastered:** Tamamen öğrenilmiş kartlar (Sınav gününe kadar havuzdan çıkarılır).
