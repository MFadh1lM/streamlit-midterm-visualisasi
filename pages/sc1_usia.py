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
    
    st.subheader("Interpretasi dan Kesimpulan")
    st.markdown("""
        ### Studi Kasus 1: Kelompok usia berapakah yang mengalami peningkatan risiko serangan jantung paling tinggi?

        1. **Usia muda hingga 44 tahun (risiko dasar rendah):**  
        Risiko serangan jantung masih sangat rendah pada kelompok ini, dengan persentase total di bawah **2%**.  
        Peningkatan dari satu kelompok usia ke kelompok berikutnya masih relatif kecil dan stabil.

        2. **Usia 45–69 tahun (fase percepatan risiko):**  
        Mulai usia **45 tahun**, laju kenaikan risiko meningkat secara tajam.  
        Kenaikan absolut mencapai puncaknya pada kelompok **65–69 tahun**, menandakan periode di mana faktor usia mulai memberi dampak paling besar terhadap kemungkinan serangan jantung.

        3. **Usia ≥70 tahun (fase stabil dengan risiko tinggi):**  
        Setelah usia 70 tahun, risiko total tetap tinggi, tetapi kenaikan absolut mulai menurun.  
        Hal ini dapat diartikan sebagai efek **plateau**, di mana sebagian besar individu berisiko tinggi sudah termasuk dalam kelompok usia sebelumnya.

        ### Rumus Persentase Risiko Global
    """)
    
    st.latex(r"""
        P(\text{Risiko Usia}_i) = \frac{\text{Jumlah Kasus Usia}_i}{\text{Total Kasus}} \times 100
    """)

    st.markdown("""
        ### Kesimpulan
        1. **Masa tenang (usia <45 tahun):** Risiko serangan jantung bertambah sangat lambat hingga usia pertengahan.  
        2. **Fase percepatan (usia 45–69 tahun):** Periode paling kritis di mana risiko meningkat paling tajam dan signifikan.  
        3. **Fase penurunan (≥70 tahun):** Risiko tetap tinggi, namun tidak lagi bertambah secepat fase sebelumnya.  
        4. **Implikasi:** Upaya pencegahan sebaiknya dimulai sejak usia 40-an agar tidak memasuki fase percepatan risiko tanpa persiapan gaya hidup dan pemeriksaan rutin.
    """)
