import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.preprocessing import LabelEncoder

try:
    from data_loader import DF_FULL
except ImportError:
    st.error("Gagal mengimpor DF_FULL. Pastikan file data_loader.py sudah dibuat.")
    DF_FULL = None

# --- VARIABEL KONSTAN ---
FEATURE_VARIABLES = [
    'AgeCategory', 'Sex', 'SleepHours', 'CovidPos', 'AlcoholDrinkers', 
    'SmokerStatus', 'ECigaretteUsage', 'State', 'PhysicalActivities', 
    'HadDiabetes', 'HadStroke'
]
TARGET_VARIABLE = 'HadHeartAttack'
NUMERICAL_COLS_ALL = ['PhysicalHealthDays', 'MentalHealthDays', 'SleepHours', 
                      'HeightInMeters', 'WeightInKilograms', 'BMI']


# --- FUNGSI CACHE UNTUK KORELASI
@st.cache_data
def get_correlation_plot_data(df):
    """Menghitung korelasi dan mengembalikannya untuk plot."""
    # 1. Encoding seluruh kolom
    df_encoded = df.apply(LabelEncoder().fit_transform)
    
    # 2. Hitung korelasi dengan HadHeartAttack
    corr_target = df_encoded.corr()[['HadHeartAttack']].sort_values(by='HadHeartAttack', ascending=False)
    
    # 3. Hapus korelasi 1.00 (dengan dirinya sendiri)
    corr_target = corr_target[corr_target.index != 'HadHeartAttack']
    
    return corr_target

# --- FUNGSI CACHE UNTUK DATA OUTLIER (Plotly Box Plot) ---
@st.cache_data
def get_outlier_plot_data(df, cols):
    """Mengambil subset data untuk plot outlier."""
    # Karena data frame besar, hanya mengambil kolom yang dibutuhkan
    return df[cols] 

# Fungsi-fungsi plotting dan display lainnya tetap sama
def plot_categorical_distribution(df, column, title, sort_order=None, orientation='h'):
    df_counts = df[column].value_counts().reset_index()
    df_counts.columns = [column, 'Count']
    if sort_order:
        df_counts[column] = pd.Categorical(df_counts[column], categories=sort_order, ordered=True)
        df_counts = df_counts.sort_values(column)
    
    if orientation == 'h':
        fig = px.bar(df_counts, x='Count', y=column, orientation='h', title=f'{title}')
        fig.update_layout(yaxis={'categoryorder': 'array', 'categoryarray': df_counts[column]})
    else:
        fig = px.bar(df_counts, x=column, y='Count', title=f'{title}')
        fig.update_xaxes(tickangle=45)
        
    st.plotly_chart(fig, use_container_width=True)


# FUNGSI UTAMA HALAMAN EDA
def show_page():
    st.header("🔬 Exploratory Data Analysis (EDA) & Analisis Dataset")
    st.markdown("---")

    df_full = DF_FULL

    if df_full is None or df_full.empty:
        st.error("Gagal memuat dataset. Silakan periksa file data_loader.py Anda.")
        return

    # --- POIN 1: PENJELASAN DATASET ---
    st.subheader("1. Penjelasan Mengenai Dataset")
    st.markdown("""
        Dataset **Key Indicators of Heart Disease (2022)** berasal dari survei **CDC Behavioral Risk Factor Surveillance System (BRFSS) 2022** di Amerika Serikat.
        
        * **Jumlah Baris:** 246.022 entri (responden dewasa).
        * **Jumlah Kolom:** 40 variabel, dengan fokus pada variabel risiko penyakit kardiovaskular.
    """)

    st.markdown("#### Variabel Kunci Analisis (Fokus Studi Kasus 1-10)")
    variable_list = []
    for var in FEATURE_VARIABLES:
        dtype = df_full[var].dtype
        v_type = "Kategorikal" if dtype == 'object' else "Numerik"
        variable_list.append({'Variabel': var, 'Tipe Data': v_type, 'Contoh Nilai': df_full[var].mode().iloc[0]})
        
    df_vars = pd.DataFrame(variable_list)
    st.table(df_vars)
    st.markdown(f"**Variabel Target:** `{TARGET_VARIABLE}` (Riwayat Serangan Jantung)")
    st.markdown("---")


    # --- POIN 2: MASALAH PADA DATASET ---
    st.subheader("2. Masalah Utama pada Dataset")
    
    # Sub-point 2.1: Imbalance Data
    st.markdown("### A. Imbalance Data (Ketidakseimbangan Kelas)")
    target_counts = df_full[TARGET_VARIABLE].value_counts(normalize=True).mul(100).rename('Percentage').to_frame().reset_index()
    target_counts.columns = [TARGET_VARIABLE, 'Percentage (%)']
    target_counts['Count'] = df_full[TARGET_VARIABLE].value_counts().values
    
    fig_imbalance = px.pie(
        target_counts, 
        values='Percentage (%)', 
        names=TARGET_VARIABLE, 
        title='Proporsi Kasus Serangan Jantung',
        hole=.3
    )
    st.plotly_chart(fig_imbalance, use_container_width=True)
    
    st.warning(f"""
        Rasio proporsi adalah sekitar **{target_counts['Percentage (%)'].iloc[0]:.2f}% (No)** berbanding **{target_counts['Percentage (%)'].iloc[1]:.2f}% (Yes)**. 
    """)
    
    # Sub-point 2.2: Outlier
    st.markdown("### B. Terdapat Banyak Outlier pada Fitur-Fitur dengan Data Numerik (Mohon tunggu, loadnya lama)")
    st.markdown("""
        Visualisasi *box plot* menunjukkan adanya **outlier (pencilan) ekstrem** pada hampir semua fitur numerik. Keberadaan outlier ini meningkatkan variabilitas data.
    """)
    
    # --- PANGGIL FUNGSI CACHE UNTUK DATA OUTLIER ---
    df_outliers = get_outlier_plot_data(df_full, NUMERICAL_COLS_ALL)

    fig_outliers = px.box(
        df_outliers, 
        y=NUMERICAL_COLS_ALL, 
        title="Deteksi Outlier pada Variabel Numerik Kunci",
    )
    fig_outliers.update_layout(height=600, showlegend=False)
    st.plotly_chart(fig_outliers, use_container_width=True)
    
    # Sub-point 2.3: Korelasi Lemah
    st.markdown("### C. Sebagian Besar Fitur Tidak Memiliki Korelasi Kuat dengan Target")
    st.markdown("""
        Analisis korelasi menunjukkan bahwa sebagian besar variabel independen hanya memiliki **korelasi lemah** dengan variabel target. Ini mengindikasikan bahwa risiko serangan jantung dipengaruhi oleh **interaksi banyak faktor secara kompleks**.
    """)
    
    # --- PANGGIL FUNGSI CACHE UNTUK KORELASI ---
    with st.spinner('Menghitung Korelasi Data (Hanya Sekali)...'):
        corr_target = get_correlation_plot_data(df_full)
    
    # 4. Buat Heatmap menggunakan Plotly
    fig_corr = px.imshow(
        corr_target, 
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale='RdBu_r',
        title="Korelasi Setiap Fitur terhadap Riwayat Serangan Jantung (HadHeartAttack)"
    )
    
    fig_corr.update_traces(hovertemplate="Variabel: %{y}<br>Korelasi: %{z}<extra></extra>")
    fig_corr.update_layout(
        height=800,
        xaxis={'side': 'top'},
        coloraxis_colorbar={'title': 'Nilai Korelasi'},
        yaxis={'title': 'Variabel (Diurutkan)'}
    )
    st.plotly_chart(fig_corr, use_container_width=True)
    
    st.markdown("---")

    # --- POIN 3: PEMANFAATAN DATASET ---
    st.subheader("3. Pemanfaatan Dataset dalam Analisis Kelompok")
    st.markdown("""
        Untuk mengatasi masalah **imbalance data** dan mendapatkan kesimpulan yang valid dari **data yang bervariasi dan korelasi lemah**, pemanfaatan dataset difokuskan pada **Analisis Rasio Insiden** di 10 Studi Kasus.
        
        ### Strategi Analisis Kuantitatif
        Kami menggunakan metrik **Rasio Insiden (%)** yang menormalisasi jumlah kasus (`Case Count`) terhadap total populasi di kelompok tersebut (`Total Population`), sehingga fokus beralih dari jumlah absolut ke **risiko per kapita**.
        
        $$\\text{Rasio Insiden (\\%)} = \\left(\\frac{\\text{Jumlah Kasus Serangan Jantung}}{\\text{Total Populasi dalam Kelompok}}\\right) \\times 100$$
        
        ### Rencana Lanjutan
        Pemanfaatan data di masa depan dapat mencakup:
        
        * **Modeling Risiko:** Mengembangkan model prediktif (Regresi Logistik) untuk memprediksi probabilitas serangan jantung.
        * **Clustering:** Mengelompokkan responden menjadi profil risiko yang berbeda.
        * **Simulasi Intervensi:** Memprediksi dampak perubahan faktor risiko tertentu pada penurunan insiden serangan jantung secara keseluruhan.
    """)
    
    st.markdown("---")