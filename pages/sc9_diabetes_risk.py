import streamlit as st
import pandas as pd
import altair as alt

try:
    from data_loader import DF_FULL
except ImportError:
    st.error("Gagal mengimpor DF_FULL. Pastikan file data_loader.py sudah dibuat.")
    DF_FULL = None

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

if DF_FULL is not None:
    # 1. Filter kasus serangan jantung ('HadHeartAttack' == 'Yes')
    df_cases = DF_FULL[DF_FULL['HadHeartAttack'] == 'Yes'].copy()

    # 2. Hitung Count of HadHeartAttack berdasarkan HadDiabetes
    df_counts = df_cases.groupby('HadDiabetes', as_index=False)['HadHeartAttack'].count()
    df_counts.rename(columns={'HadHeartAttack': 'Count_of_HadHeartAttack', 'HadDiabetes': 'Status Diabetes'}, inplace=True)
    
    # 3. Hitung Proporsi Kasus Absolut
    total_cases = df_counts['Count_of_HadHeartAttack'].sum()
    df_counts['Proporsi_Kasus (%)'] = (df_counts['Count_of_HadHeartAttack'] / total_cases * 100).round(1)

    # 4. Definisikan urutan visualisasi
    diabetes_order = ['Yes', 'No, pre-diabetes or borderline diabetes', 'Yes, but only during pregnancy (female)', 'No']
    
    df_diabetes_risk = df_counts
else:
    df_diabetes_risk = pd.DataFrame(columns=['Status Diabetes', 'Count_of_HadHeartAttack', 'Proporsi_Kasus (%)'])

def create_bar_chart(df):
    """Membuat Bagan Kolom dengan Warna yang Mengikuti Tingkat Kasus."""
    
    diabetes_order = ['No', 'No, pre-diabetes or borderline diabetes', 'Yes, but only during pregnancy (female)', 'Yes']
    
    # Kunci: Mengkodekan warna berdasarkan metrik kuantitatif (Count)
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Status Diabetes:N', sort=diabetes_order, title='Status Diabetes', axis=alt.Axis(labelAngle=-45)),
        y=alt.Y('Count_of_HadHeartAttack:Q', title='Jumlah Kasus Serangan Jantung Absolut'),
        
        # <<< PERUBAHAN UTAMA: Warna berdasarkan Count_of_HadHeartAttack >>>
        color=alt.Color('Count_of_HadHeartAttack:Q', 
                        title='Kasus Absolut',
                        scale=alt.Scale(scheme='bluegreen')), # Skema warna sequential
        # <<< AKHIR PERUBAHAN UTAMA >>>
        
        tooltip=['Status Diabetes', 'Count_of_HadHeartAttack', 'Proporsi_Kasus (%)'],
        text=alt.Text('Proporsi_Kasus (%):Q', format='.1f')
    ).properties(
        title='Proporsi Kasus Serangan Jantung Berdasarkan Status Diabetes'
    ).interactive()
    
    return chart

def show_page():
    """Menampilkan konten lengkap Study Case 9."""
    
    if DF_FULL is None:
        return

    st.header("Study Case 9: Diabetes vs. Kontribusi Kasus Serangan Jantung")
    st.markdown("---")
    
    st.subheader("1. Bagan Kolom Proporsi Kasus Absolut (Warna Mengikuti Jumlah Kasus)")
    st.altair_chart(create_bar_chart(df_diabetes_risk), use_container_width=True) 

    st.subheader("2. Data Rinci Kasus Absolut dan Proporsi")
    st.dataframe(df_diabetes_risk, hide_index=True)
    
    st.subheader("3. Interpretasi dan Kesimpulan")
    
    st.markdown("""
        ### Analisis Proporsi Kasus Absolut:
        Visualisasi ini menunjukkan seberapa besar setiap kelompok diabetes berkontribusi terhadap total kasus serangan jantung yang tercatat ($13.435$ kasus). **Warna batang menunjukkan beban kasus (semakin gelap, semakin tinggi jumlah kasus absolut).**

        1.  **Individu tanpa diabetes (`No`)** memiliki jumlah kasus serangan jantung tertinggi, yaitu $\mathbf{8.333}$ kasus ($\mathbf{62,0\%}$). **Warna Gelap:** Warna batang ini akan menjadi yang paling gelap, mengindikasikan beban kasus terbesar.
        2.  **Penderita diabetes (`Yes`)** mencatat $\mathbf{4.654}$ kasus ($\mathbf{34,6\%}$). **Warna Sedang:** Warna batang ini akan lebih terang daripada 'No', tetapi lebih gelap dari kelompok pre-diabetes, menunjukkan kontribusi kasus yang besar.
        3.  **Kelompok pre-diabetes** ($\mathbf{392}$ kasus, $\mathbf{2,9\%}$) dan **diabetes gestasional** ($\mathbf{56}$ kasus, $\mathbf{0,4\%}$) memiliki warna paling terang.

        ### Kesimpulan:
        Warna batang secara visual mengonfirmasi bahwa **mayoritas kasus serangan jantung (beban kasus)** terkonsentrasi pada kelompok Non-Diabetes (`No`), meskipun proporsi $\mathbf{37,9\%}$ kasus berasal dari individu dengan riwayat diabetes. Ini menegaskan adanya **korelasi kuat antara diabetes dan peningkatan risiko penyakit jantung.**
    """)