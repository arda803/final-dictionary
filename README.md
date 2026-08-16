# Sözlük — Offline Desktop Dictionary 📚

Python ve PyQt6 kullanılarak geliştirilmiş, çevrimdışı çalışan masaüstü sözlük ve kelime öğrenme uygulaması.

## ✨ Özellikler

- 🔍 **Kelime Arama:** Kelime, anlam ve örnek cümleler içinde hızlı arama
- 🔊 **Sesli Telaffuz (TTS):** Kelime ve çevirileri dinleme
- 💾 **Ses Önbelleği:** Daha önce oluşturulan seslerin `audio_cache/` klasöründe saklanması
- ⭐ **Favoriler:** Sık kullanılan veya öğrenilmek istenen kelimeleri favorilere ekleme
- 📊 **Öğrenme Durumu:** `Öğrenilmedi`, `Öğreniliyor` ve `Öğrenildi` durumlarını takip etme
- 🎯 **Kelime Quiz:** Kelime bilgilerini test etmek için etkileşimli quiz modu
- 📖 **Günün Kelimesi:** Sözlükteki kelimeler arasından günlük kelime gösterimi
- 🌙 **Açık / Koyu Tema:** Kullanıcı tercihine göre tema değiştirme
- 📋 **Panoya Kopyalama:** Kelime ve çevirileri hızlıca kopyalama
- 📂 **İçe / Dışa Aktarma:** JSON, Excel ve TXT formatlarıyla veri aktarımı
- ⌨️ **Klavye Kısayolları:** Sık kullanılan özelliklere hızlı erişim

## 🌍 Dil Desteği

| Dil Çifti | Kaynak Dil | Hedef Dil |
|---|---|---|
| `ru-tr` | Rusça | Türkçe |
| `tr-ru` | Türkçe | Rusça |
| `en-tr` | İngilizce | Türkçe |
| `tr-en` | Türkçe | İngilizce |


## 🛠️ Kullanılan Teknolojiler

- Python
- PyQt6
- SQLite
- Edge-TTS
- openpyxl

## 🚀 Kurulum

Repository'yi klonlayın:

```bash
git clone https://github.com/arda803/final-dictionary.git
cd final-dictionary
```

Gerekli bağımlılıkları yükleyin:

```bash
pip install -r requirements.txt
```

## ▶️ Çalıştırma

```bash
python main.py
```

## ⌨️ Klavye Kısayolları

| Kısayol | İşlem |
|---|---|
| `Ctrl + N` | Yeni kelime ekle |
| `Ctrl + F` | Arama kutusuna odaklan |
| `Ctrl + Q` | Kelime quizini aç |
| `Ctrl + ,` | Ayarları aç |
| `Ctrl + W` | Uygulamayı kapat |
| `Delete` | Seçili kelimeyi sil |
| `F5` | Listeyi yenile |

## 🔊 TTS (Seslendirme)

Sesli telaffuz sistemi Edge-TTS kullanır.

Bir kelimenin sesi ilk kez oluşturulurken internet bağlantısı gerekebilir. Oluşturulan ses dosyaları `audio_cache/` klasöründe önbelleğe alınır. Böylece daha önce oluşturulmuş sesler tekrar kullanılabilir.

## 💾 Veri Yönetimi

Uygulama SQLite tabanlı bir veritabanı kullanır.

Kelime kayıtlarında aşağıdaki bilgiler tutulabilir:

- Kelime
- Dil çifti
- Çeviri / anlam
- Sözcük türü
- Örnek cümle
- Öğrenme durumu
- Favori durumu

Veriler JSON, Excel ve TXT formatlarında içe veya dışa aktarılabilir.

## 🎯 Projenin Amacı

Sözlük yalnızca kelime aramak için değil, kelime öğrenme sürecini daha düzenli hale getirmek amacıyla geliştirilmiştir.

Arama, sesli telaffuz, favoriler, öğrenme durumu ve quiz gibi özelliklerin tek bir masaüstü uygulamasında bir araya getirilmesi hedeflenmektedir.

## 🔮 Geliştirme

Proje aktif olarak geliştirilmektedir. Mevcut özelliklerin iyileştirilmesi, kullanıcı deneyiminin geliştirilmesi ve yeni kelime öğrenme özelliklerinin eklenmesi planlanmaktadır.

## 📌 Proje Durumu

**Development / Open Source**

Proje geliştirme aşamasındadır ve bazı özellikler ilerleyen sürümlerde değişebilir.

## 🔗 Bağlantılar

**GitHub:**  
https://github.com/arda803/final-dictionary

**Issues:**  
https://github.com/arda803/final-dictionary/issues

**LinkedIn:**  
https://www.linkedin.com/in/arda-talha-tekinel-882176351/

**YouTube:**  
https://www.youtube.com/@kedilercoksel314

## 👨‍💻 Geliştirici

**Arda Talha Tekinel**

Python • PyQt6 • Desktop Application Development

> Sözlük — kelimeleri bulmanın, dinlemenin ve öğrenmenin daha düzenli bir yolu.
