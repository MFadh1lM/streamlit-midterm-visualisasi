import streamlit as st
import pandas as pd
import altair as alt
from data_loader import DF_FULL

df_full = DF_FULL


if df_full is not None:
    # 1. Menghitung Jumlah Kasus Serangan Jantung (HadHeartAttack == 'Yes') per Kelompok Usia
    df_cases = df_full[df_full['HadHeartAttack'] == 'Yes']

    # 2. Mengelompokkan berdasarkan AgeCategory dan menghitung count (Count of HadHeartAttack)
    df_counts = df_cases.groupby('AgeCategory', as_index=False)['HadHeartAttack'].count()
    df_counts.rename(columns={'HadHeartAttack': 'Count of HadHeartAttack'}, inplace=True)

    # 3. Urutan Kelompok Usia yang Benar (Untuk visualisasi dan perhitungan selisih)
    age_order = [
        'Age 18 to 24', 'Age 25 to 29', 'Age 30 to 34', 'Age 35 to 39',
        'Age 40 to 44', 'Age 45 to 49', 'Age 50 to 54', 'Age 55 to 59',
        'Age 60 to 64', 'Age 65 to 69', 'Age 70 to 74', 'Age 75 to 79',
        'Age 80 or older'
    ]
    
    # 4. Memastikan urutan dan mengisi usia yang kosong (jika ada)
    df_final = pd.DataFrame({'AgeCategory': age_order})
    df_final = df_final.merge(df_counts, left_on='AgeCategory', right_on='AgeCategory', how='left').fillna(0)
    
    # 5. Menghitung Persentase Risiko Global
    total_cases_sc1 = df_final['Count of HadHeartAttack'].sum()
    df_final['Persentase Risiko (%)'] = (df_final['Count of HadHeartAttack'] / total_cases_sc1 * 100).round(2)
    
    # 6. Menghitung Kenaikan Absolut
    df_final['Kenaikan Absolut (%)'] = df_final['Persentase Risiko (%)'].diff().fillna(0).round(2)
    
    # Ganti nama kolom AgeCategory agar sesuai dengan visualisasi
    df_final.rename(columns={'AgeCategory': 'Kelompok Usia'}, inplace=True)
    df_raw_usia = df_final # Variabel yang akan digunakan di fungsi render
else:
    # Jika data gagal dimuat, buat DataFrame kosong untuk mencegah error
    df_raw_usia = pd.DataFrame(columns=['Kelompok Usia', 'Count of HadHeartAttack', 'Persentase Risiko (%)', 'Kenaikan Absolut (%)'])

def create_absolute_increase_chart(df):
    color_condition = alt.condition(
        alt.datum['Kenaikan Absolut (%)'] > 0,
        alt.value('steelblue'), 
        alt.value('firebrick')   
    )
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Kelompok Usia', sort=None, axis=alt.Axis(title='Kelompok Usia')),
        y=alt.Y('Kenaikan Absolut (%)', axis=alt.Axis(title='Kenaikan Absolut Risiko (%)')),
        color=color_condition,
        tooltip=['Kelompok Usia', 'Kenaikan Absolut (%)', 'Persentase Risiko (%)']
    ).properties(title='Kenaikan Absolut (%)').interactive() 
    return chart

def create_pie_chart(df):
    chart = alt.Chart(df).mark_arc(outerRadius=120).encode(
        theta=alt.Theta("Persentase Risiko (%):Q", stack=True),
        color=alt.Color("Kelompok Usia:N", legend=alt.Legend(title="Kelompok Usia")),
        order=alt.Order("Persentase Risiko (%):Q", sort="descending"),
        tooltip=["Kelompok Usia", alt.Tooltip("Persentase Risiko (%):Q", format=".2f")]
    ).properties(title="Count of HadHeartAttack")

    text = chart.mark_text(radius=140).encode(
        text=alt.Text("Persentase Risiko (%):Q", format=".2f"),
        order=alt.Order("Persentase Risiko (%):Q", sort="descending"),
        color=alt.value("black") 
    )
    return chart + text

def show_page():
    st.header("Study Case 1: Analisis Evolusi Risiko Serangan Jantung Berdasarkan Usia")
    st.markdown("---")
    
    st.subheader("Data Rinci Risiko Serangan Jantung Berdasarkan Usia")
    st.dataframe(df_raw_usia, use_container_width=True, hide_index=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Persentase Risiko Serangan Jantung Berdasarkan Kelompok Usia")
        st.altair_chart(create_pie_chart(df_raw_usia), use_container_width=False)
    with col2:
        st.subheader("Visualisasi Kenaikan Absolut Risiko")
        st.altair_chart(create_absolute_increase_chart(df_raw_usia), use_container_width=True)
    
    st.subheader("Interpretasi dan Penjelasan Detail")
    st.markdown("""
        ### Studi kasus 1: Kelompok usia berapakah yang mengalami peningkatan risiko serangan jantung paling tinggi?
        
        1.  **Risiko dasar dan kenaikan lambat dimulai dari usia 18 - 44 tahun:** Ini adalah periode risiko rendah di mana persentase risiko total berada di bawah $2\%$ dan kecepatan penambahan risiko (Kenaikan Absolut) sangat lambat.
        2.  **Percepatan risiko dan titik kritis dimulai dari usia 45-69 tahun:** Ini adalah fase berbahaya di mana risiko berakselerasi secara dramatis. Kenaikan absolut risiko melonjak dari $0,54\%$ menjadi puncaknya di $4,32\%$.
        3.  **Risiko total tertinggi dan fenomena "Survivor Bias" di usia $\ge 70$ tahun:** Risiko total tertinggi ada di kelompok usia $80$ tahun atau lebih yang mencatat persentase risiko total tertinggi ($18,06\%$). Lalu terdapat penurunan kenaikan absolut yang signifikan ($-2,55\%$) pada usia $75-79$ tahun yang mengindikasikan seleksi penyintas (*survivor bias*) yaitu individu yang sangat rentan, atau telah menderita komplikasi parah kemungkinan besar telah meninggal sebelum mencapai usia $75$, meninggalkan populasi yang tersisa yang secara relatif lebih tangguh dan sehat.
        
        ### Kesimpulan
        1.  **Masa tenang:** Risiko serangan jantung absolut bertambah sangat lambat hingga usia $44$ tahun.
        2.  **Periode peringatan (Akselerasi Risiko):** Percepatan risiko yang signifikan dan berbahaya dimulai di usia $45-49$ tahun dan berpuncak pada usia $65-69$ tahun.
        3.  **Risiko puncak absolut:** Persentase risiko tertinggi secara keseluruhan ada pada kelompok $80$ tahun atau lebih ($18,06\%$).
        4.  **Implikasi medis:** Intervensi klinis dan perubahan gaya hidup harus mulai diterapkan pada usia pertengahan ($40$an) untuk meminimalkan percepatan risiko yang akan terjadi secara cepat pada dua dekade berikutnya.
    """)