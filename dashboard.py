import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# --- PAGE CONFIG ---
st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "main_data.csv")
    
    df = pd.read_csv(file_path)
    df["dteday"] = pd.to_datetime(df["dteday"])
    return df

main_df = load_data()

# --- SIDEBAR FILTER ---
with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")

    min_date = main_df["dteday"].min().date()
    max_date = main_df["dteday"].max().date()

    st.subheader("Filter Tanggal")

    start_date = st.date_input(
        "Tanggal Mulai",
        value=min_date,
        min_value=min_date,
        max_value=max_date
    )

    end_date = st.date_input(
        "Tanggal Akhir",
        value=max_date,
        min_value=min_date,
        max_value=max_date
    )

    if start_date > end_date:
        st.error("Tanggal mulai tidak boleh lebih besar dari tanggal akhir.")
        st.stop()

    st.subheader("Filter Tambahan")

    # Filter Musim (Season Label)
    season_options = main_df["season_label"].unique() if "season_label" in main_df.columns else main_df["season"].unique()
    season_filter = st.multiselect(
        "Musim (Season)",
        options=season_options,
        default=season_options
    )

    # Filter Kondisi Cuaca (Weather Label)
    weather_options = main_df["weather_label"].unique() if "weather_label" in main_df.columns else main_df["weathersit"].unique()
    weather_filter = st.multiselect(
        "Kondisi Cuaca",
        options=weather_options,
        default=weather_options
    )

# --- FILTER DATASET ---
season_col = "season_label" if "season_label" in main_df.columns else "season"
weather_col = "weather_label" if "weather_label" in main_df.columns else "weathersit"

filtered_df = main_df[
    (main_df["dteday"].dt.date >= start_date) &
    (main_df["dteday"].dt.date <= end_date) &
    (main_df[season_col].isin(season_filter)) &
    (main_df[weather_col].isin(weather_filter))
].copy()

# --- MAIN PAGE HEADER ---
st.header("Bike Sharing Performance & Behavior Dashboard 🚲")
st.markdown("Dashboard interaktif untuk menganalisis pola penyewaan sepeda berdasarkan tipe hari, faktor cuaca/musim, dan kategori tingkat permintaan.")

# --- METRICS ---
col1, col2, col3 = st.columns(3)

with col1:
    total_rentals = filtered_df["cnt"].sum() if not filtered_df.empty else 0
    st.metric("Total Penyewaan", f"{total_rentals:,}")

with col2:
    total_registered = filtered_df["registered"].sum() if not filtered_df.empty else 0
    st.metric("Total Penyewa Registered", f"{total_registered:,}")

with col3:
    total_casual = filtered_df["casual"].sum() if not filtered_df.empty else 0
    st.metric("Total Penyewa Casual", f"{total_casual:,}")

st.divider()

# --- VISUALISASI 1: PERILAKU PENGGUNA (PERTANYAAN 1) ---
st.subheader("1. Komposisi Pengguna: Registered vs Casual pada Hari Kerja & Libur")

if not filtered_df.empty:
    user_type_df = filtered_df.groupby('workingday')[['casual', 'registered']].mean().reset_index()
    user_type_df['workingday'] = user_type_df['workingday'].map({0: 'Hari Libur / Weekend', 1: 'Hari Kerja'})
    user_type_melted = user_type_df.melt(id_vars='workingday', var_name='Tipe Pengguna', value_name='Rata-Rata Penyewaan')

    fig1, ax1 = plt.subplots(figsize=(10, 5))
    sns.barplot(
        data=user_type_melted,
        x='workingday',
        y='Rata-Rata Penyewaan',
        hue='Tipe Pengguna',
        palette=['#FF7F0E', '#1F77B4'],
        ax=ax1
    )

    for p in ax1.patches:
        if p.get_height() > 0:
            ax1.annotate(f'{p.get_height():.0f}',
                        (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='bottom', fontsize=10, fontweight='bold',
                        xytext=(0, 3), textcoords='offset points')

    ax1.set_title("Rata-Rata Penyewaan Berdasarkan Tipe Hari dan Tipe Pengguna", fontsize=14)
    ax1.set_xlabel("Tipe Hari")
    ax1.set_ylabel("Rata-Rata Jumlah Penyewaan")
    ax1.grid(axis='y', linestyle='--', alpha=0.5)
    st.pyplot(fig1)
else:
    st.warning("Tidak ada data untuk rentang filter ini.")

with st.expander("Selengkapnya (Insight Perilaku Pengguna)"):
    st.write(
        """
        * **Pengguna Registered (Terdaftar):** Mendominasi secara signifikan pada hari kerja untuk kebutuhan perjalanan rutin/komputerisasi (berangkat dan pulang kerja).
        * **Pengguna Casual (Kasual):** Mengalami peningkatan proporsi yang tinggi pada hari libur / akhir pekan untuk tujuan rekreasi dan mobilitas santai.
        """
    )

# --- VISUALISASI 2 & 3: MUSIM DAN SUHU (PERTANYAAN 2) ---
st.subheader("2. Pengaruh Faktor Musim dan Suhu terhadap Volume Penyewaan")

col_a, col_b = st.columns(2)

with col_a:
    if not filtered_df.empty:
        fig2, ax2 = plt.subplots(figsize=(6, 4.5))
        sns.barplot(
            data=filtered_df,
            x=season_col,
            y='cnt',
            order=['Spring', 'Summer', 'Fall', 'Winter'] if season_col == 'season_label' else None,
            palette='Blues_d',
            ax=ax2,
            errorbar=None
        )
        for p in ax2.patches:
            if p.get_height() > 0:
                ax2.annotate(f'{p.get_height():.0f}', (p.get_x() + p.get_width() / 2., p.get_height()),
                            ha='center', va='bottom', fontsize=10, fontweight='bold',
                            xytext=(0, 3), textcoords='offset points')

        ax2.set_title("Rata-Rata Penyewaan per Musim", fontsize=12, fontweight='bold')
        ax2.set_xlabel("Musim")
        ax2.set_ylabel("Rata-Rata Penyewaan")
        ax2.grid(axis='y', linestyle='--', alpha=0.5)
        st.pyplot(fig2)

with col_b:
    if not filtered_df.empty:
        fig3, ax3 = plt.subplots(figsize=(6, 4.5))
        sns.scatterplot(
            data=filtered_df,
            x='temp',
            y='cnt',
            hue=season_col,
            palette='Set2',
            alpha=0.8,
            ax=ax3
        )
        sns.regplot(data=filtered_df, x='temp', y='cnt', scatter=False, color='red', ax=ax3)
        ax3.set_title("Hubungan Suhu (Temp) vs Total Penyewaan", fontsize=12, fontweight='bold')
        ax3.set_xlabel("Suhu (Normalized)")
        ax3.set_ylabel("Total Penyewaan Harian")
        ax3.grid(True, linestyle='--', alpha=0.5)
        st.pyplot(fig3)

with st.expander("Selengkapnya (Insight Musim & Suhu)"):
    st.write(
        """
        * **Pengaruh Musim:** Musim Gugur (*Fall*) dan Musim Panas (*Summer*) mencatatkan volume penyewaan tertinggi, sedangkan Musim Semi (*Spring*) paling rendah.
        * **Korelasi Suhu:** Terdapat hubungan linier positif kuat antara suhu udara (`temp`) dan total penyewaan, menandakan minat penggunaan sepeda meningkat pesat pada kondisi cuaca yang hangat.
        """
    )

# --- VISUALISASI 4: ADVANCED ANALYSIS (BINNING DEMAND CATEGORY) ---
st.subheader("3. Analisis Lanjutan: Distribusi Kategori Permintaan Sepeda (Manual Binning)")

if not filtered_df.empty:
    temp_df_bin = filtered_df.copy()
    max_val = temp_df_bin['cnt'].max() if temp_df_bin['cnt'].max() > 6000 else 10000
    bins = [0, 3000, 6000, max_val]
    labels_bin = ['Low Demand', 'Medium Demand', 'High Demand']
    
    temp_df_bin['demand_category'] = pd.cut(temp_df_bin['cnt'], bins=bins, labels=labels_bin)

    fig4, ax4 = plt.subplots(figsize=(10, 5))
    ax_bar = sns.countplot(
        data=temp_df_bin,
        x='demand_category',
        palette=['#72B4EB', '#2B5C8F', '#0D2B45'],
        order=['Low Demand', 'Medium Demand', 'High Demand'],
        ax=ax4
    )

    for p in ax_bar.patches:
        if p.get_height() > 0:
            ax4.annotate(f'{int(p.get_height())} hari',
                        (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='bottom', fontsize=11, fontweight='bold',
                        xytext=(0, 5), textcoords='offset points')

    ax4.set_title("Frekuensi Hari berdasarkan Kategori Permintaan Harian", fontsize=14)
    ax4.set_xlabel("Kategori Permintaan")
    ax4.set_ylabel("Jumlah Hari")
    ax4.grid(axis='y', linestyle='--', alpha=0.5)
    st.pyplot(fig4)

with st.expander("Selengkapnya (Insight Kategori Permintaan)"):
    st.write(
        """
        * Sebagian besar hari operasional berada pada kategori **Medium Demand** (3.000–6.000 penyewaan) dan **High Demand** (>6.000 penyewaan).
        * Kategori **Low Demand** (<3.000 penyewaan) memiliki frekuensi kejadian paling sedikit, menandakan bahwa penurunan drastis pada permintaan hanya terjadi pada kondisi khusus seperti cuaca ekstrem atau musim dingin.
        """
    )

st.caption("Copyright (c) 2026 - Bike Sharing Dashboard Analysis")