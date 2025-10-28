import streamlit as st
import pandas as pd
import os

# Tentukan path file CSV secara relatif dari root folder
CSV_PATH = 'Data/heart_2022_no_nans.csv'

@st.cache_data
def load_full_dataset():
    """
    Memuat dataset lengkap hanya sekali dan menyimpannya di cache Streamlit.
    """
    st.info(f"Memuat dataset besar dari: {CSV_PATH}.")
    
    # Tambahkan pemeriksaan untuk memastikan file ada
    if not os.path.exists(CSV_PATH):
        st.error(f"Error: File CSV TIDAK DITEMUKAN di {CSV_PATH}. Harap periksa path Anda.")
        return None
        
    try:
        df = pd.read_csv(CSV_PATH)
    except Exception as e:
        st.error(f"Error saat membaca file CSV: {e}")
        return None
        
    return df

# Panggil fungsi load_full_dataset() untuk mendapatkan DataFrame
# Semua file study case akan mengimpor variabel ini
DF_FULL = load_full_dataset()