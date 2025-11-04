import streamlit as st
import pandas as pd
import altair as alt

# --- FUNGSI RENDER HALAMAN DATASET ---
def show_page():
    st.header("📚 Deskripsi Dataset yang Digunakan")
    st.markdown("---")

    st.subheader("Indicators of Heart Disease (2022)")
    
    st.info("Dataset ini digunakan sebagai sumber data utama untuk analisis 10 Studi Kasus mengenai risiko penyakit kardiovaskular.")

    # Tampilkan Detail Kunci dalam bentuk tabel
    data_info = {
        'Metrik': ['Nama Dataset', 'Sumber', 'Jumlah Kolom', 'Jumlah Baris (Setelah Pembersihan)', 'Lisensi'],
        'Nilai': [
            'Key Indicators of Heart Disease (2022)',
            'Kaggle / CDC BRFSS 2022',
            '40',
            '246.022',
            'CC0: Public Domain'
        ]
    }
    df_info = pd.DataFrame(data_info)
    
    st.table(df_info.set_index('Metrik'))
    
    st.subheader("Latar Belakang Dataset")
    st.markdown("""
        Dataset **Key Indicators of Heart Disease** berasal dari survei **CDC Behavioral Risk Factor Surveillance System (BRFSS) 2022**. Survei ini melibatkan lebih dari $400.000$ responden dewasa di Amerika Serikat.

        Dataset yang digunakan dalam proyek ini merupakan hasil penyaringan dari sekitar $300$ variabel asli menjadi $\mathbf{40}$ variabel utama yang relevan.

        #### Fokus Variabel Utama:
        Variabel-variabel tersebut berkaitan erat dengan faktor risiko penyakit jantung, termasuk:
        * Tekanan darah tinggi dan kolesterol tinggi.
        * Kebiasaan merokok dan penggunaan rokok elektrik.
        * Riwayat penyakit kronis (Diabetes, Stroke, dll.).
        * Gaya hidup (obesitas, kurang aktivitas fisik, dan konsumsi alkohol berlebih).
        
        Analisis 10 Studi Kasus di aplikasi ini bertujuan untuk menguji dan memvisualisasikan korelasi antara faktor-faktor gaya hidup dan kesehatan tersebut dengan risiko terjadinya serangan jantung (`HadHeartAttack`).
    """)