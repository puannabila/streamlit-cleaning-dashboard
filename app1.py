import streamlit as st
import pandas as pd

st.title("Upload & Cleaning Data Excel")

uploaded_file = st.file_uploader("Upload file Excel", type=["xlsx", "xls"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    st.subheader("Data Asli")
    st.dataframe(df.head())

    # --- Preprocessing ---
    df_clean = df.dropna()

    # Standarisasi format tanggal
    if "Tanggal" in df_clean.columns:
        df_clean["Tanggal"] = pd.to_datetime(df_clean["Tanggal"], errors="coerce").dt.strftime("%Y-%m-%d")

    # Standarisasi Nama Perusahaan
    if "Nama Perusahaan" in df_clean.columns:
        df_clean["Nama Perusahaan"] = df_clean["Nama Perusahaan"].str.upper()

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
