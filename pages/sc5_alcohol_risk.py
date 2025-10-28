import streamlit as st
import pandas as pd
import altair as alt
import os

try:
    from data_loader import DF_FULL
except ImportError:
    st.error("Gagal mengimpor DF_FULL. Pastikan file data_loader.py sudah dibuat.")
    DF_FULL = None

# Fungsi pengelompokan SmokerStatus yang disederhanakan
def simplify_smoker_status(status):
    if 'Current' in status:
        return 'Current Smoker'
    elif 'Former' in status:
        return 'Former Smoker'
    elif 'Never' in status:
        return 'Never Smoked'
    return status

if DF_FULL is not None:
    df_temp = DF_FULL.copy()
    df_temp['SmokerStatusSimple'] = df_temp['SmokerStatus'].apply(simplify_smoker_status)

    # Hitung total populasi dan kasus serangan jantung
    df_pop = df_temp.groupby(['AlcoholDrinkers', 'SmokerStatusSimple'], as_index=False)['HadHeartAttack'].count().rename(columns={'HadHeartAttack': 'Total_Population'})
    df_cases = df_temp[df_temp['HadHeartAttack'] == 'Yes'].groupby(['AlcoholDrinkers', 'SmokerStatusSimple'], as_index=False)['HadHeartAttack'].count().rename(columns={'HadHeartAttack': 'Case_Count'})
    df_risk = df_pop.merge(df_cases, on=['AlcoholDrinkers', 'SmokerStatusSimple'], how='left').fillna(0)
    df_risk['Incidence_Ratio (%)'] = (df_risk['Case_Count'] / df_risk['Total_Population'] * 100).round(2)
    df_alcohol_risk = df_risk
else:
    df_alcohol_risk = pd.DataFrame(columns=['AlcoholDrinkers', 'SmokerStatusSimple', 'Total_Population', 'Case_Count', 'Incidence_Ratio (%)'])

def create_bubble_chart(df):
    color_scale = alt.Scale(scheme='orangered')
    bubble = (
        alt.Chart(df)
        .mark_circle(opacity=0.8)
        .encode(
            x=alt.X('SmokerStatusSimple:N', title='Status Merokok', sort=['Never Smoked', 'Former Smoker', 'Current Smoker']),
            y=alt.Y('AlcoholDrinkers:N', title='Konsumsi Alkohol'),
            size=alt.Size('Incidence_Ratio (%):Q', title='Rasio Serangan Jantung (%)', scale=alt.Scale(range=[100, 2000])),
            color=alt.Color('Incidence_Ratio (%):Q', scale=color_scale, legend=alt.Legend(title='Rasio Serangan Jantung (%)')),
            tooltip=['SmokerStatusSimple', 'AlcoholDrinkers', 'Total_Population', 'Case_Count', 'Incidence_Ratio (%)']
        )
        .properties(
            title="Interaksi Merokok dan Konsumsi Alkohol terhadap Risiko Serangan Jantung",
            width=700,
            height=350
        )
        .interactive()
    )
    return bubble

def show_page():
    if DF_FULL is None:
        return

    st.header("Study Case 5: Interaksi Merokok, Alkohol, dan Risiko Serangan Jantung")
    st.markdown("---")

    # 1️ Visualisasi Bubble Chart
    st.subheader("1. Visualisasi Interaktif (Bubble Chart)")
    st.info("Bubble Chart ini menggambarkan hubungan antara status merokok, kebiasaan konsumsi alkohol, dan rasio kejadian serangan jantung. Ukuran dan warna gelembung mewakili tingkat risiko yang lebih tinggi.")
    st.altair_chart(create_bubble_chart(df_alcohol_risk), use_container_width=True)

    # 2️ Data Ringkasan
    st.subheader("2. Data Ringkasan Rasio Risiko")
    st.info("Rasio Insiden dihitung sebagai: (Kasus Serangan Jantung / Total Populasi) × 100.")
    st.dataframe(df_alcohol_risk, hide_index=True, use_container_width=True)

    # 3️ Kesimpulan dan Analisis
    st.subheader("3. Interpretasi dan Kesimpulan")
    st.markdown("""
    ### **Analisis Interaksi Risiko**
    Dari visualisasi di atas, terlihat pola yang menarik:

    1. **Perokok aktif (Current Smoker)** tetap memiliki **rasio serangan jantung tertinggi**, menunjukkan bahwa merokok adalah faktor risiko dominan.
    2. Namun, pada kelompok perokok aktif, individu yang **tidak mengonsumsi alkohol** justru memiliki rasio serangan jantung **lebih tinggi (sekitar 10%)** dibandingkan peminum alkohol **(sekitar 5–6%)**.
    3. Pola serupa juga tampak pada kelompok **mantan perokok (Former Smoker)**, di mana peminum alkohol memiliki rasio sedikit lebih rendah.
    4. Pada kelompok **tidak pernah merokok (Never Smoked)**, perbedaan antara peminum dan bukan peminum relatif kecil.

    Hasil ini tampak bertolak belakang dengan dugaan umum bahwa konsumsi alkohol selalu meningkatkan risiko penyakit jantung.  
    Beberapa kemungkinan penyebabnya antara lain:

    - **Bias Gaya Hidup:** Peminum ringan (moderate drinkers) seringkali memiliki pola sosial dan aktivitas fisik yang lebih baik.
    - **Variabel Perancu:** Faktor lain seperti usia, tekanan darah, dan berat badan tidak dikontrol pada analisis ini.
    - **Efek Moderasi:** Alkohol mungkin berinteraksi dengan faktor risiko lain (misalnya rokok) dengan cara yang tidak linier.

    ---

    ### **Kesimpulan Akhir**
    Berdasarkan hasil visualisasi, **status merokok tetap menjadi faktor risiko utama serangan jantung**.  
    Namun, **pengaruh konsumsi alkohol** tidak menunjukkan peningkatan risiko yang konsisten.  
    Sebaliknya, data ini mengindikasikan bahwa **perokok non-peminum alkohol memiliki risiko sedikit lebih tinggi**, menandakan hubungan antara alkohol dan penyakit jantung **tidak sederhana dan dipengaruhi banyak faktor**.
    """)

