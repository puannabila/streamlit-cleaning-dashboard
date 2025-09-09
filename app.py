import streamlit as st
import pandas as pd
import re

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
        # Ganti bulan Indonesia ke Inggris
        for indo, eng in bulan_mapping.items():
            df_clean["Day of Tanggal Pengajuan Proyek"] = df_clean["Day of Tanggal Pengajuan Proyek"].astype(str).str.replace(indo, eng, regex=False)

        # Ubah ke datetime lalu format dd/mm/yyyy
        df_clean["Day of Tanggal Pengajuan Proyek"] = pd.to_datetime(
            df_clean["Day of Tanggal Pengajuan Proyek"], errors="coerce"
        ).dt.strftime("%d/%m/%Y")

    # Standarisasi Nama Perusahaan
    if "Nama Perusahaan" in df_clean.columns:
        def clean_company_name(name):
            if pd.isnull(name):
                return name
            # Ubah ke uppercase
            name = name.upper()
            # Hapus spasi ganda
            name = re.sub(r'\s+', ' ', name)
            # Hapus karakter khusus kecuali titik dan koma
            name = re.sub(r'[^\w\s.,]', '', name)
            return name.strip()

        df_clean["Nama Perusahaan"] = df_clean["Nama Perusahaan"].astype(str).apply(clean_company_name)

    st.subheader("Data Setelah Cleaning")
    st.dataframe(df_clean.head())

    # Download hasil cleaning
    cleaned_file = "data_cleaning.xlsx"
    df_clean.to_excel(cleaned_file, index=False)
    with open(cleaned_file, "rb") as f:
        st.download_button("Download Hasil Cleaning", f, file_name="data_cleaning.xlsx")

    # Dashboard sederhana
    st.subheader("Dashboard Visualisasi")
    if "Kecamatan" in df_clean.columns:
        kecamatan_count = df_clean["Kecamatan"].value_counts()
        st.bar_chart(kecamatan_count)
