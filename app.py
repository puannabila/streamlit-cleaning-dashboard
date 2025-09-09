import streamlit as st
import pandas as pd
import re
from sqlalchemy import create_engine

# --- Konfigurasi koneksi database ---
DB_HOST = "sql.freedb.tech"
DB_PORT = 3306
DB_NAME = "freedb_dashboardkp"
DB_USER = "freedb_puankp"
DB_PASS = "67$HZZgR9zvAAns"

# Buat engine koneksi SQLAlchemy
engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

st.title("Upload & Cleaning Data Excel")

uploaded_file = st.file_uploader("Upload file Excel", type=["xlsx", "xls"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    st.subheader("Data Asli")
    st.dataframe(df.head())

    # --- Preprocessing ---
    df_clean = df.dropna()

    # Mapping bulan Indonesia ke Inggris
    bulan_mapping = {
        "Januari": "January",
        "Februari": "February",
        "Maret": "March",
        "April": "April",
        "Mei": "May",
        "Juni": "June",
        "Juli": "July",
        "Agustus": "August",
        "September": "September",
        "Oktober": "October",
        "November": "November",
        "Desember": "December"
    }

    # Standarisasi format tanggal -> dd/mm/yyyy
    if "Day of Tanggal Pengajuan Proyek" in df_clean.columns:
        for indo, eng in bulan_mapping.items():
            df_clean["Day of Tanggal Pengajuan Proyek"] = (
                df_clean["Day of Tanggal Pengajuan Proyek"]
                .astype(str)
                .str.replace(indo, eng, regex=False)
            )

        df_clean["Day of Tanggal Pengajuan Proyek"] = pd.to_datetime(
            df_clean["Day of Tanggal Pengajuan Proyek"], errors="coerce"
        ).dt.strftime("%d/%m/%Y")

    # Standarisasi Nama Perusahaan
    if "Nama Perusahaan" in df_clean.columns:
        def clean_company_name(name):
            if pd.isnull(name):
                return name
            name = name.upper()
            name = re.sub(r'\s+', ' ', name)  # hapus spasi ganda
            name = re.sub(r'[^\w\s.,]', '', name)  # hapus karakter khusus
            return name.strip()

        df_clean["Nama Perusahaan"] = df_clean["Nama Perusahaan"].astype(str).apply(clean_company_name)

    # --- Standarisasi Nama Kelurahan Usaha ---
    if "kelurahan_usaha" in df_clean.columns:
        kelurahan_mapping = {
            "Pallima": "Pal Lima",
            "Sungaijawi Dalam": "Sungai Jawi Dalam",
            "Sungaijawi Luar": "Sungai Jawi Luar",
            "Daratsekip": "Darat Sekip",
            "Sungaibangkong": "Sungai Bangkong",
            "Sungaijawi": "Sungai Jawi",
            "Benuamelayu Darat": "Benua Melayu Darat",
            "Benuamelayu Laut": "Benua Melayu Laut",
            "Kotabaru": "Kota Baru",
            "Parittokaya": "Parit Tokaya",
            "Dalambugis": "Dalam Bugis",
            "Paritmayor": "Parit Mayor",
            "Tambelansampit": "Tambelan Sampit",
            "Tanjunghulu": "Tanjung Hulu",
            "Tanjunghilir": "Tanjung Hilir",
            "Batulayang": "Batu Layang"
        }

        df_clean["kelurahan_usaha"] = df_clean["kelurahan_usaha"].replace(kelurahan_mapping)

    st.subheader("Data Setelah Cleaning")
    st.dataframe(df_clean.head())

    # --- Simpan hasil cleaning ke file Excel ---
    cleaned_file = "data_cleaning.xlsx"
    df_clean.to_excel(cleaned_file, index=False)
    with open(cleaned_file, "rb") as f:
        st.download_button("Download Hasil Cleaning", f, file_name="data_cleaning.xlsx")

    # --- Simpan hasil cleaning ke Database ---
    if st.button("Simpan ke Database"):
        try:
            df_clean.to_sql("data_cleaning", con=engine, if_exists="replace", index=False)
            st.success("Data berhasil disimpan ke database!")
        except Exception as e:
            st.error(f"Gagal menyimpan ke database: {e}")

    # --- Dashboard sederhana ---
    st.subheader("Dashboard Visualisasi")
    if "Kecamatan" in df_clean.columns:
        kecamatan_count = df_clean["Kecamatan"].value_counts()
        st.bar_chart(kecamatan_count)
