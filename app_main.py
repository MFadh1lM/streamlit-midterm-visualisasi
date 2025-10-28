import streamlit as st
# Import fungsi show_page dari setiap file study case
from pages import sc1_usia, sc2_gender_usia

# --- KONFIGURASI APLIKASI ---
st.set_page_config(
    page_title="Visualisasi Midterm Kelompok [Nama Kelompok Anda]",
    layout="wide"
)

# --- STRUKTUR UTAMA APLIKASI STREAMLIT ---
def main():
    st.sidebar.title("Navigasi Study Case")
    
    # Header di halaman utama
    st.title("Aplikasi Visualisasi Data Serangan Jantung")
    st.info("Pilih Study Case dari menu di samping kiri (Sidebar).")

    # Daftar Study Case
    PAGES = {
        "1. Risiko Usia": sc1_usia,
        "2. Rasio Gender vs Usia": sc2_gender_usia,
        "3. Peta Regional": None, # Akan diisi saat Anda membuatnya
        # Tambahkan sisa 7 case lainnya di sini
    }

    # Sidebar Navigation
    case_selection = st.sidebar.radio("Pilih Study Case:", list(PAGES.keys()))

    # Memanggil fungsi show_page() dari file yang dipilih
    page = PAGES[case_selection]
    
    if page is not None:
        page.show_page()
    else:
        st.warning(f"Konten untuk '{case_selection}' belum tersedia.")

if __name__ == '__main__':
    main()