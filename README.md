# Konya Yemek Dağıtım Optimizasyonu (ACO)

Karınca Kolonisi Optimizasyonu (Ant Colony Optimization — ACO) kullanarak Konya'daki bir yemek merkezinden 20 farklı KYK öğrenci yurduna yemek dağıtımı için en kısa kapalı rotayı hesaplayan interaktif Streamlit uygulaması.

## Özellikler

- **Gerçek Konum Verisi:** Google Maps Geocoding API aracılığıyla `data/locations.py` içindeki merkez ve 20 KYK yurdunun koordinatlarını çözer.
- **Mesafe Matrisi:** Koordinatlar üzerinden Haversine formülüyle kuş uçuşu mesafe matrisi üretir.
- **ACO Rota Optimizasyonu:** `core/aco.py` içindeki `AntColonyOptimizer` sınıfı ile karınca sayısı, iterasyon ve feromon buharlaşması parametrelerine göre en kısa turu bulur.
- **İnteraktif Harita & Grafik:** PyDeck katmanları (`ScatterplotLayer`, `TextLayer`, `LineLayer`) ile rotayı haritada çizer ve iterasyon bazlı yakınsama grafiğini gösterir.

## Proje Yapısı

```text
konya-aco-optimization/
├── main.py                  # Streamlit arayüzü ve PyDeck görselleştirmesi
├── core/
│   ├── aco.py               # Karınca Kolonisi Optimizasyonu (ACO) motoru
│   └── google_maps.py       # Geocoding API ve Haversine mesafe matrisi
├── data/
│   └── locations.py         # Merkez ve 20 KYK yurdu lokasyon listesi
├── tests/
│   └── test_aco.py          # ACO motoru birim testleri
├── .env.example             # Ortam değişkeni şablonu
└── requirements.txt
```

## Kurulum ve Çalıştırma

1. Depoyu klonlayın ve bağımlılıkları yükleyin:
   ```bash
   git clone https://github.com/yyigituncu/konya-aco-optimization.git
   cd konya-aco-optimization
   python -m venv .venv
   # Windows: .venv\Scripts\activate | Linux/macOS: source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Ortam değişkenini tanımlayın:
   ```bash
   cp .env.example .env
   ```
   `.env` dosyası içine kendi Google Maps Geocoding API anahtarınızı ekleyin:
   ```env
   GOOGLE_API_KEY=your_google_maps_api_key_here
   ```

3. Uygulamayı başlatın:
   ```bash
   streamlit run main.py
   ```

## Testler

```bash
python -m unittest discover -s tests -v
```

## Lisans

Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır.
