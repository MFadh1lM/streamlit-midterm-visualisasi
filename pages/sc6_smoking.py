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
        ### Analisis Interaksi Risiko (Berdasarkan Data Aktual):
        Analisis ini membandingkan Rasio Insiden untuk mengukur risiko per kapita.
    """)
    
    # Menggunakan st.latex() untuk menampilkan rumus dengan format yang benar
    st.latex(r"""
        \text{Rasio Insiden} = \frac{\text{Kasus Serangan Jantung}}{\text{Total Populasi}}
    """)


    st.markdown("""
        #### Temuan Kunci Baru:
        1.  **Risiko Puncak Mutlak:** Rasio Insiden tertinggi ($ \mathbf{9.14\%} $) berada pada kelompok **Perokok Harian Saat Ini** yang **TIDAK PERNAH menggunakan rokok elektrik dalam hidupnya**.
        2.  **Former Smoker Risiko Tinggi:** Kelompok **Former Smoker** yang **Tidak Pernah Menggunakan Vape** juga menunjukkan risiko yang sangat tinggi ($ \mathbf{8.94\%} $), hampir menyamai risiko puncak.
        3.  **Efek Vape yang Tidak Jelas:** Pada kelompok perokok harian, rasio insiden justru **lebih rendah** pada pengguna vape (*Use them every day* $\mathbf{7.76\%}$) dibandingkan non-pengguna vape ($ \mathbf{9.14\%} $). Ini menguatkan kesimpulan bahwa hubungan antara rokok elektrik dan serangan jantung tidak linier dan dipengaruhi bias data yang kuat.

        #### Interpretasi:
        * **Faktor Merokok Tradisional Dominan:** Terbukti bahwa risiko serangan jantung tertinggi terkonsentrasi pada kelompok yang **merokok secara tradisional** (aktif atau mantan).
        * **Bias Sub-Populasi:** Hasil ini menunjukkan adanya **Bias Data** di mana kategori `Never used e-cigarettes in my entire life` pada perokok aktif mungkin mencakup perokok yang lebih tua atau memiliki kondisi kronis lainnya yang tidak diukur, sementara populasi pengguna vape yang tersisa (terutama yang berusia muda) memiliki risiko yang lebih rendah. Ini membuktikan bahwa **Rokok Tradisional adalah bahaya utama**, dan penafsiran tentang vape harus dilakukan dengan hati-hati.

        ### Kesimpulan
        * **Faktor Merokok Tradisional adalah pendorong risiko utama.** Kelompok yang pernah merokok (aktif/mantan) menunjukkan risiko jauh lebih tinggi daripada **Never Smoked** ($ \mathbf{3.87\%} $).
        * **Pola Risiko:** Risiko terkonsentrasi pada perokok harian yang tidak beralih ke vape dan mantan perokok, menekankan bahaya dari paparan rokok tradisional jangka panjang.
    """)