import streamlit as st
import pandas as pd
import altair as alt
from data_loader import DF_FULL

df_full = DF_FULL

if df_full is not None:
    # 1. Filter kasus serangan jantung ('HadHeartAttack' == 'Yes')
    df_cases = df_full[df_full['HadHeartAttack'] == 'Yes'].copy()

    # 2. Hitung jumlah kasus per kategori CovidPos
    df_counts = df_cases.groupby('CovidPos', as_index=False)['HadHeartAttack'].count()
    df_counts.rename(columns={'HadHeartAttack': 'Count of HadHeartAttack', 'CovidPos': 'Riwayat COVID-19'}, inplace=True)

    # 3. Hitung total populasi per kategori CovidPos
    df_total = df_full.groupby('CovidPos', as_index=False)['HadHeartAttack'].count()
    df_total.rename(columns={'HadHeartAttack': 'Total Populasi', 'CovidPos': 'Riwayat COVID-19'}, inplace=True)

    # 4. Gabungkan untuk menghitung Rasio Insiden (%)
    df_merge = pd.merge(df_counts, df_total, on='Riwayat COVID-19', how='inner')
    df_merge['Rasio Insiden'] = (df_merge['Count of HadHeartAttack'] / df_merge['Total Populasi'] * 100).astype(float)

    # Urutan kategori
    covid_order = ['No', 'Tested positive using home test without a health professional', 'Yes']
    df_merge['Riwayat COVID-19'] = pd.Categorical(df_merge['Riwayat COVID-19'], categories=covid_order, ordered=True)
    df_merge = df_merge.sort_values('Riwayat COVID-19')

    df_covid_risk = df_merge
else:
    df_covid_risk = pd.DataFrame(columns=['Riwayat COVID-19', 'Count of HadHeartAttack', 'Total Populasi', 'Rasio Insiden'])


# ==== CHART UTAMA: BAR CHART JUMLAH KASUS ====
def create_bar_chart(df):
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Riwayat COVID-19:N', title='Riwayat COVID-19'),
        y=alt.Y('Count of HadHeartAttack:Q', title='Jumlah Kasus Serangan Jantung'),
        tooltip=['Riwayat COVID-19', 'Count of HadHeartAttack', 'Total Populasi']
    ).properties(
        title='Distribusi Kasus Serangan Jantung Berdasarkan Riwayat COVID-19'
    ).interactive()
    return chart


# ==== CHART TAMBAHAN: RASIO INSIDEN (%) ====
def create_ratio_chart(df):
    chart = alt.Chart(df).mark_line(point=True, color='orange', strokeWidth=3).encode(
        x=alt.X('Riwayat COVID-19:N', title='Riwayat COVID-19'),
        y=alt.Y('Rasio Insiden:Q', title='Rasio Insiden Serangan Jantung (%)'),
        tooltip=['Riwayat COVID-19', alt.Tooltip('Rasio Insiden:Q', format='.2f')]
    ).properties(
        title='Rasio Insiden Serangan Jantung Berdasarkan Riwayat COVID-19 (%)'
    ).interactive()
    return chart


# ==== TAMPILAN STREAMLIT ====
def show_page():
    if df_full is None:
        return

    st.header("Study Case 4: Infeksi COVID-19 vs. Risiko Serangan Jantung")
    st.markdown("---")

    # === Bar Chart Kasus Absolut ===
    st.subheader("1. Distribusi Kasus Serangan Jantung (Absolut)")
    st.altair_chart(create_bar_chart(df_covid_risk), use_container_width=True)

    # === Chart Rasio Insiden ===
    st.subheader("2. Rasio Insiden Serangan Jantung (%)")
    st.altair_chart(create_ratio_chart(df_covid_risk), use_container_width=True)

    # === Dataframe Detail ===
    st.subheader("3. Data Rinci")
    st.dataframe(df_covid_risk, hide_index=True)

    # === Interpretasi ===
    st.subheader("4. Interpretasi dan Kesimpulan")

    st.markdown("""
    **Langkah Analisis:**
    1. Grafik pertama menunjukkan **jumlah absolut kasus serangan jantung** berdasarkan riwayat infeksi COVID-19.  
    2. Namun angka absolut tidak memperhitungkan ukuran populasi tiap kelompok, sehingga diperlukan perhitungan **rasio insiden (%)**, menggunakan rumus:
    """)

    st.latex(r"""
        \text{Rasio Insiden (\%)} = 
        \left(
        \frac{\text{Jumlah Kasus Serangan Jantung dalam Kelompok}}{\text{Total Populasi dalam Kelompok}}
        \right) \times 100
    """)

    st.markdown("""
        **Interpretasi:**
        - Setelah dikonversi ke rasio insiden (%), terlihat bahwa kelompok dengan **riwayat COVID-19 positif** menunjukkan **persentase kasus serangan jantung sedikit lebih tinggi** dibandingkan kelompok tanpa riwayat infeksi.  
        - Artinya, **infeksi COVID-19 berpotensi menjadi faktor risiko tambahan** bagi penyakit jantung, walaupun data ini belum dapat memastikan hubungan sebab-akibat.
        - Variasi kecil antara kategori “Home Test” dan “Yes” bisa disebabkan oleh **perbedaan tingkat keparahan atau akses diagnosis**.

        **Kesimpulan Akhir:**
        - Dalam konteks data ini, **proporsi individu dengan serangan jantung meningkat seiring riwayat COVID-19 positif**.  
        - Hasil ini menunjukkan kemungkinan adanya **keterkaitan antara infeksi COVID-19 dan peningkatan risiko kardiovaskular**, yang layak dieksplorasi lebih lanjut dengan model prediktif dan kontrol variabel tambahan.
    """)
