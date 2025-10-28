import streamlit as st
import pandas as pd
import altair as alt

try:
    from data_loader import DF_FULL
except ImportError:
    st.error("Gagal mengimpor DF_FULL. Pastikan file data_loader.py sudah dibuat.")
    DF_FULL = None

if DF_FULL is not None:
    # 1. Filter kasus serangan jantung ('HadHeartAttack' == 'Yes')
    df_cases = DF_FULL[DF_FULL['HadHeartAttack'] == 'Yes'].copy()

    # 2. Hitung Count of HadHeartAttack berdasarkan HadStroke
    df_counts = df_cases.groupby('HadStroke', as_index=False)['HadHeartAttack'].count()
    df_counts.rename(columns={'HadHeartAttack': 'Count_of_HadHeartAttack', 'HadStroke': 'Riwayat Stroke'}, inplace=True)
    
    # 3. Hitung Proporsi Kasus Absolut
    total_cases = df_counts['Count_of_HadHeartAttack'].sum()
    df_counts['Proporsi_Kasus (%)'] = (df_counts['Count_of_HadHeartAttack'] / total_cases * 100).round(1)

    # 4. Definisikan urutan visualisasi
    stroke_order = ['No', 'Yes']
    
    df_stroke_risk = df_counts
else:
    df_stroke_risk = pd.DataFrame(columns=['Riwayat Stroke', 'Count_of_HadHeartAttack', 'Proporsi_Kasus (%)'])

# Ganti fungsi create_bar_chart(df) di pages/sc10_stroke_risk.py

def create_bar_chart(df):
    """Membuat Bagan Kolom Proporsi Kasus Absolut (Sederhana)."""
    
    stroke_order = ['No', 'Yes']
    
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Riwayat Stroke:N', sort=stroke_order, title='Riwayat Stroke'),
        y=alt.Y('Count_of_HadHeartAttack:Q', title='Jumlah Kasus Serangan Jantung Absolut'),
        
        # Warna berdasarkan Count (Semakin Tinggi Kasus, Semakin Gelap Warna)
        color=alt.Color('Count_of_HadHeartAttack:Q', 
                        title='Kasus Absolut',
                        # <<< PERUBAHAN WARNA DI SINI >>>
                        scale=alt.Scale(scheme='yelloworangered')), 
        
        tooltip=['Riwayat Stroke', 'Count_of_HadHeartAttack', 'Proporsi_Kasus (%)'],
        text=alt.Text('Proporsi_Kasus (%):Q', format='.1f')
    ).properties(
        title='Peningkatan Risiko Penyakit Jantung akibat Riwayat Stroke'
    ).interactive()
    
    return chart

def show_page():
    """Menampilkan konten lengkap Study Case 10."""
    
    if DF_FULL is None:
        return

    st.header("Study Case 10: Riwayat Stroke vs. Risiko Serangan Jantung")
    st.markdown("---")
    
    # 1. Visualisasi Bar Chart Proporsi Kasus Absolut
    st.subheader("1. Bagan Kolom Proporsi Kasus Absolut")
    st.altair_chart(create_bar_chart(df_stroke_risk), use_container_width=True) 

    # 2. Data Rinci
    st.subheader("2. Data Rinci Kasus Absolut dan Proporsi")
    st.dataframe(df_stroke_risk, hide_index=True)
    
    # 3. Interpretasi dan Penjelasan Detail
    st.subheader("3. Interpretasi dan Kesimpulan")
    
    st.markdown("""
        ### Analisis Proporsi Kasus Absolut:
        Visualisasi ini menunjukkan seberapa besar setiap kelompok risiko berkontribusi terhadap total kasus serangan jantung yang tercatat ($13.435$ kasus).
        
        1.  **Individu tanpa riwayat stroke (`No`)** mengalami $\mathbf{10.917}$ kasus ($\mathbf{81,2\%}$ dari total) serangan jantung. Angka ini menunjukkan bahwa sebagian besar kasus berasal dari populasi umum tanpa riwayat stroke.
        2.  **Individu dengan riwayat stroke (`Yes`)** mengalami $\mathbf{2.518}$ kasus ($\mathbf{18,8\%}$). **Temuan Kunci:** Meskipun secara jumlah terlihat lebih sedikit, proporsi $\mathbf{18,8\%}$ dari total kasus di kelompok penderita stroke ini menunjukkan **tingkat risiko yang tinggi**, karena populasi yang memiliki riwayat stroke umumnya jauh lebih kecil dibandingkan kelompok tanpa stroke.
        
        3.  Hasil ini memperkuat bukti medis bahwa stroke dan penyakit jantung memiliki **faktor risiko yang saling berkaitan**, seperti tekanan darah tinggi, penyumbatan pembuluh darah, kolesterol, dan gaya hidup tidak sehat.
        
        4.  Dengan **1 dari setiap 5 kasus serangan jantung ($\mathbf{18,8\%}$) terjadi pada individu dengan riwayat stroke**, data ini menegaskan bahwa riwayat penyakit pembuluh darah otak (stroke) merupakan **indikator kuat** terhadap risiko penyakit jantung di masa depan.
        
        ### Kesimpulan:
        Data menunjukkan bahwa individu dengan riwayat stroke memiliki risiko lebih tinggi mengalami penyakit jantung dibandingkan mereka yang tidak memiliki riwayat stroke. Kedua penyakit ini memiliki hubungan erat dalam sistem kardiovaskular, sehingga penderita stroke perlu mendapatkan pengawasan ketat terhadap kesehatan jantungnya. Pencegahan sekunder seperti pengendalian tekanan darah, kolesterol, dan gaya hidup sehat menjadi sangat penting untuk menghindari serangan jantung lanjutan.
    """)