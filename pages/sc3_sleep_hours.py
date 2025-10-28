import streamlit as st
import pandas as pd
import altair as alt
from data_loader import DF_FULL

df_full = DF_FULL

if df_full is not None:
    # 1. Filter kasus serangan jantung ('HadHeartAttack' == 'Yes')
    df_cases = df_full[df_full['HadHeartAttack'] == 'Yes'].copy()

    # 2. Kelompokkan berdasarkan SleepHours dan hitung Count of HadHeartAttack
    df_counts = df_cases.groupby('SleepHours', as_index=False)['HadHeartAttack'].count()
    df_counts.rename(columns={'HadHeartAttack': 'Count of HadHeartAttack'}, inplace=True)

    # 3. Urutkan berdasarkan jam tidur untuk visualisasi line chart
    df_counts = df_counts.sort_values(by='SleepHours')
    
    # 4. Hitung Total untuk tabel
    total_cases = df_counts['Count of HadHeartAttack'].sum()
    df_counts['Persentase Kasus (%)'] = (df_counts['Count of HadHeartAttack'] / total_cases * 100).round(2)
    
    df_sleep_risk = df_counts
else:
    df_sleep_risk = pd.DataFrame(columns=['SleepHours', 'Count of HadHeartAttack', 'Persentase Kasus (%)'])

def create_line_chart(df):
    """Membuat Line Chart Count of HadHeartAttack vs SleepHours."""
    
    chart = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X('SleepHours:Q', title='Durasi Tidur (Jam)', scale=alt.Scale(domain=[1, 12])), # Batasi sumbu X agar tidak terlalu lebar
        y=alt.Y('Count of HadHeartAttack:Q', title='Jumlah Kasus Serangan Jantung'),
        tooltip=['SleepHours', 'Count of HadHeartAttack']
    ).properties(
        title='Batas Waktu Tidur per Malam yang Dapat Meningkatkan Risiko Serangan Jantung'
    ).interactive()
    
    return chart

def show_page():
    """Menampilkan konten lengkap Study Case 3."""
    
    if df_full is None:
        return

    st.header("Study Case 3: Durasi Tidur per Malam vs. Risiko Serangan Jantung")
    st.markdown("---")
    
    # 1. Visualisasi
    st.subheader("1. Line Chart Distribusi Kasus Berdasarkan Durasi Tidur")
    st.altair_chart(create_line_chart(df_sleep_risk), use_container_width=True) 

    # 2. Data Rinci
    st.subheader("2. Data Rinci Jumlah Kasus per Jam Tidur")
    st.dataframe(df_sleep_risk, hide_index=True)
    
    # 3. Interpretasi dan Penjelasan Detail
    st.subheader("3. Interpretasi dan Kesimpulan")
    
    st.markdown("""
        ### Analisis Kasus Tertinggi:
        Dari diagram garis dan tabel, terlihat bahwa **tiga durasi tidur teratas** yang memiliki jumlah kasus serangan jantung tertinggi adalah:
        
        * **8 jam:** $\mathbf{3.815}$ kasus (Puncak)
        * **7 jam:** $\mathbf{2.926}$ kasus
        * **6 jam:** $\mathbf{2.831}$ kasus
        
        ### Interpretasi Kontekstual:
        
        Menurut artikel kesehatan (misalnya, Halodoc), rekomendasi jam tidur optimal untuk orang dewasa adalah $\mathbf{7-9}$ jam.
        
        * Fakta bahwa kasus serangan jantung paling banyak terjadi pada durasi $\mathbf{6-8}$ jam tidak berarti durasi tidur ini **menyebabkan** risiko.
        * Sebaliknya, ini menunjukkan bahwa **mayoritas responden dalam *dataset* ini** (baik yang sakit maupun yang sehat) **memang tidur dalam rentang waktu yang direkomendasikan** (populasi umum).
        
        ### Kesimpulan
        Data batas waktu tidur absolut **TIDAK berkaitan langsung dengan meningkatnya risiko serangan jantung**; kasus serangan jantung hanya cenderung terjadi pada durasi tidur yang paling umum dan normal bagi populasi dewasa ($\mathbf{6-8}$ jam). Visualisasi ini tidak memberikan bukti bahwa tidur $7-8$ jam meningkatkan risiko.
    """)