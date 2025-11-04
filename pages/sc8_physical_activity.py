import streamlit as st
import pandas as pd
import altair as alt

try:
    from data_loader import DF_FULL
except ImportError:
    st.error("Gagal mengimpor DF_FULL. Pastikan file data_loader.py sudah dibuat.")
    DF_FULL = None

if DF_FULL is not None:
    # 1. Hitung Total Populasi (Denominator)
    df_pop = DF_FULL.groupby('PhysicalActivities', as_index=False)['HadHeartAttack'].count().rename(columns={'HadHeartAttack': 'Total_Population'})

    # 2. Hitung Kasus Serangan Jantung (Numerator)
    df_cases = DF_FULL[DF_FULL['HadHeartAttack'] == 'Yes'].groupby('PhysicalActivities', as_index=False)['HadHeartAttack'].count().rename(columns={'HadHeartAttack': 'Case_Count'})

    # 3. Gabungkan dan Hitung Rasio Insiden
    df_risk = df_pop.merge(df_cases, on='PhysicalActivities', how='left').fillna(0)
    
    # Rasio Insiden: (Kasus / Total Populasi) * 100
    df_risk['Incidence_Ratio (%)'] = (df_risk['Case_Count'] / df_risk['Total_Population'] * 100).round(2)
    
    df_activity_risk = df_risk
else:
    df_activity_risk = pd.DataFrame(columns=['PhysicalActivities', 'Total_Population', 'Case_Count', 'Incidence_Ratio (%)'])

def create_ratio_bar_chart(df):
    """Membuat Bar Chart untuk Rasio Insiden."""
    
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('PhysicalActivities:N', sort=['No', 'Yes'], title='Aktif Secara Fisik'),
        y=alt.Y('Incidence_Ratio (%):Q', title='Rasio Insiden Serangan Jantung (%)'),
        color=alt.Color('PhysicalActivities:N'),
        tooltip=['PhysicalActivities', 'Total_Population', 'Case_Count', alt.Tooltip('Incidence_Ratio (%)', format='.2f')]
    ).properties(
        title='Perbandingan Rasio Insiden Serangan Jantung Berdasarkan Aktivitas Fisik'
    ).interactive()
    
    return chart

def show_page():
    """Menampilkan konten lengkap Study Case 8."""
    
    if DF_FULL is None:
        return

    st.header("Study Case 8: Aktivitas Fisik vs. Risiko Serangan Jantung")
    st.markdown("---")
    
    # 1. Visualisasi Rasio Insiden
    st.subheader("1. Rasio Insiden (Risiko Relatif) per Kelompok Populasi")
    st.altair_chart(create_ratio_bar_chart(df_activity_risk), use_container_width=True) 

    # 2. Data Rinci
    st.subheader("2. Data Rinci Rasio Insiden")
    st.dataframe(df_activity_risk, hide_index=True)
    
    # 3. Interpretasi dan Penjelasan Detail
    st.subheader("3. Interpretasi dan Kesimpulan")

    st.markdown("""
        ### Analisis Perbandingan: Kasus Absolut vs. Rasio Insiden

        Data absolut menunjukkan bahwa jumlah kasus serangan jantung lebih banyak terjadi pada kelompok **Aktif Secara Fisik** (≈8.514 kasus) dibandingkan dengan kelompok **Tidak Aktif Secara Fisik** (≈4.921 kasus). Namun, nilai absolut ini **tidak memperhitungkan perbedaan jumlah populasi** di tiap kelompok.

        #### Temuan Kunci: Rasio Insiden
        Rasio insiden digunakan untuk menilai **risiko relatif** dengan menormalkan jumlah kasus terhadap total populasi tiap kelompok, menggunakan rumus:

    """)
    st.latex(r"""
        \text{Rasio Insiden} = \frac{\text{Jumlah Kasus Serangan Jantung}}{\text{Total Populasi Kelompok}} \times 100
    """)

    st.markdown("""
        Dari hasil perhitungan:
        - **Kelompok Tidak Aktif Secara Fisik** memiliki rasio insiden lebih tinggi dibandingkan kelompok aktif.  
        - Ini menunjukkan bahwa **aktivitas fisik masih berperan sebagai faktor protektif terhadap risiko penyakit jantung**, walaupun jumlah kasus absolut tampak lebih tinggi pada kelompok aktif (karena populasi aktif lebih besar).

        ### Interpretasi Tambahan
        1. **Perbedaan populasi** sangat berpengaruh — lebih banyak orang aktif secara fisik dalam dataset, sehingga jumlah kasus absolut mereka juga lebih tinggi.  
        2. **Rasio insiden** memberi gambaran risiko yang sebenarnya: proporsi orang aktif yang terkena serangan jantung lebih kecil daripada yang tidak aktif.  
        3. **Kualitas aktivitas fisik** juga berperan — aktivitas ringan atau tidak rutin mungkin tidak cukup memberikan efek protektif yang kuat.  
        4. Terdapat potensi **bias pelaporan** — responden yang sudah memiliki riwayat penyakit jantung bisa mulai lebih aktif setelah sakit (reverse causality).

        ### Kesimpulan Akhir
        - **Secara proporsional**, individu yang **tidak aktif secara fisik** memiliki **risiko serangan jantung lebih tinggi**.  
        - **Aktivitas fisik** tetap terbukti memiliki efek protektif, tetapi efektivitasnya dapat bervariasi tergantung intensitas dan konsistensinya.  
        - Pencegahan penyakit jantung perlu bersifat **komprehensif**, mencakup gaya hidup aktif, diet sehat, kontrol stres, dan pemeriksaan medis rutin.
    """)
