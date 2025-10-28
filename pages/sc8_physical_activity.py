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
        
        Data absolut (tanpa normalisasi) menunjukkan bahwa kasus serangan jantung lebih banyak terjadi pada kelompok **Aktif Secara Fisik** ($8.514$ kasus) dibandingkan dengan yang **Tidak Aktif** ($4.921$ kasus). Ini adalah hasil yang kontradiktif.
        
        #### Temuan Kunci (Rasio Insiden):
        
        1.  **Risiko Relatif:** Rasio Insiden (yang didefinisikan di bawah) yang ditampilkan pada Bar Plot adalah metrik risiko yang benar setelah dinormalisasi terhadap populasi setiap kelompok.
    """)
    
    # <<< GUNAKAN st.latex() UNTUK RUMUS RUMIT >>>
    st.latex(r"""
        \text{Rasio Insiden} = \frac{\text{Kasus}}{\text{Total Populasi}}
    """)
    # <<< AKHIR st.latex() >>>

    st.markdown("""
        2.  **Koreksi Asumsi:** Jika ternyata Rasio Insiden untuk kelompok **Aktif Secara Fisik** tidak jauh berbeda, ini menguatkan bahwa aktivitas fisik yang dilaporkan mungkin **tidak cukup intens** atau **terdapat bias data/pelaporan** (misalnya, responden yang sakit baru mulai aktif).

        ### Kesimpulan:
        
        **1. Sebagian besar responden yang mengalami serangan jantung berasal dari kelompok yang melaporkan dirinya aktif secara fisik.**
        
        **2. Temuan ini tampak kontradiktif dengan asumsi umum, karena seharusnya aktivitas fisik berperan melindungi jantung.**
        
        **3. Alasan Kontradiksi:**
        * Data "aktif secara fisik" mungkin hanya menggambarkan **aktivitas ringan atau tidak teratur** yang tidak cukup untuk proteksi jantung.
        * Responden aktif mungkin sudah memiliki **risiko jantung/usia lanjut** yang lebih tinggi (bias).
        * Ada kemungkinan **bias pelaporan** — individu yang sakit mulai aktif setelah kejadian.
        
        **Kesimpulan Akhir:** Aktivitas fisik saja tidak cukup; pencegahan penyakit jantung harus dilakukan secara **menyeluruh** dengan mengelola faktor risiko lain (usia, merokok, stres) dan pemeriksaan kesehatan rutin.
    """)