import streamlit as st
import pandas as pd
import altair as alt

# --- KONFIGURASI DAN PEMBACAAN DATA ---
CSV_PATH = 'Data/heart_2022_no_nans.csv'

@st.cache_data
def load_data(path):
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        st.error(f"Error: File CSV tidak ditemukan di {path}. Pastikan path sudah benar.")
        return None
    return df

df_full = load_data(CSV_PATH)

# Fungsi pengelompokan usia yang disederhanakan
def simplify_age(age_category):
    if age_category in ['Age 18 to 24', 'Age 25 to 29', 'Age 30 to 34', 'Age 35 to 39', 'Age 40 to 44']:
        return '<45 Tahun'
    elif age_category in ['Age 45 to 49', 'Age 50 to 54', 'Age 55 to 59', 'Age 60 to 64']:
        return '45-64 Tahun'
    elif age_category in ['Age 65 to 69', 'Age 70 to 74', 'Age 75 to 79']:
        return '65-79 Tahun'
    elif age_category == 'Age 80 or older':
        return '>=80 Tahun'
    return age_category


# =================================================================
#                         STUDY CASE 2 DATA (DARI CSV & DIKELOMPOKKAN)
# =================================================================

if df_full is not None:
    # 1. Filter kasus serangan jantung & Kelompokkan usia
    df_cases = df_full[df_full['HadHeartAttack'] == 'Yes'].copy()
    df_cases['Kelompok Usia'] = df_cases['AgeCategory'].apply(simplify_age)

    # 2. Hitung Jumlah Kasus (Count) per kombinasi Jenis Kelamin dan Usia Baru
    df_counts = df_cases.groupby(['Kelompok Usia', 'Sex'], as_index=False)['HadHeartAttack'].count()
    df_counts.rename(columns={'HadHeartAttack': 'Jumlah Kasus'}, inplace=True)
    
    # 3. Hitung Persentase Kasus Global (untuk Kenaikan Absolut)
    total_cases_sc2 = df_counts['Jumlah Kasus'].sum()
    df_counts['Persentase Kasus Global (%)'] = (df_counts['Jumlah Kasus'] / total_cases_sc2 * 100).round(2)
    
    # 4. Definisikan urutan usia yang disederhanakan
    simple_age_order = ['<45 Tahun', '45-64 Tahun', '65-79 Tahun', '>=80 Tahun']
    
    # 5. Fungsi BARU untuk menghitung Kenaikan Absolut dan menyertakan Jumlah Kasus
    def calculate_increase_with_count(df, gender):
        df_f = df[df['Sex'] == gender].copy()
        
        # Urutkan berdasarkan urutan usia yang disederhanakan
        df_f = df_f.sort_values(by='Kelompok Usia', key=lambda x: x.map({age: i for i, age in enumerate(simple_age_order)}))
        
        # Hitung Kenaikan Absolut
        df_f['Kenaikan Absolut (%)'] = df_f['Persentase Kasus Global (%)'].diff().fillna(0).round(2)
        
        df_f.rename(columns={'Sex': 'Jenis Kelamin'}, inplace=True)
        
        # Urutan kolom yang baru (dengan Jumlah Kasus)
        return df_f[['Kelompok Usia', 'Jumlah Kasus', 'Persentase Kasus Global (%)', 'Kenaikan Absolut (%)']]

    df_male_increase = calculate_increase_with_count(df_counts, 'Male')
    df_female_increase = calculate_increase_with_count(df_counts, 'Female')
    
    # Menyiapkan data untuk visualisasi Stacked Bar
    df_gender_age_count = df_counts.rename(columns={'Sex': 'Jenis Kelamin'})
    
else:
    # Buat DataFrame kosong jika data gagal dimuat
    df_gender_age_count = pd.DataFrame(columns=['Kelompok Usia', 'Jenis Kelamin', 'Jumlah Kasus'])
    df_male_increase = pd.DataFrame(columns=['Kelompok Usia', 'Jumlah Kasus', 'Persentase Kasus Global (%)', 'Kenaikan Absolut (%)'])
    df_female_increase = pd.DataFrame(columns=['Kelompok Usia', 'Jumlah Kasus', 'Persentase Kasus Global (%)', 'Kenaikan Absolut (%)'])


# =================================================================
#                       FUNGSI VISUALISASI SC 2
# =================================================================
def create_gender_age_stacked_bar_chart(df):
    """Membuat Normalized Stacked Bar Chart (Proporsi 100%)"""
    
    simple_age_order = ['<45 Tahun', '45-64 Tahun', '65-79 Tahun', '>=80 Tahun']
    color_scale = alt.Scale(domain=['Male', 'Female'], range=['#1f77b4', '#ff7f0e'])

    chart_bar = alt.Chart(df).mark_bar().encode(
        y=alt.Y('Kelompok Usia:N', sort=simple_age_order, title='Kelompok Usia'),
        x=alt.X('Jumlah Kasus:Q', stack='normalize', axis=alt.Axis(title='Proporsi Kasus Serangan Jantung (%)', format='.0%')), 
        color=alt.Color('Jenis Kelamin:N', scale=color_scale, legend=alt.Legend(title="Jenis Kelamin")),
        tooltip=[
            'Kelompok Usia', 
            'Jenis Kelamin', 
            alt.Tooltip('Jumlah Kasus:Q', title='Jumlah Kasus Aktual')
        ]
    ).properties(
        title='Proporsi Kasus Serangan Jantung Berdasarkan Jenis Kelamin dalam Setiap Kelompok Usia',
        height=250 
    ).interactive()
    
    return chart_bar

# =================================================================
#                       FUNGSI RENDER SC 2
# =================================================================
def show_page():
    """Menampilkan konten lengkap Study Case 2: Gender vs. Usia."""
    
    if df_full is None:
        return

    st.header("Study Case 2: Perbandingan Risiko Serangan Jantung Berdasarkan Jenis Kelamin dan Kelompok Usia")
    st.markdown("---")
    
    # --- BAGIAN 1: STACKED BAR CHART ---
    st.subheader("1. Proporsi Kasus Berdasarkan Gender dan Usia (Proporsi 100% per Kelompok Usia)")
    st.altair_chart(create_gender_age_stacked_bar_chart(df_gender_age_count), use_container_width=True) 

    # --- BAGIAN 2: DATA KENAIKAN ABSOLUT (2 TABEL FOKUS) ---
    st.subheader("2. Analisis Kenaikan Absolut Risiko Antar Kelompok Usia")
    st.info("Tabel ini menunjukkan total kasus, persentase global, dan percepatan risiko per gender.")
    
    col_male_table, col_female_table = st.columns(2)
    
    with col_male_table:
        st.caption("**:blue[Laki-laki (Male)]**")
        st.dataframe(df_male_increase, hide_index=True)
        
    with col_female_table:
        st.caption("**:orange[Perempuan (Female)]**")
        st.dataframe(df_female_increase, hide_index=True)

    # Catatan: Tabel Rincian Lama Dihapus

    st.subheader("3. Interpretasi dan Penjelasan Detail")
    st.markdown("""
        ### Studi kasus 2: Apakah proporsi risiko serangan jantung pada perempuan selalu lebih rendah daripada laki-laki di setiap fase usia?
        
        #### Analisis Proporsi (Stacked Chart):
        Visualisasi ini menunjukkan **proporsi kasus serangan jantung** di dalam setiap kelompok usia (total $100\%$ per bar).
        
        1.  **Dominasi Awal (<45 Tahun):** Proporsi kasus pada Laki-laki sangat signifikan (sekitar $\mathbf{60\%}$), menegaskan perlindungan hormonal Estrogen pada perempuan di usia reproduktif.
        2.  **Kesenjangan Menyempit (45-64 Tahun):** Proporsi Perempuan mulai meningkat tajam. Ini adalah periode kritis yang bertepatan dengan hilangnya perlindungan hormonal (menopause).
        3.  **Proporsi Tinggi di Usia Lanjut (>=80 Tahun):** Proporsi Perempuan tetap tinggi (mendekati $\mathbf{40\%}$ dari total kasus di kelompok usia tersebut), menunjukkan bahwa di usia sangat tua, Perempuan membentuk bagian kasus yang sangat substansial.

        #### Analisis Kenaikan Absolut (Tabel):
        Tabel ini menunjukkan percepatan risiko absolut global di setiap transisi fase usia.
        1.  **Titik Percepatan Kritis:** Kenaikan absolut tertinggi untuk **kedua gender** terjadi pada transisi usia **45-64 Tahun** dan **65-79 Tahun**. Usia paruh baya (45-64) dan awal usia lanjut (65-79) adalah fase percepatan risiko paling dramatis bagi kedua gender.
        
        ### Kesimpulan
        * **Proporsi Risiko Perempuan Meningkat Tajam:** Proporsi kasus pada Perempuan meningkat signifikan setelah usia 45 tahun.
        * **Fase Kritis:** Usia **45-64 Tahun** dan **65-79 Tahun** adalah fase yang paling penting untuk intervensi preventif pada kedua gender, karena mengalami percepatan risiko absolut terbesar.
    """)