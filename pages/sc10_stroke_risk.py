import streamlit as st
import pandas as pd
import altair as alt

try:
    from data_loader import DF_FULL
except ImportError:
    st.error("Gagal mengimpor DF_FULL. Pastikan file data_loader.py sudah dibuat.")
    DF_FULL = None

if DF_FULL is not None:
    # 1. Hitung Total Populasi (Denominator) untuk setiap kategori HadStroke
    df_pop = DF_FULL.groupby('HadStroke', as_index=False)['HadHeartAttack'].count().rename(columns={'HadHeartAttack': 'Total_Population'})

    # 2. Hitung Kasus Serangan Jantung (Numerator)
    df_cases = DF_FULL[DF_FULL['HadHeartAttack'] == 'Yes'].groupby('HadStroke', as_index=False)['HadHeartAttack'].count().rename(columns={'HadHeartAttack': 'Count_of_HadHeartAttack'})

    # 3. Gabungkan
    df_risk = df_pop.merge(df_cases, on='HadStroke', how='left').fillna(0)
    
    # 4. Hitung Rasio Insiden: (Kasus / Total Populasi) * 100
    df_risk['Rasio_Insiden (%)'] = (df_risk['Count_of_HadHeartAttack'] / df_risk['Total_Population'] * 100).round(2)
    
    # 5. Hitung Proporsi Kasus Absolut
    total_cases = df_risk['Count_of_HadHeartAttack'].sum()
    df_risk['Proporsi_Kasus (%)'] = (df_risk['Count_of_HadHeartAttack'] / total_cases * 100).round(1)

    df_risk.rename(columns={'HadStroke': 'Riwayat Stroke'}, inplace=True)
    
    stroke_order = ['No', 'Yes']
    df_stroke_risk = df_risk
else:
    df_stroke_risk = pd.DataFrame(columns=['Riwayat Stroke', 'Count_of_HadHeartAttack', 'Proporsi_Kasus (%)', 'Total_Population', 'Rasio_Insiden (%)'])

# === VISUALISASI BAR CHART UNTUK PROPORSI KASUS ABSOLUT ===
def create_bar_chart(df):
    stroke_order = ['No', 'Yes']
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Riwayat Stroke:N', sort=stroke_order, title='Riwayat Stroke'),
        y=alt.Y('Count_of_HadHeartAttack:Q', title='Jumlah Kasus Serangan Jantung Absolut'),
        color=alt.Color('Count_of_HadHeartAttack:Q', 
                        title='Kasus Absolut',
                        scale=alt.Scale(scheme='yelloworangered')), 
        tooltip=['Riwayat Stroke', 'Count_of_HadHeartAttack', 'Proporsi_Kasus (%)']
    ).properties(
        title='Peningkatan Risiko Penyakit Jantung akibat Riwayat Stroke'
    ).interactive()
    return chart

# === VISUALISASI LINE CHART UNTUK RASIO INSIDEN ===
def create_lollipop_chart(df):
    stroke_order = ['No', 'Yes']
    
    # Garis horizontal
    lines = alt.Chart(df).mark_rule(size=4, color='gray').encode(
        x=alt.X('Rasio_Insiden (%):Q', title='Rasio Insiden (%)'),
        y=alt.Y('Riwayat Stroke:N', sort=stroke_order)
    )
    
    # Titik di ujung garis
    points = alt.Chart(df).mark_circle(size=200, color='crimson').encode(
        x='Rasio_Insiden (%):Q',
        y=alt.Y('Riwayat Stroke:N', sort=stroke_order),
        tooltip=['Riwayat Stroke', 'Rasio_Insiden (%)']
    )
    
    chart = (lines + points).properties(
        title='Rasio Insiden (%) Serangan Jantung Berdasarkan Riwayat Stroke',
        height=300
    )
    return chart

def show_page():
    if DF_FULL is None:
        return

    st.header("Study Case 10: Riwayat Stroke vs. Risiko Serangan Jantung")
    st.markdown("---")
    
    # Visualisasi Kasus Absolut
    st.subheader("1. Bagan Kolom Kontribusi Kasus Absolut")
    st.altair_chart(create_bar_chart(df_stroke_risk), use_container_width=True) 

    # Visualisasi Rasio Insiden
    st.subheader("2. Perbandingan Rasio Insiden Serangan Jantung")
    st.altair_chart(create_lollipop_chart(df_stroke_risk), use_container_width=True)

    # Data Rinci
    st.subheader("3. Data Rinci Kasus Absolut, Populasi, dan Rasio Insiden")
    st.dataframe(df_stroke_risk, hide_index=True)
    
    # Interpretasi dan Kesimpulan
    st.subheader("4. Interpretasi dan Kesimpulan")
    
    ratio_no = df_stroke_risk[df_stroke_risk['Riwayat Stroke'] == 'No']['Rasio_Insiden (%)'].iloc[0]
    ratio_yes = df_stroke_risk[df_stroke_risk['Riwayat Stroke'] == 'Yes']['Rasio_Insiden (%)'].iloc[0]
    risk_factor = (ratio_yes / ratio_no).round(1)
    
    st.markdown(f"""
        ### Rumus Perhitungan
        $$Rasio\\ Insiden(\\%) = \\frac{{Jumlah\\ Kasus\\ Serangan\\ Jantung}}{{Total\\ Populasi}} \\times 100$$

        ---
        ### Analisis Korelasi Kuat: Rasio Insiden

        Visualisasi di atas menampilkan bagaimana **riwayat stroke** berhubungan dengan risiko serangan jantung.

        #### Temuan Kunci:
        1. **Proporsi Kasus:** Individu tanpa stroke (`No`) menyumbang sebagian besar kasus serangan jantung karena populasinya jauh lebih besar.
        2. **Rasio Insiden:**
           * Riwayat stroke `Yes`: sekitar **{ratio_yes}%**
           * Tanpa riwayat stroke `No`: sekitar **{ratio_no}%**
        3. **Perbandingan Risiko:** Risiko serangan jantung pada individu dengan riwayat stroke adalah **{risk_factor} kali lipat** lebih tinggi.

        ---
        ### Kesimpulan
        Hasil menunjukkan **korelasi yang sangat kuat** antara riwayat stroke dan peningkatan risiko serangan jantung.
        Faktor risiko umum seperti **tekanan darah tinggi dan kolesterol** memperkuat hubungan ini.
        
        **Pencegahan sekunder** seperti pengendalian tekanan darah, diet sehat, dan pemantauan kardiovaskular sangat penting untuk mengurangi risiko lanjutan pada penderita stroke.
    """)
