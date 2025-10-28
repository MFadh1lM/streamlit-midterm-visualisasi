import streamlit as st
# Import fungsi show_page dari setiap file study case
from pages import sc1_usia, sc2_gender_usia, sc3_sleep_hours, sc4_covid_risk, sc5_alcohol_risk, sc6_smoking, sc7_regional_map, sc8_physical_activity, sc9_diabetes_risk, sc10_stroke_risk

st.set_page_config(
    page_title="Visualisasi Data Midterm",
    layout="wide"
)

def main():
    
    # 1. Definisikan Struktur Navigasi (PAGES)
    PAGES = {
        "1. Usia": sc1_usia,
        "2. Rasio Gender vs Usia": sc2_gender_usia,
        "3. Durasi Tidur": sc3_sleep_hours,
        "4. Covid-19": sc4_covid_risk,
        "5. Alkohol vs Rokok": sc5_alcohol_risk,
        "6. Rokok vs Penggunaan Vape": sc6_smoking,
        "7. Beban Kasus Regional": sc7_regional_map,
        "8. Aktivitas Fisik": sc8_physical_activity,
        "9. Diabetes": sc9_diabetes_risk,
        "10. Riwayat Stroke": sc10_stroke_risk,
    }

    # 2. Setup Sidebar
    st.sidebar.title("Navigasi Study Case")
    
    # Tambahkan item "Halaman Utama" ke pilihan sidebar
    page_options = ["Halaman Utama"] + list(PAGES.keys())
    case_selection = st.sidebar.radio("Pilih Study Case:", page_options)

    # 3. Logika Tampilan
    
    if case_selection == "Halaman Utama":
        # Tampilan Halaman Utama (Homepage)
        st.title("Proyek Midterm: Analisis Risiko Penyakit Jantung")
        st.subheader("Visualisasi dan Deskripsi 10 Studi Kasus")
        st.info("Navigasi ke 10 Studi Kasus dapat dilakukan melalui menu di *Sidebar* (Samping Kiri).")
        
        st.markdown("---")
        
        st.header(" Detail Kelompok")
        
        # --- TEMPLATE ANGGOTA KELOMPOK ---
        st.subheader("1. Identitas Kelompok")
        st.markdown(
            """
            | No. | Nama Lengkap | NIM |
            | :---: | :--- | :--- |
            | 1 | Muhammad Ma'ruf Firdaus | 1301223001 |
            | 2 | Muhammad Fadhil Munawwar | 1301223377 |
            | 3 | I Dewa Putu Rangga Putra Dharma | 1301220427 |
            | 4 | Fernando Agusti | 1301223388 |
            | 5 | Nazhmi Ahmad Fauzan | 1301223056 |

            """
        )

        st.subheader("2. Link Proyek & Laporan")
        st.markdown(
            """
            * **Link GitHub:** `https://github.com/MFadh1lM/streamlit-midterm-visualisasi`
            * **Link Live Preview (Streamlit Cloud):** `https://app-midterm-visualisasi-jujvzgnxaslzrarxmptivj.streamlit.app/`
            * **Laporan Analisis:** `https://colab.research.google.com/drive/1D1JgfEn_R8FhZ80nrCJ79uEEiSnn2NFU?usp=sharing`
            """
        )
        st.markdown("---")
        
    else:
        # Jika Study Case dipilih, jalankan fungsi show_page()
        page = PAGES[case_selection]
        page.show_page()

if __name__ == '__main__':
    main()