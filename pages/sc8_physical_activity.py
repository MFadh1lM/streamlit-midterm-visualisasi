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

# --- FUNGSI BARU UNTUK VISUALISASI KASUS ABSOLUT ---
def create_count_bar_chart(df):
    """Membuat Bar Chart untuk Kasus Absolut."""
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('PhysicalActivities:N', sort=['No', 'Yes'], title='Aktif Secara Fisik'),
        y=alt.Y('Case_Count:Q', title='Jumlah Kasus Absolut'),
        color=alt.Color('PhysicalActivities:N'),
        tooltip=['PhysicalActivities', 'Total_Population', 'Case_Count']
    ).properties(
        title='Perbandingan Jumlah Kasus Serangan Jantung Absolut'
    ).interactive()
    
    return chart

def create_ratio_bar_chart(df):
    """Membuat Bar Chart untuk Rasio Insiden."""
    
    # Tambahkan garis horizontal rata-rata Rasio Insiden global
    mean_ratio = df['Incidence_Ratio (%)'].mean()
    
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('PhysicalActivities:N', sort=['No', 'Yes'], title='Aktif Secara Fisik'),
        y=alt.Y('Incidence_Ratio (%):Q', title='Rasio Insiden Serangan Jantung (%)'),
        color=alt.Color('PhysicalActivities:N', legend=None),
        tooltip=['PhysicalActivities', 'Total_Population', 'Case_Count', alt.Tooltip('Incidence_Ratio (%)', format='.2f')]
    ).properties(
        title='Perbandingan Rasio Insiden (Risiko Relatif)'
    ).interactive()
    
    # Tambahkan garis rata-rata
    line = alt.Chart(pd.DataFrame({'y': [mean_ratio]})).mark_rule(color='red').encode(y='y')
    
    return chart + line


def show_page():
    """Menampilkan konten lengkap Study Case 8."""
    
    if DF_FULL is None:
        return

    st.header("Study Case 8: Aktivitas Fisik vs. Risiko Serangan Jantung")
    st.markdown("---")
    
    # 1. Visualisasi Berdampingan (Kasus Absolut vs. Rasio Insiden)
    st.subheader("1. Membandingkan Beban Kasus Absolut dan Rasio Insiden")
    
    col_count_chart, col_ratio_chart = st.columns(2)
    
    with col_count_chart:
        st.altair_chart(create_count_bar_chart(df_activity_risk), use_container_width=True)
        st.caption("Visualisasi ini menunjukkan **Kasus Absolut**.")
        
    with col_ratio_chart:
        st.altair_chart(create_ratio_bar_chart(df_activity_risk), use_container_width=True)
        st.caption("Visualisasi ini menunjukkan **Rasio Insiden (Risiko Relatif)**.")


    # 2. Data Rinci
    st.subheader("2. Data Rinci Rasio Insiden")
    st.dataframe(df_activity_risk, hide_index=True)
    
    # 3. Interpretasi dan Penjelasan Detail
    st.subheader("3. Interpretasi dan Kesimpulan")
    
    st.markdown(f"""
        ### Analisis Perbandingan: Kasus Absolut vs. Rasio Insiden

        1. **Kasus Absolut:** Grafik Kiri (Jumlah Kasus Absolut) menunjukkan bahwa kelompok **Aktif Secara Fisik** memiliki kasus lebih banyak (**{df_activity_risk[df_activity_risk['PhysicalActivities'] == 'Yes']['Case_Count'].iloc[0]:.0f} kasus**) dibandingkan kelompok **Tidak Aktif Secara Fisik** (**{df_activity_risk[df_activity_risk['PhysicalActivities'] == 'No']['Case_Count'].iloc[0]:.0f} kasus**).
        2. **Populasi:** Hal ini disebabkan karena **populasi responden yang Aktif Secara Fisik JAUH lebih besar** (**{df_activity_risk[df_activity_risk['PhysicalActivities'] == 'Yes']['Total_Population'].iloc[0]:,.0f} orang**) dibandingkan yang Tidak Aktif (**{df_activity_risk[df_activity_risk['PhysicalActivities'] == 'No']['Total_Population'].iloc[0]:,.0f} orang**).
        
        #### Temuan Kunci: Rasio Insiden (Risiko Sebenarnya)
        Rasio insiden digunakan untuk menilai **risiko relatif** dengan menormalkan jumlah kasus terhadap total populasi tiap kelompok:

    """)
    st.latex(r"""
        \text{Rasio Insiden} = \frac{\text{Jumlah Kasus Serangan Jantung}}{\text{Total Populasi Kelompok}} \times 100
    """)

    st.markdown(f"""
        Dari hasil perhitungan:
        - Rasio Insiden Kelompok **Tidak Aktif Secara Fisik** adalah **{df_activity_risk[df_activity_risk['PhysicalActivities'] == 'No']['Incidence_Ratio (%)'].iloc[0]:.2f}%**.
        - Rasio Insiden Kelompok **Aktif Secara Fisik** adalah **{df_activity_risk[df_activity_risk['PhysicalActivities'] == 'Yes']['Incidence_Ratio (%)'].iloc[0]:.2f}%**.  
        
        Hasil ini menunjukkan bahwa **Kelompok Tidak Aktif Secara Fisik memiliki Rasio Insiden (Risiko) 2 kali lipat lebih tinggi** ({df_activity_risk[df_activity_risk['PhysicalActivities'] == 'No']['Incidence_Ratio (%)'].iloc[0] / df_activity_risk[df_activity_risk['PhysicalActivities'] == 'Yes']['Incidence_Ratio (%)'].iloc[0]:.1f}x) dibandingkan kelompok Aktif.

        ### Kesimpulan Akhir
        - **Secara proporsional**, individu yang **tidak aktif secara fisik** memiliki **risiko serangan jantung JAUH lebih tinggi**.  
        - **Aktivitas fisik** terbukti memiliki efek protektif (menurunkan risiko), namun pola ini tersembunyi jika hanya melihat jumlah kasus absolut.  
        - **Pentingnya Normalisasi:** Visualisasi berdampingan ini membuktikan mengapa menggunakan **Rasio Insiden** sangat penting dalam data survei yang memiliki perbedaan besar dalam ukuran populasi antar kelompok.
    """)