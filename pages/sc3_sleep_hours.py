import streamlit as st
import pandas as pd
import altair as alt
from data_loader import DF_FULL

df_full = DF_FULL

if df_full is not None:
    # --- 1. Hitung Total Populasi (Denominator) ---
    df_pop = df_full.groupby('SleepHours', as_index=False)['HadHeartAttack'].count().rename(
        columns={'HadHeartAttack': 'Total_Population'}
    )

    # --- 2. Hitung Kasus Serangan Jantung (Numerator) ---
    df_cases = df_full[df_full['HadHeartAttack'] == 'Yes'].groupby('SleepHours', as_index=False)['HadHeartAttack'].count().rename(
        columns={'HadHeartAttack': 'Case_Count'}
    )

    # --- 3. Gabungkan dan Hitung Rasio Insiden ---
    df_risk = df_pop.merge(df_cases, on='SleepHours', how='left').fillna(0)
    df_risk['Incidence_Ratio (%)'] = (df_risk['Case_Count'] / df_risk['Total_Population'] * 100).round(2)

    # --- 4. Sortir Berdasarkan Durasi Tidur ---
    df_risk = df_risk.sort_values(by='SleepHours')

    df_sleep_risk = df_risk
else:
    df_sleep_risk = pd.DataFrame(columns=['SleepHours', 'Total_Population', 'Case_Count', 'Incidence_Ratio (%)'])


# --- Fungsi Visualisasi 1: Jumlah Kasus Absolut ---
def create_case_line_chart(df):
    chart = (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x=alt.X('SleepHours:Q', title='Durasi Tidur (Jam)', scale=alt.Scale(domain=[1, 12])),
            y=alt.Y('Case_Count:Q', title='Jumlah Kasus Serangan Jantung'),
            tooltip=['SleepHours', 'Case_Count']
        )
        .properties(title='Distribusi Jumlah Kasus Serangan Jantung Berdasarkan Durasi Tidur')
        .interactive()
    )
    return chart


# --- Fungsi Visualisasi 2: Rasio Insiden ---
def create_ratio_line_chart(df):
    chart = (
        alt.Chart(df)
        .mark_line(point=True, color='orange')
        .encode(
            x=alt.X('SleepHours:Q', title='Durasi Tidur (Jam)', scale=alt.Scale(domain=[1, 12])),
            y=alt.Y('Incidence_Ratio (%):Q', title='Rasio Insiden Serangan Jantung (%)'),
            tooltip=['SleepHours', 'Incidence_Ratio (%)']
        )
        .properties(title='Rasio Insiden Serangan Jantung Berdasarkan Durasi Tidur (Per 100 Individu)')
        .interactive()
    )
    return chart


# --- Fungsi Utama Halaman ---
def show_page():
    if df_full is None:
        return

    st.header("Study Case 3: Durasi Tidur per Malam vs. Risiko Serangan Jantung")
    st.markdown("---")

    # --- Visualisasi 1 ---
    st.subheader("1. Distribusi Kasus Absolut")
    st.altair_chart(create_case_line_chart(df_sleep_risk), use_container_width=True)

    # --- Visualisasi 2 ---
    st.subheader("2. Rasio Insiden (Normalized per Populasi)")
    st.info("Rasio Insiden dihitung sebagai: (Jumlah Kasus / Total Populasi) × 100")
    st.altair_chart(create_ratio_line_chart(df_sleep_risk), use_container_width=True)

    # --- Data Tabel ---
    st.subheader("3. Data Rinci Per Durasi Tidur")
    st.dataframe(df_sleep_risk, hide_index=True, use_container_width=True)

    # --- Interpretasi & Kesimpulan ---
    st.subheader("4. Interpretasi dan Kesimpulan")

    st.markdown("""
        ### **Analisis Distribusi Kasus**
        Berdasarkan grafik pertama, jumlah kasus serangan jantung tertinggi tercatat pada kelompok dengan durasi tidur **6 hingga 8 jam**, 
        dengan puncak pada **8 jam**. Hal ini menunjukkan bahwa mayoritas responden yang mengalami serangan jantung 
        berada dalam rentang jam tidur yang umum dijumpai pada populasi dewasa.

        Namun, jumlah kasus yang tinggi tidak selalu berarti risiko yang lebih besar, 
        karena kelompok dengan durasi tidur tersebut juga merupakan kelompok dengan jumlah populasi terbesar.
    """)

    st.markdown("---")
    st.markdown("### **Analisis Rasio Insiden**")
    st.latex(r"""
        \text{Rasio Insiden (\%)} = 
        \left(
        \frac{\text{Jumlah Kasus Serangan Jantung pada Durasi Tidur Tertentu}}{\text{Total Populasi dengan Durasi Tidur Tersebut}}
        \right) \times 100
    """)

    st.markdown("""
        Ketika jumlah kasus dinormalisasi menjadi rasio insiden, terlihat bahwa **pola rasio tidak sepenuhnya mengikuti jumlah kasus absolut**.
        Beberapa kelompok dengan populasi kecil dapat memiliki rasio insiden lebih tinggi meskipun jumlah kasusnya sedikit.

        Dari pola ini dapat diamati:
        - **Tidur terlalu sedikit (≤5 jam)** atau **terlalu lama (≥10 jam)** cenderung memiliki rasio insiden yang relatif lebih tinggi.  
        - Sementara durasi tidur **6–8 jam** menunjukkan rasio insiden yang lebih stabil dan relatif rendah.
    """)

    st.markdown("---")
    st.markdown("""
    ### **Kesimpulan**
        1. Durasi tidur 6–8 jam merupakan kelompok paling umum dan menunjukkan jumlah kasus tertinggi secara absolut.  
        2. Setelah dinormalisasi, terlihat bahwa risiko relatif meningkat pada kelompok dengan tidur sangat singkat atau sangat panjang.  
        3. Artinya, **baik kekurangan maupun kelebihan waktu tidur dapat dikaitkan dengan kecenderungan risiko lebih tinggi**, 
        sedangkan durasi sedang (6–8 jam) menunjukkan proporsi insiden yang paling stabil.  
        4. Kesimpulan ini diperoleh murni berdasarkan distribusi dan perbandingan antar kelompok dalam dataset tanpa mengacu pada sumber eksternal.
    """)
