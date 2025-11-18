import streamlit as st
import pandas as pd
import altair as alt

try:
    from data_loader import DF_FULL
except ImportError:
    st.error("Gagal mengimpor DF_FULL. Pastikan file data_loader.py sudah dibuat.")
    DF_FULL = None

if DF_FULL is not None:
    # --- PROSES DATA ---
    df_pop = DF_FULL.groupby('HadStroke', as_index=False)['HadHeartAttack'].count().rename(columns={'HadHeartAttack': 'Total_Population'})
    df_cases = DF_FULL[DF_FULL['HadHeartAttack'] == 'Yes'].groupby('HadStroke', as_index=False)['HadHeartAttack'].count().rename(columns={'HadHeartAttack': 'Count_of_HadHeartAttack'})
    df_risk = df_pop.merge(df_cases, on='HadStroke', how='left').fillna(0)
    df_risk['Rasio_Insiden (%)'] = (df_risk['Count_of_HadHeartAttack'] / df_risk['Total_Population'] * 100).round(2)
    total_cases = df_risk['Count_of_HadHeartAttack'].sum()
    df_risk['Proporsi_Kasus (%)'] = (df_risk['Count_of_HadHeartAttack'] / total_cases * 100).round(1)
    df_risk.rename(columns={'HadStroke': 'Riwayat Stroke'}, inplace=True)
    df_stroke_risk = df_risk
    
    # Hitung Rasio Risiko Relatif
    ratio_no = df_stroke_risk[df_stroke_risk['Riwayat Stroke'] == 'No']['Rasio_Insiden (%)'].iloc[0]
    ratio_yes = df_stroke_risk[df_stroke_risk['Riwayat Stroke'] == 'Yes']['Rasio_Insiden (%)'].iloc[0]
    risk_factor = (ratio_yes / ratio_no).round(1)
else:
    df_stroke_risk = pd.DataFrame(columns=['Riwayat Stroke', 'Count_of_HadHeartAttack', 'Proporsi_Kasus (%)', 'Total_Population', 'Rasio_Insiden (%)'])
    ratio_no, ratio_yes, risk_factor = 0.0, 0.0, 0.0

# === VISUALISASI BAR CHART UNTUK KASUS ABSOLUT (FOKUS BEBAN) ===
def create_bar_chart(df):
    """Membuat Bar Chart untuk Jumlah Kasus Absolut (Beban Penyakit)."""
    stroke_order = ['No', 'Yes']
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Riwayat Stroke:N', sort=stroke_order, title='Riwayat Stroke'),
        y=alt.Y('Count_of_HadHeartAttack:Q', title='Jumlah Kasus Absolut'),
        color=alt.Color('Riwayat Stroke:N', 
                        scale=alt.Scale(range=['#B22222', '#FF8C00']),
                        legend=None),
        tooltip=['Riwayat Stroke', 'Count_of_HadHeartAttack', 'Proporsi_Kasus (%)']
    ).properties(
        title='Beban Kasus Serangan Jantung Absolut'
    ).interactive()
    return chart

# === VISUALISASI LOLLIPOP CHART UNTUK RASIO INSIDEN (FOKUS RISIKO) ===
def create_lollipop_chart(df):
    """Membuat Lollipop Chart untuk Rasio Insiden (Risiko Relatif)."""
    stroke_order = ['No', 'Yes']
    
    # Garis horizontal
    lines = alt.Chart(df).mark_rule(size=4).encode(
        x=alt.X('Rasio_Insiden (%):Q', title='Rasio Insiden (%)'),
        y=alt.Y('Riwayat Stroke:N', sort=stroke_order),
        color=alt.value('lightgray')
    )
    
    # Titik di ujung garis
    points = alt.Chart(df).mark_circle(size=200).encode(
        x='Rasio_Insiden (%):Q',
        y=alt.Y('Riwayat Stroke:N', sort=stroke_order),
        color=alt.Color('Riwayat Stroke:N', legend=None, scale=alt.Scale(range=['#B22222', '#FF8C00'])),
        tooltip=['Riwayat Stroke', alt.Tooltip('Rasio_Insiden (%)', format='.2f')]
    ).properties(
        title='Risiko Relatif (Rasio Insiden %)'
    )
    
    chart = (lines + points).interactive()
    return chart

def show_page():
    if DF_FULL is None:
        return

    st.header("Study Case 10: Riwayat Stroke vs. Risiko Serangan Jantung")
    st.markdown("---")
    
    st.subheader("1. Perbandingan Beban Kasus Absolut dan Risiko Relatif")
    
    # Tampilkan 2 visualisasi side-by-side
    col_abs, col_ratio = st.columns(2)

    with col_abs:
        st.caption("Visualisasi ini menunjukkan **BEBAN KASUS ABSOLUT**.")
        st.altair_chart(create_bar_chart(df_stroke_risk), use_container_width=True) 

    with col_ratio:
        st.caption("Visualisasi ini menunjukkan **RASIO INSIDEN (RISIKO RELATIF)**.")
        st.altair_chart(create_lollipop_chart(df_stroke_risk), use_container_width=True)

    # Data Rinci
    st.subheader("2. Data Rinci Kasus Absolut, Populasi, dan Rasio Insiden")
    st.dataframe(df_stroke_risk, hide_index=True)
    
    # Interpretasi dan Kesimpulan
    st.subheader("3. Interpretasi dan Kesimpulan")
    
    st.markdown(f"""
        ### Analisis Kuantitatif Utama

        1. **Populasi dan Kasus Absolut:**
           * Kelompok **Tanpa Stroke** (`No`) memiliki populasi **{df_stroke_risk[df_stroke_risk['Riwayat Stroke'] == 'No']['Total_Population'].iloc[0]:,.0f}** orang dan menyumbang **{df_stroke_risk[df_stroke_risk['Riwayat Stroke'] == 'No']['Count_of_HadHeartAttack'].iloc[0]:,.0f} kasus** (Grafik Kiri).
           * Kelompok **Dengan Stroke** (`Yes`) memiliki populasi **{df_stroke_risk[df_stroke_risk['Riwayat Stroke'] == 'Yes']['Total_Population'].iloc[0]:,.0f}** orang dan menyumbang **{df_stroke_risk[df_stroke_risk['Riwayat Stroke'] == 'Yes']['Count_of_HadHeartAttack'].iloc[0]:,.0f} kasus**.

        2. **Rasio Insiden (Risiko Sebenarnya):**
           * Riwayat stroke `Yes`: **{ratio_yes}%** (24.90%)
           * Tanpa riwayat stroke `No`: **{ratio_no}%** (4.63%)
        
        ### Perbandingan Risiko
        
        Hasil ini membuktikan bahwa **individu dengan riwayat stroke memiliki risiko serangan jantung sekitar {risk_factor} kali lipat lebih tinggi** dibandingkan mereka yang tidak memiliki riwayat stroke.

        $$\\text{{Faktor Risiko Relatif}} = \\frac{{\\text{{Rasio Insiden}}_{{Stroke}}}}{{\\text{{Rasio Insiden}}_{{Non-Stroke}}}} = \\frac{{{ratio_yes}\\%}}{{{ratio_no}\\%}} \\approx {risk_factor}$$

        ---
        ### Kesimpulan
        * **Korelasi Sangat Kuat:** Hasil menunjukkan **korelasi yang sangat kuat** dan substansial antara riwayat stroke dan peningkatan risiko serangan jantung, sebuah pola yang konsisten dengan literatur medis.
        * **Pentingnya Pencegahan Sekunder:** Karena risiko berlipat ganda, **pencegahan sekunder** (pengendalian tekanan darah, kolesterol, dan gaya hidup aktif) sangat penting untuk mengurangi risiko lanjutan pada penderita stroke.
    """)