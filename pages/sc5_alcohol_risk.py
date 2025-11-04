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
    st.subheader("1. Visualisasi Bubble Chart")
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
        Berdasarkan tabel dan visualisasi di atas, dapat diamati beberapa pola penting mengenai hubungan antara **kebiasaan merokok**, **konsumsi alkohol**, dan **risiko serangan jantung**:

        1. **Kelompok perokok aktif (Current Smoker)** yang **tidak mengonsumsi alkohol** memiliki **rasio serangan jantung tertinggi**, yaitu sekitar **10.36%**.
        2. Menariknya, **mantan perokok (Former Smoker)** tanpa alkohol bahkan memiliki rasio sedikit **lebih tinggi (11.07%)** dibanding perokok aktif tanpa alkohol.  
        Ini bisa menunjukkan bahwa efek risiko merokok masih bertahan lama bahkan setelah berhenti.
        3. Pada kelompok yang **mengonsumsi alkohol**, rasio insiden lebih **rendah secara konsisten** di semua kategori perokok — contohnya hanya **5.77% pada perokok aktif** dan **6.04% pada mantan perokok**.
        4. Kelompok **tidak pernah merokok (Never Smoked)** tetap memiliki risiko paling rendah, dengan rasio **sekitar 2.55–5.08%**, tergantung konsumsi alkohol.

        ---
        ### **Rumus Perhitungan Rasio Insiden**
    """)

    st.latex(r"""
        ext{Rasio Insiden (\%)} = 
        \frac{\text{Jumlah Kasus Serangan Jantung}}{\text{Total Populasi}} \times 100
    """)

    st.markdown("""
        Contoh perhitungan untuk kelompok *Current Smoker tanpa alkohol*:
    """)

    st.latex(r"""
        \frac{1438}{13875} \times 100 = 10.36\%
    """)

    st.markdown("""
        ---
        ### **Interpretasi Lanjutan**
        Hasil ini memberikan gambaran bahwa:
        - **Merokok tetap menjadi faktor risiko dominan** terhadap serangan jantung, bahkan setelah berhenti merokok.
        - **Konsumsi alkohol tidak selalu meningkatkan risiko**; pada beberapa kelompok justru terlihat sedikit menurunkan rasio insiden.  
        Namun, hal ini **tidak dapat diartikan sebagai efek protektif**, karena bisa dipengaruhi oleh:
            - Perbedaan usia dan kesehatan umum antar kelompok.
            - Perilaku hidup lain seperti olahraga dan pola makan.
            - Bias pelaporan dalam survei (underreporting konsumsi alkohol).

        ---
        ### **Kesimpulan Akhir**
        1. **Mantan perokok tanpa alkohol memiliki rasio serangan jantung tertinggi (11.07%)**, disusul perokok aktif tanpa alkohol (10.36%).  
        2. **Konsumsi alkohol tampak berkorelasi dengan penurunan rasio insiden**, namun efek ini kemungkinan dipengaruhi faktor lain.
        3. Secara keseluruhan, **merokok—baik aktif maupun riwayat sebelumnya—tetap merupakan faktor risiko paling kuat terhadap penyakit jantung**.  
        4. Temuan ini menegaskan pentingnya **intervensi berhenti merokok dan promosi gaya hidup sehat** sebagai strategi pencegahan utama.
    """)


