import streamlit as st
import pandas as pd
import altair as alt
from data_loader import DF_FULL

df_full = DF_FULL

if df_full is not None:
    # 1. Filter kasus serangan jantung ('HadHeartAttack' == 'Yes')
    df_cases = df_full[df_full['HadHeartAttack'] == 'Yes'].copy()

    # 2. Hitung Count of HadHeartAttack berdasarkan CovidPos
    df_counts = df_cases.groupby('CovidPos', as_index=False)['HadHeartAttack'].count()
    df_counts.rename(columns={'HadHeartAttack': 'Count of HadHeartAttack', 'CovidPos': 'Riwayat COVID-19'}, inplace=True)

    # Urutan visualisasi: No, Home Test, Yes (menggunakan data dari gambar yang Anda berikan)
    covid_order = ['No', 'Tested positive using home test without a health professional', 'Yes']
    df_counts['Riwayat COVID-19'] = pd.Categorical(df_counts['Riwayat COVID-19'], categories=covid_order, ordered=True)
    df_counts = df_counts.sort_values('Riwayat COVID-19')
    
    df_covid_risk = df_counts
else:
    df_covid_risk = pd.DataFrame(columns=['Riwayat COVID-19', 'Count of HadHeartAttack'])

def create_bar_chart(df):
    """Membuat Bar Chart Count of HadHeartAttack vs Riwayat COVID-19."""
    
    covid_order = ['No', 'Tested positive using home test without a health professional', 'Yes']
    
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Riwayat COVID-19:N', sort=covid_order, title='Riwayat COVID-19'),
        y=alt.Y('Count of HadHeartAttack:Q', title='Jumlah Kasus Serangan Jantung'),
        tooltip=['Riwayat COVID-19', 'Count of HadHeartAttack']
    ).properties(
        title='Distribusi Kasus Serangan Jantung Berdasarkan Riwayat COVID-19'
    ).interactive()
    
    return chart

def show_page():
    """Menampilkan konten lengkap Study Case 4."""
    
    if df_full is None:
        return

    st.header("Study Case 4: Infeksi COVID-19 vs. Risiko Serangan Jantung")
    st.markdown("---")
    
    # 1. Visualisasi
    st.subheader("1. Bar Chart Kasus Absolut vs. Riwayat COVID-19")
    st.altair_chart(create_bar_chart(df_covid_risk), use_container_width=True) 

    # 2. Data Rinci
    st.subheader("2. Data Rinci Jumlah Kasus Absolut")
    st.dataframe(df_covid_risk, hide_index=True)
    
    # 3. Interpretasi dan Penjelasan Detail
    st.subheader("3. Interpretasi dan Kesimpulan Kritis")
    
    st.markdown("""
        ### Kesimpulan:
        
        Pernyataan bahwa "infeksi COVID-19 tidak mempengaruhi risiko penyakit jantung" adalah **interpretasi yang terlalu sederhana** dari data absolut:
        
        1.  **Bukti Tidak Cukup:** Bar chart ini **TIDAK dapat membuktikan** apakah COVID-19 menaikkan atau menurunkan risiko serangan jantung karena kita tidak memiliki **total populasi** di setiap kategori COVID-19 (yaitu, berapa banyak orang yang 'Yes' vs 'No' di total *dataset*).
        
        2.  **Kebutuhan Data Lanjut:** Untuk menentukan pengaruh, kita perlu membandingkan **Rasio Serangan Jantung (Insiden)**, yang didefinisikan sebagai:
    """)

    # Menggunakan st.latex() untuk memastikan rumus tampil dengan benar
    st.latex(r"""
        \text{Rasio Insiden} = \frac{\text{Kasus Serangan Jantung dalam Kelompok}}{\text{Total Populasi dalam Kelompok}}
    """)

    st.markdown("""
        3.  **Kesimpulan Final:** Berdasarkan data kasus absolut ini, kita hanya dapat menyimpulkan bahwa **mayoritas kasus serangan jantung** dalam *dataset* ini terjadi pada orang yang **tidak memiliki riwayat COVID-19**—sebuah refleksi dari distribusi populasi umum.
    """)