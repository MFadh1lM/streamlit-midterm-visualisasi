import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt

try:
    from data_loader import DF_FULL
except ImportError:
    st.error("Gagal mengimpor DF_FULL. Pastikan file data_loader.py sudah dibuat.")
    DF_FULL = None

# Fungsi Mapping Negara Bagian (tetap sama)
STATE_ABBREV_MAPPING = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
    'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
    'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
    'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
    'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
    'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY',
    # Wilayah yang tidak memiliki singkatan Plotly
    'District of Columbia': 'DC', 'Puerto Rico': 'PR', 'Guam': 'GU', 'Virgin Islands': 'VI' 
}


if DF_FULL is not None:
    # 1. Hitung Jumlah Kasus Serangan Jantung per Negara Bagian
    df_cases = DF_FULL[DF_FULL['HadHeartAttack'] == 'Yes'].copy()
    df_counts = df_cases.groupby('State', as_index=False)['HadHeartAttack'].count().rename(columns={'HadHeartAttack': 'Count_of_HadHeartAttack'})

    # 2. Tambahkan kolom singkatan negara bagian
    df_counts['State_Code'] = df_counts['State'].map(STATE_ABBREV_MAPPING)
    
    # 3. Hitung Persentase Kontribusi Global
    total_grand = df_counts['Count_of_HadHeartAttack'].sum()
    df_counts['Kontribusi (%)'] = (df_counts['Count_of_HadHeartAttack'] / total_grand * 100).round(2)


    # 4. Urutkan berdasarkan kasus absolut tertinggi
    df_regional_cases = df_counts.sort_values(by='Count_of_HadHeartAttack', ascending=False)
else:
    df_regional_cases = pd.DataFrame(columns=['State', 'Count_of_HadHeartAttack', 'State_Code', 'Kontribusi (%)'])

def create_plotly_map(df):
    """Membuat Peta Choropleth (Heatmap) Interaktif dengan Plotly."""
    df_map = df[~df['State_Code'].isin(['DC', 'PR', 'GU', 'VI'])].copy()

    fig = px.choropleth(df_map, 
                        locations='State_Code',
                        locationmode='USA-states',
                        scope='usa',
                        color='Count_of_HadHeartAttack',
                        color_continuous_scale=px.colors.sequential.Sunset,
                        hover_name='State',
                        hover_data={'State_Code': False, 'Count_of_HadHeartAttack': True}
    )
    fig.update_layout(title_text='Peta Beban Kasus Serangan Jantung Absolut per Negara Bagian', geo_scope='usa')
    return fig

def create_top10_pie_chart(df):
    """Membuat Pie Chart untuk 10 Negara Bagian Penyumbang Kasus Terbesar."""
    
    # Ambil 10 teratas dan hitung sisanya sebagai 'Lainnya'
    df_top_10 = df.head(10).copy()
    
    other_cases = df['Count_of_HadHeartAttack'].iloc[10:].sum()
    other_percent = df['Kontribusi (%)'].iloc[10:].sum()

    df_other = pd.DataFrame({
        'State': ['Lainnya'], 
        'Kontribusi (%)': [other_percent], 
        'Count_of_HadHeartAttack': [other_cases]
    })
    
    df_pie = pd.concat([df_top_10, df_other])

    fig = px.pie(df_pie, 
                 values='Kontribusi (%)', 
                 names='State', 
                 title='Kontribusi Persentase Kasus (Top 10 + Lainnya)',
                 hole=0.4 # Membuat Donut Chart
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def show_page():
    """Menampilkan konten lengkap Study Case 7."""
    
    if DF_FULL is None:
        return

    st.header("Study Case 7: Pemetaan Beban Kasus Serangan Jantung Regional")
    st.markdown("---")
    
    # 1. Visualisasi Peta Choropleth (Plotly)
    st.subheader("1. Peta Interaktif Beban Kasus Absolut")
    st.plotly_chart(create_plotly_map(df_regional_cases), use_container_width=True) 

    # 2. Visualisasi Pie Chart & Top 10 Bar
    st.subheader("2. Kontribusi Kasus Terbesar")
    
    col_pie, col_bar = st.columns([1, 1])

    with col_pie:
        st.caption("Diagram Donut: Kontribusi Persentase (Total Kasus)")
        st.plotly_chart(create_top10_pie_chart(df_regional_cases), use_container_width=True)

    with col_bar:
        st.caption("Top 10 Beban Kasus Absolut (Angka)")
        df_top_10_bar = df_regional_cases.head(10).sort_values(by='Count_of_HadHeartAttack', ascending=True)
        
        fig_bar = px.bar(df_top_10_bar, 
                         x='Count_of_HadHeartAttack', # X adalah Count
                         y='State', # Y adalah Negara Bagian
                         orientation='h', # Bar horizontal
                         title="Top 10 Beban Kasus Absolut",
                         text='Count_of_HadHeartAttack',
                         color_discrete_sequence=px.colors.qualitative.Bold)
        fig_bar.update_traces(textposition='outside')
        st.plotly_chart(fig_bar, use_container_width=True)


    # 3. Data Rinci
    st.subheader("3. Data Rinci Kasus Regional")
    st.dataframe(df_regional_cases[['State', 'Count_of_HadHeartAttack', 'Kontribusi (%)']], hide_index=True, use_container_width=True)
    
    # 4. Interpretasi dan Penjelasan Detail
    st.subheader("4. Interpretasi dan Kesimpulan")

    st.markdown("""
        ### Analisis Beban Kasus Absolut per Negara Bagian

        Visualisasi ini menampilkan distribusi jumlah **kasus serangan jantung absolut** di seluruh negara bagian Amerika Serikat.  
        Data ini menunjukkan **volume total kasus yang dilaporkan**, bukan tingkat risiko per individu.

        #### Temuan Kunci

        1. **Dominasi Kasus Regional:**  
        Berdasarkan *Donut Chart*, beberapa negara bagian seperti **Washington, Ohio, Florida, dan Texas** muncul sebagai penyumbang terbesar kasus serangan jantung secara absolut.  
        Hal ini berarti bahwa wilayah-wilayah tersebut memiliki **jumlah kasus terbanyak**, bukan berarti warganya memiliki risiko tertinggi.

        2. **Konsentrasi Geografis (Peta Choropleth):**  
        Warna yang lebih gelap pada peta menunjukkan wilayah dengan jumlah kasus tertinggi.  
        Pola ini membantu mengidentifikasi **cluster geografis** — misalnya bagian Tenggara dan Timur AS yang cenderung lebih padat kasus.

        3. **Kontribusi Terhadap Total Dataset:**  
        Sepuluh negara bagian teratas menyumbang lebih dari separuh total kasus dalam dataset, menunjukkan **distribusi yang tidak merata** antar wilayah.

        ---

        - **Interpretasi:**  
        Peta ini mengukur **beban penyakit (disease burden)**, bukan **tingkat risiko (incidence rate)**.  
        Jadi, wilayah dengan populasi besar atau responden lebih banyak akan tampak lebih dominan.

        - **Kemungkinan Faktor Penyebab Perbedaan Regional:**  
        *Variasi gaya hidup, prevalensi faktor risiko (seperti obesitas, rokok, dan tekanan darah tinggi), serta ketersediaan layanan kesehatan* dapat menjelaskan perbedaan antar wilayah.

        ---

        ### Kesimpulan Akhir

        - Peta dan diagram menunjukkan bahwa **beban absolut kasus serangan jantung tidak merata antar wilayah AS**, dengan konsentrasi di beberapa negara bagian besar seperti **Texas, Florida, dan Ohio**.  
        - Visualisasi ini berguna untuk **prioritas sumber daya kesehatan masyarakat** di wilayah dengan beban tinggi.  
        - Namun, untuk memahami **risiko sebenarnya**, diperlukan analisis tambahan menggunakan **rasio insiden per kapita atau tingkat prevalensi per 100.000 penduduk.**
    """)
