import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    layout="wide"
)

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
    st.image(
        "https://github.com/dicodingacademy/assets/raw/main/logo.png"
    )

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
        st.error(
            "Tanggal mulai tidak boleh lebih besar "
            "dari tanggal akhir."
        )
        st.stop()

    season_col = (
        "season_label"
        if "season_label" in main_df.columns
        else "season"
    )

    weather_col = (
        "weather_label"
        if "weather_label" in main_df.columns
        else "weathersit"
    )

    st.subheader("Filter Tambahan")

    season_options = main_df[season_col].dropna().unique()
    weather_options = main_df[weather_col].dropna().unique()

    season_filter = st.multiselect(
        "Musim (Season)",
        options=season_options,
        default=list(season_options)
    )

    weather_filter = st.multiselect(
        "Kondisi Cuaca",
        options=weather_options,
        default=list(weather_options)
    )

# --- FILTER DATASET ---
filtered_df = main_df[
    (main_df["dteday"].dt.date >= start_date)
    & (main_df["dteday"].dt.date <= end_date)
    & (main_df[season_col].isin(season_filter))
    & (main_df[weather_col].isin(weather_filter))
].copy()

# --- AGGREGATE DAILY DATA ---
if not filtered_df.empty:
    daily_df = (
        filtered_df.groupby("dteday")
        .agg({
            "cnt": "sum",
            "registered": "sum",
            "casual": "sum",
            "temp": "mean",
            season_col: "first",
            weather_col: "first"
        })
        .reset_index()
    )
else:
    daily_df = pd.DataFrame()

# --- MAIN PAGE HEADER ---
st.header("Bike Sharing Performance & Behavior Dashboard 🚲")
st.markdown(
    "Dashboard interaktif untuk menganalisis pola penyewaan sepeda "
    "berdasarkan jam, tipe pengguna, musim, suhu, dan kategori permintaan."
)

# --- METRICS ---
col1, col2, col3 = st.columns(3)

total_rentals = daily_df["cnt"].sum() if not daily_df.empty else 0
total_registered = daily_df["registered"].sum() if not daily_df.empty else 0
total_casual = daily_df["casual"].sum() if not daily_df.empty else 0

col1.metric("Total Penyewaan", f"{total_rentals:,.0f}")
col2.metric("Total Penyewa Registered", f"{total_registered:,.0f}")
col3.metric("Total Penyewa Casual", f"{total_casual:,.0f}")

st.divider()

# --- VISUALIZATION 1: HOURLY RENTAL PATTERNS ---
st.subheader("1. Pola Penyewaan Sepeda Per Jam: Casual vs Registered")

if not filtered_df.empty and "hr" in filtered_df.columns:
    hourly_df = (
        filtered_df.groupby(["workingday", "hr"])[
            ["casual", "registered"]
        ]
        .mean()
        .reset_index()
    )

    fig1, axes = plt.subplots(
        1, 2,
        figsize=(14, 5),
        sharey=True
    )

    # Working days
    workday_data = hourly_df[hourly_df["workingday"] == 1]

    sns.lineplot(
        data=workday_data,
        x="hr",
        y="registered",
        label="Registered",
        marker="o",
        color="#1F77B4",
        ax=axes[0]
    )

    sns.lineplot(
        data=workday_data,
        x="hr",
        y="casual",
        label="Casual",
        marker="o",
        color="#FF7F0E",
        ax=axes[0]
    )

    axes[0].set_title("Hari Kerja (Working Day)")
    axes[0].set_xlabel("Jam (0–23)")
    axes[0].set_ylabel("Rata-Rata Jumlah Penyewaan")
    axes[0].set_xticks(range(0, 24, 2))
    axes[0].grid(axis="y", linestyle="--", alpha=0.5)

    # Weekends and holidays
    holiday_data = hourly_df[hourly_df["workingday"] == 0]

    sns.lineplot(
        data=holiday_data,
        x="hr",
        y="registered",
        label="Registered",
        marker="o",
        color="#1F77B4",
        ax=axes[1]
    )

    sns.lineplot(
        data=holiday_data,
        x="hr",
        y="casual",
        label="Casual",
        marker="o",
        color="#FF7F0E",
        ax=axes[1]
    )

    axes[1].set_title("Hari Libur / Akhir Pekan")
    axes[1].set_xlabel("Jam (0–23)")
    axes[1].set_xticks(range(0, 24, 2))
    axes[1].grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()
    st.pyplot(fig1)
    plt.close(fig1)
else:
    st.warning("Data kosong atau kolom `hr` tidak ditemukan.")

with st.expander("Selengkapnya (Insight Perilaku Pengguna)"):
    st.markdown("""
    - **Hari Kerja:** Pengguna Registered dapat menunjukkan puncak
      penyewaan pada pagi dan sore hari.
    - **Hari Libur / Akhir Pekan:** Pengguna Registered dapat menunjukkan
      aktivitas penyewaan yang lebih tinggi pada siang hingga sore hari.
    """)

st.divider()

# --- VISUALIZATION 2: SEASON AND TEMPERATURE ---
st.subheader("2. Pengaruh Faktor Musim dan Suhu terhadap Volume Penyewaan pada 2011-2012")

col_a, col_b = st.columns(2)

if not daily_df.empty:
    with col_a:
        fig2, ax2 = plt.subplots(figsize=(6, 4.5))

        season_order = (
            ["Spring", "Summer", "Fall", "Winter"]
            if season_col == "season_label"
            else None
        )

        sns.barplot(
            data=daily_df,
            x=season_col,
            y="cnt",
            order=season_order,
            color="#4C78A8",
            errorbar=None,
            ax=ax2
        )

        for bar in ax2.patches:
            if bar.get_height() > 0:
                ax2.annotate(
                    f"{bar.get_height():.0f}",
                    (
                        bar.get_x() + bar.get_width() / 2,
                        bar.get_height()
                    ),
                    ha="center",
                    va="bottom",
                    fontsize=9,
                    xytext=(0, 3),
                    textcoords="offset points"
                )

        ax2.set_title("Rata-Rata Penyewaan per Musim")
        ax2.set_xlabel("Musim")
        ax2.set_ylabel("Rata-Rata Penyewaan Harian")
        ax2.grid(axis="y", linestyle="--", alpha=0.5)

        st.pyplot(fig2)
        plt.close(fig2)

    with col_b:
        fig3, ax3 = plt.subplots(figsize=(6, 4.5))

        sns.scatterplot(
            data=daily_df,
            x="temp",
            y="cnt",
            hue=season_col,
            palette="Set2",
            alpha=0.8,
            ax=ax3
        )

        sns.regplot(
            data=daily_df,
            x="temp",
            y="cnt",
            scatter=False,
            color="red",
            ax=ax3
        )

        ax3.set_title("Hubungan Suhu vs Total Penyewaan")
        ax3.set_xlabel("Suhu (Normalized)")
        ax3.set_ylabel("Total Penyewaan Harian")
        ax3.grid(True, linestyle="--", alpha=0.5)

        st.pyplot(fig3)
        plt.close(fig3)
else:
    st.info("Tidak ada data untuk menampilkan analisis musim dan suhu.")

with st.expander("Selengkapnya (Insight Musim & Suhu)"):
    st.markdown("""
    - **Pengaruh Musim:** Bandingkan rata-rata penyewaan pada setiap
      musim untuk mengetahui perbedaan tingkat permintaan.
    - **Korelasi Suhu:** Grafik sebar dan garis tren membantu mengamati
      hubungan antara suhu udara (`temp`) dan jumlah penyewaan.
    """)

st.divider()

# --- VISUALIZATION 3: DEMAND CATEGORY ---
st.subheader("3. Analisis Lanjutan: Distribusi Kategori Permintaan Sepeda")

if not daily_df.empty:
    temp_df_bin = daily_df.copy()

    bins = [0, 3000, 6000, float("inf")]
    labels_bin = [
        "Low Demand",
        "Medium Demand",
        "High Demand"
    ]

    temp_df_bin["demand_category"] = pd.cut(
        temp_df_bin["cnt"],
        bins=bins,
        labels=labels_bin,
        include_lowest=True
    )

    fig4, ax4 = plt.subplots(figsize=(10, 5))

    sns.countplot(
        data=temp_df_bin,
        x="demand_category",
        order=labels_bin,
        hue="demand_category",
        palette=["#72B4EB", "#2B5C8F", "#0D2B45"],
        legend=False,
        ax=ax4
    )

    for bar in ax4.patches:
        if bar.get_height() > 0:
            ax4.annotate(
                f"{int(bar.get_height())} hari",
                (
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height()
                ),
                ha="center",
                va="bottom",
                fontsize=10,
                fontweight="bold",
                xytext=(0, 5),
                textcoords="offset points"
            )

    ax4.set_title("Frekuensi Hari berdasarkan Kategori Permintaan")
    ax4.set_xlabel("Kategori Permintaan")
    ax4.set_ylabel("Jumlah Hari")
    ax4.grid(axis="y", linestyle="--", alpha=0.5)

    st.pyplot(fig4)
    plt.close(fig4)
else:
    st.info("Tidak ada data untuk menampilkan kategori permintaan.")

with st.expander("Selengkapnya (Insight Kategori Permintaan)"):
    st.markdown("""
    - **Low Demand:** 0–3.000 penyewaan per hari.
    - **Medium Demand:** Lebih dari 3.000 hingga 6.000 penyewaan per hari.
    - **High Demand:** Lebih dari 6.000 penyewaan per hari.

    Kategori ini membantu menunjukkan frekuensi setiap tingkat permintaan
    selama periode yang dipilih.
    """)

# --- FOOTER ---
st.caption("Copyright © 2026 - Bike Sharing Dashboard Analysis")