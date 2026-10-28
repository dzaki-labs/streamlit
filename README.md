# Bike Sharing Performance & Behavior Analysis Dashboard 🚲✨

## 📝 Deskripsi
Proyek ini merupakan hasil analisis data eksploratif (EDA) pada dataset **Bike Sharing** untuk memahami pola dan perilaku penyewaan sepeda. Fokus utama analisis ini menjawab dua pertanyaan bisnis utama mengenai dinamika tipe pengguna (**Casual vs Registered**) berdasarkan tipe hari, serta pengaruh faktor iklim (**Musim dan Suhu udara**), dilanjutkan dengan analisis lanjutan menggunakan teknik **Binning (Manual Grouping)** untuk mengelompokkan tingkat permintaan harian (*Demand Level*).

---

## 📊 Fitur Utama Dashboard
- **Metrik Utama (KPIs):** Menampilkan akumulasi total penyewaan harian, total pengguna terdaftar (*Registered*), dan pengguna kasual (*Casual*).
- **Analisis Perilaku Pengguna:** Visualisasi perbandingan rata-rata penyewaan antara pengguna *Registered* dan *Casual* pada Hari Kerja (*Workingday*) vs Hari Libur (*Weekend/Holiday*).
- **Analisis Faktor Musim & Suhu:** 
  - Visualisasi rata-rata volume penyewaan harian berdasarkan musim (*Spring, Summer, Fall, Winter*).
  - *Scatter plot* korelasi suhu udara (*temp*) terhadap total penyewaan sepeda.
- **Analisis Lanjutan (Binning Demand):** Pengelompokan frekuensi hari berdasarkan kategori permintaan (*Low Demand, Medium Demand, High Demand*).
- **Filter Interaktif:** Pengguna dapat memfilter rentang tanggal, musim (*Season*), dan kondisi cuaca (*Weather*) secara fleksibel di *sidebar*.

---

## 📂 Struktur Proyek
```text
Submition Fundamental Analisis/
├── dashboard/
│   ├── dashboard.py        # Script utama Streamlit Dashboard
│   └── main_data.csv       # Dataset bersih hasil Data Wrangling & Cleaning
├── data/                   # Folder dataset mentah (raw data)
│   ├── day.csv             # Dataset harian
│   └── hour.csv            # Dataset per jam
├── notebook.ipynb          # Notebook Jupyter untuk Wrangling, EDA, & Visualisasi
├── requirements.txt        # Daftar library/dependencies Python
├── README.md               # Dokumentasi proyek
└── url.txt                 # Tautan (URL) deployment Streamlit Cloud

## 🛠️ Setup Environment & Menjalankan Dashboard

# 1. Masuk ke direktori proyek
cd "Submition Fundamental Analisis"

# 2. Buat virtual environment
python -m venv venv

# 3. Aktifkan virtual environment
# Untuk Windows (PowerShell):
.\venv\Scripts\activate
# Untuk macOS / Linux:
source venv/bin/activate

# 4. Install seluruh library yang dibutuhkan
pip install -r requirements.txt

## Menjalankan Dashboard Streamlit
```
streamlit run dashboard/dashboard.py
```