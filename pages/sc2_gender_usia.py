import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
from data_loader import DF_FULL

df_full = DF_FULL

# Fungsi pengelompokan usia yang disederhanakan
def simplify_age(age_category):
    if age_category in ['Age 18 to 24', 'Age 25 to 29', 'Age 30 to 34', 'Age 35 to 39', 'Age 40 to 44']:
        return '<45 Tahun'
    elif age_category in ['Age 45 to 49', 'Age 50 to 54', 'Age 55 to 59', 'Age 60 to 64']:
        return '45-64 Tahun'
    elif age_category in ['Age 65 to 69', 'Age 70 to 74', 'Age 75 to 79']:
        return '65-79 Tahun'
    elif age_category == 'Age 80 or older':
        return '>=80 Tahun'
    return age_category

if df_full is not None:
    # 1. Filter kasus serangan jantung & Kelompokkan usia
    df_cases = df_full[df_full['HadHeartAttack'] == 'Yes'].copy()
    df_cases['Kelompok Usia'] = df_cases['AgeCategory'].apply(simplify_age)

    # 2. Hitung Jumlah Kasus (Count) per kombinasi Jenis Kelamin dan Usia Baru
    df_counts = df_cases.groupby(['Kelompok Usia', 'Sex'], as_index=False)['HadHeartAttack'].count()
    df_counts.rename(columns={'HadHeartAttack': 'Jumlah Kasus'}, inplace=True)
    
    # 3. Hitung Persentase Kasus Global (untuk Kenaikan Absolut)
    total_cases_sc2 = df_counts['Jumlah Kasus'].sum()
    df_counts['Persentase Kasus Global (%)'] = (df_counts['Jumlah Kasus'] / total_cases_sc2 * 100).round(2)
    
    # 4. Definisikan urutan usia yang disederhanakan
    simple_age_order = ['<45 Tahun', '45-64 Tahun', '65-79 Tahun', '>=80 Tahun']
    
    # 5. Fungsi BARU untuk menghitung Kenaikan Absolut dan menyertakan Jumlah Kasus
    def calculate_increase_with_count(df, gender):
        df_f = df[df['Sex'] == gender].copy()
        
        # Urutkan berdasarkan urutan usia yang disederhanakan
        df_f = df_f.sort_values(by='Kelompok Usia', key=lambda x: x.map({age: i for i, age in enumerate(simple_age_order)}))
        
        # Hitung Kenaikan Absolut
        df_f['Kenaikan Absolut (%)'] = df_f['Persentase Kasus Global (%)'].diff().fillna(0).round(2)
        
        df_f.rename(columns={'Sex': 'Jenis Kelamin'}, inplace=True)
        
        # Urutan kolom yang baru (dengan Jumlah Kasus)
        return df_f[['Kelompok Usia', 'Jumlah Kasus', 'Persentase Kasus Global (%)', 'Kenaikan Absolut (%)']]

    df_male_increase = calculate_increase_with_count(df_counts, 'Male')
    df_female_increase = calculate_increase_with_count(df_counts, 'Female')
    
    # Menyiapkan data untuk visualisasi Stacked Bar
    df_gender_age_count = df_counts.rename(columns={'Sex': 'Jenis Kelamin'})
    
else:
    # Buat DataFrame kosong jika data gagal dimuat
    df_gender_age_count = pd.DataFrame(columns=['Kelompok Usia', 'Jenis Kelamin', 'Jumlah Kasus'])
    df_male_increase = pd.DataFrame(columns=['Kelompok Usia', 'Jumlah Kasus', 'Persentase Kasus Global (%)', 'Kenaikan Absolut (%)'])
    df_female_increase = pd.DataFrame(columns=['Kelompok Usia', 'Jumlah Kasus', 'Persentase Kasus Global (%)', 'Kenaikan Absolut (%)'])

# Visualisasi
def create_gender_age_stacked_bar_chart(df):
    """Membuat Normalized Stacked Bar Chart (Proporsi 100%)"""
    
    simple_age_order = ['<45 Tahun', '45-64 Tahun', '65-79 Tahun', '>=80 Tahun']
    color_scale = alt.Scale(domain=['Male', 'Female'], range=['#1f77b4', '#ff7f0e'])

    chart_bar = alt.Chart(df).mark_bar().encode(
        y=alt.Y('Kelompok Usia:N', sort=simple_age_order, title='Kelompok Usia'),
        x=alt.X('Jumlah Kasus:Q', stack='normalize', axis=alt.Axis(title='Proporsi Kasus Serangan Jantung (%)', format='.0%')), 
        color=alt.Color('Jenis Kelamin:N', scale=color_scale, legend=alt.Legend(title="Jenis Kelamin")),
        tooltip=[
            'Kelompok Usia', 
            'Jenis Kelamin', 
            alt.Tooltip('Jumlah Kasus:Q', title='Jumlah Kasus Aktual')
        ]
    ).properties(
        title='Proporsi Kasus Serangan Jantung Berdasarkan Jenis Kelamin dalam Setiap Kelompok Usia',
        height=250 
    ).interactive()
    
    return chart_bar

# --- 3A. Chart Persentase Kasus Global per Gender ---
def create_global_percentage_chart(df_male, df_female):
    df_male['Jenis Kelamin'] = 'Male'
    df_female['Jenis Kelamin'] = 'Female'
    df_combined = pd.concat([df_male, df_female])
    
    simple_age_order = ['<45 Tahun', '45-64 Tahun', '65-79 Tahun', '>=80 Tahun']
    color_scale = alt.Scale(domain=['Male', 'Female'], range=['#1f77b4', '#ff7f0e'])
    
    chart = alt.Chart(df_combined).mark_line(point=True).encode(
        x=alt.X('Kelompok Usia:N', sort=simple_age_order, title='Kelompok Usia'),
        y=alt.Y('Persentase Kasus Global (%):Q', title='Persentase dari Total Kasus Global'),
        color=alt.Color('Jenis Kelamin:N', scale=color_scale),
        tooltip=['Jenis Kelamin', 'Kelompok Usia', 'Persentase Kasus Global (%)']
    ).properties(
        title='Persentase Kasus Serangan Jantung per Kelompok Usia (Global)',
        height=300
    )
    return chart


# --- 3B. Chart Kenaikan Absolut Risiko per Gender ---
def create_absolute_increase_chart(df_male, df_female):
    """Membuat Grouped Bar Chart Interaktif Plotly untuk Kenaikan Absolut Risiko per Gender."""
    
    # 1. Gabungkan data
    df_combined = pd.concat([df_male, df_female])
    
    simple_age_order = ['<45 Tahun', '45-64 Tahun', '65-79 Tahun', '>=80 Tahun']
    
    # 2. Buat Plotly Chart
    fig = px.bar(
        df_combined,
        x='Kelompok Usia', 
        y='Kenaikan Absolut (%)', 
        color='Jenis Kelamin', # Variabel untuk mengelompokkan
        barmode='group',        # Mode grouping (batang berdampingan)
        text_auto='.2f',        # Menambahkan label teks di atas batang
        category_orders={"Kelompok Usia": simple_age_order},
        labels={
            "Jenis Kelamin": "Jenis Kelamin", 
            "Kenaikan Absolut (%)": "Kenaikan Absolut Risiko (%)"
        },
        title="Kenaikan Absolut Risiko Serangan Jantung Antar Kelompok Usia"
    )

    # 3. Perbaiki Layout
    fig.update_traces(textposition='outside')
    fig.update_layout(xaxis_title="Kelompok Usia", 
                      yaxis_title="Kenaikan Absolut Risiko (%)",
                      # Menambahkan garis nol untuk membedakan kenaikan/penurunan
                      shapes=[
                          dict(
                            type='line',
                            yref='y', y0=0, y1=0,
                            xref='paper', x0=0, x1=1,
                            line=dict(color='Red', width=1, dash='dot')
                          )
                      ],
                      legend_title="Jenis Kelamin")
    
    return fig

def show_page():
    """Menampilkan konten lengkap Study Case 2: Gender vs. Usia."""
    
    if df_full is None:
        return

    st.header("Study Case 2: Perbandingan Risiko Serangan Jantung Berdasarkan Jenis Kelamin dan Kelompok Usia")
    st.markdown("---")
    
    st.subheader("1. Proporsi Kasus Berdasarkan Gender dan Usia (Proporsi 100% per Kelompok Usia)")
    st.altair_chart(create_gender_age_stacked_bar_chart(df_gender_age_count), use_container_width=True) 

    st.subheader("2. Analisis Kenaikan Absolut Risiko Antar Kelompok Usia")
    st.info("Tabel ini menunjukkan total kasus, persentase global, dan percepatan risiko per gender.")
    
    col_male_table, col_female_table = st.columns(2)
    
    with col_male_table:
        st.caption("**:blue[Laki-laki (Male)]**")
        st.dataframe(df_male_increase, hide_index=True)
        
    with col_female_table:
        st.caption("**:orange[Perempuan (Female)]**")
        st.dataframe(df_female_increase, hide_index=True)

    st.subheader("3. Tren Global dan Kenaikan Risiko per Gender")

    st.altair_chart(create_global_percentage_chart(df_male_increase, df_female_increase), use_container_width=True)
    st.plotly_chart(create_absolute_increase_chart(df_male_increase, df_female_increase), use_container_width=True)

    st.subheader("4. Interpretasi dan Kesimpulan")
    st.markdown("""
        ### Studi Kasus 2: Apakah proporsi risiko serangan jantung pada perempuan selalu lebih rendah daripada laki-laki di setiap fase usia?

        #### Analisis Proporsi (Stacked Chart)
        Visualisasi ini memperlihatkan **proporsi kasus serangan jantung** di dalam setiap kelompok usia (total $100\\%$ per bar). Artinya, semakin besar bagian warna dalam bar, semakin besar kontribusi kelompok gender tersebut terhadap total kasus di usia tersebut.

        1. **Dominasi Awal (<45 Tahun):** Proporsi kasus pada laki-laki jauh lebih tinggi (sekitar **60%**), mengindikasikan bahwa pada usia muda risiko lebih banyak muncul pada laki-laki.
        2. **Penurunan Proporsi Perempuan (45–79 Tahun):** Pada rentang usia paruh baya hingga awal lanjut, proporsi perempuan justru menurun. Hal ini mengindikasikan bahwa peningkatan kasus pada laki-laki lebih tajam di fase ini.
        3. **Usia Lanjut (≥80 Tahun):** Proporsi perempuan tetap tinggi (mencapai sekitar **40%** dari total kasus pada kelompok usia tersebut), yang menandakan bahwa di usia sangat lanjut, perempuan menjadi bagian signifikan dari keseluruhan kasus.

        #### Analisis Kenaikan Absolut (Tabel)
        Tabel menampilkan perubahan atau **kenaikan absolut risiko global** antar kelompok usia.

        1. **Titik Percepatan Kritis:** Kenaikan absolut tertinggi pada **kedua gender** terjadi saat transisi dari usia **45–64 tahun** ke **65–79 tahun**.
        2. **Makna Tren:** Ini mengindikasikan percepatan peningkatan risiko pada masa paruh baya menuju usia lanjut.

        #### Analisis Persentase Kasus Global
        Persentase kasus global dihitung untuk melihat kontribusi setiap kelompok usia terhadap total keseluruhan kasus pada skala global.

    """)

    st.latex(r"""
        \text{Persentase Kasus Global} = 
        \frac{\text{Jumlah Kasus per Kelompok Usia}}{\text{Total Seluruh Kasus}} \times 100
    """)

    st.markdown("""
        Visualisasi ini membantu menunjukkan bahwa meskipun kasus pada kelompok usia muda relatif kecil, kontribusinya terhadap total global meningkat drastis seiring bertambahnya usia, terutama di kelompok **45–79 tahun**.

        ---

        ### Kesimpulan
        * **Proporsi Risiko Perempuan Meningkat:** Setelah usia 45 tahun, proporsi kasus pada perempuan naik signifikan dan perbedaannya dengan laki-laki makin kecil.  
        * **Fase Kritis untuk Pencegahan:** Usia **45–64 tahun** dan **65–79 tahun** merupakan periode dengan kenaikan risiko paling tajam bagi kedua gender.  
        * **Implikasi Umum:** Peningkatan kasus global dan rasio antar gender menunjukkan bahwa upaya pencegahan perlu difokuskan pada usia paruh baya untuk menghambat peningkatan kasus di usia lanjut.
    """)
