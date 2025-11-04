import streamlit as st
import pandas as pd
import plotly.express as px # <<< Import Plotly Express
import altair as alt # Tetap dipertahankan jika dibutuhkan library lain

try:
    from data_loader import DF_FULL
except ImportError:
    st.error("Gagal mengimpor DF_FULL. Pastikan file data_loader.py sudah dibuat.")
    DF_FULL = None

if DF_FULL is not None:
    # 1. Hitung Total Populasi (Denominator)
    df_pop = DF_FULL.groupby(['SmokerStatus', 'ECigaretteUsage'], as_index=False)['HadHeartAttack'].count().rename(columns={'HadHeartAttack': 'Total_Population'})

    # 2. Hitung Kasus Serangan Jantung (Numerator)
    df_cases = DF_FULL[DF_FULL['HadHeartAttack'] == 'Yes'].groupby(['SmokerStatus', 'ECigaretteUsage'], as_index=False)['HadHeartAttack'].count().rename(columns={'HadHeartAttack': 'Case_Count'})

    # 3. Gabungkan dan Hitung Rasio Insiden
    df_risk = df_pop.merge(df_cases, on=['SmokerStatus', 'ECigaretteUsage'], how='left').fillna(0)
    df_risk['Incidence_Ratio (%)'] = (df_risk['Case_Count'] / df_risk['Total_Population'] * 100).round(2)
    
    df_smoking_risk = df_risk
else:
    df_smoking_risk = pd.DataFrame(columns=['SmokerStatus', 'ECigaretteUsage', 'Total_Population', 'Case_Count', 'Incidence_Ratio (%)'])

def create_grouped_bar_chart_plotly(df):
    """Membuat Grouped Bar Chart Interaktif menggunakan Plotly Express."""
    
    # 1. Definisikan Urutan (untuk Sumbu X)
    smoker_order = ['Never smoked', 'Former smoker', 'Current smoker - now smokes some days', 'Current smoker - now smokes every day']

    # 2. Buat Plotly Chart
    fig = px.bar(
        df,
        x='SmokerStatus', 
        y='Incidence_Ratio (%)', 
        color='ECigaretteUsage', # Variabel untuk mengelompokkan
        barmode='group',        # Mode grouping (batang berdampingan)
        text_auto='.2f',        # Menambahkan label teks di atas batang (otomatis Plotly)
        category_orders={"SmokerStatus": smoker_order},
        labels={
            "SmokerStatus": "Status Merokok Tradisional", 
            "ECigaretteUsage": "Penggunaan Vape/E-Cig"
        },
        title="Rasio Insiden Serangan Jantung: Merokok Tradisional vs Penggunaan Vape/E-Cig"
    )

    # 3. Perbaiki Layout (Opsional: Membuat visual lebih rapi)
    fig.update_traces(textposition='outside')
    fig.update_layout(xaxis_title="Status Merokok Tradisional", 
                      yaxis_title="Rasio Insiden Serangan Jantung (%)",
                      # Mengatur angle label sumbu X agar tidak bertumpuk
                      xaxis={'tickangle': 45}, 
                      legend_title="Penggunaan Vape")
    
    return fig

def show_page():
    """Menampilkan konten lengkap Study Case 6."""
    
    if DF_FULL is None:
        return

    st.header("Study Case 6: Merokok Tradisional vs. Penggunaan Vape/E-Cigarette (Rasio Insiden)")
    st.markdown("---")
    
    # 1. Visualisasi (Plotly)
    st.subheader("1. Bagan Kolom Berkelompok Interaktif (Plotly Express)")
    st.info("Visualisasi ini membandingkan Rasio Insiden (Risiko Relatif) per kategori kebiasaan merokok dan penggunaan vape.")
    st.plotly_chart(create_grouped_bar_chart_plotly(df_smoking_risk), use_container_width=True) # <<< Menggunakan st.plotly_chart

    # 2. Data Rinci
    st.subheader("2. Data Rinci Rasio Insiden")
    st.info("Rasio Insiden dihitung sebagai: (Kasus Serangan Jantung / Total Populasi) * 100")
    st.dataframe(df_smoking_risk, hide_index=True, use_container_width=True)
    
    # 3. Interpretasi dan Penjelasan Detail
    st.subheader("3. Interpretasi dan Kesimpulan")
    
    st.markdown("""
        ### Analisis Interaksi Risiko:
        Analisis ini membandingkan Rasio Insiden untuk mengukur risiko per kapita.
    """)
    
    # Menggunakan st.latex() untuk menampilkan rumus dengan format yang benar
    st.latex(r"""
        \text{Rasio Insiden} = \frac{\text{Kasus Serangan Jantung}}{\text{Total Populasi}} \times 100
    """)


    st.markdown("""
        ### Interpretasi:
        * **Faktor Merokok Tradisional Dominan:** Risiko serangan jantung tertinggi terjadi pada kelompok yang **merokok secara aktif maupun mantan perokok**.
        * **Pengaruh Vape Tidak Linier:** Penggunaan vape tampak tidak selalu meningkatkan risiko secara langsung — hal ini mungkin dipengaruhi oleh faktor usia, perilaku kesehatan lain, atau bias pengisian survei.
        * **Keterbatasan Analisis:** Studi ini bersifat observasional dan tidak membuktikan hubungan sebab-akibat (*causality*), melainkan menunjukkan pola asosiasi.

        ### Kesimpulan
        * **Rokok tradisional tetap menjadi faktor risiko utama serangan jantung.** Mantan perokok dan perokok aktif menunjukkan risiko yang jauh lebih tinggi dibandingkan individu yang tidak pernah merokok.
        * **Efek rokok elektrik masih belum konsisten.** Walaupun beberapa kelompok pengguna vape menunjukkan rasio insiden lebih rendah, hal ini kemungkinan besar dipengaruhi oleh perbedaan karakteristik demografis dan kesehatan populasi.
        * Temuan ini menegaskan pentingnya **pengendalian kebiasaan merokok tradisional** sebagai prioritas utama dalam pencegahan penyakit jantung.
    """)