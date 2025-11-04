import streamlit as st
import pandas as pd
import altair as alt

try:
    from data_loader import DF_FULL
except ImportError:
    st.error("Gagal mengimpor DF_FULL. Pastikan file data_loader.py sudah dibuat.")
    DF_FULL = None

# === Fungsi untuk menyederhanakan kategori usia (jika dibutuhkan nanti) ===
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


# === Proses data ===
if DF_FULL is not None:
    # 1. Total populasi per kategori diabetes
    df_pop = DF_FULL.groupby('HadDiabetes', as_index=False)['HadHeartAttack'].count().rename(
        columns={'HadHeartAttack': 'Total_Population'}
    )

    # 2. Kasus serangan jantung
    df_cases = DF_FULL[DF_FULL['HadHeartAttack'] == 'Yes'].groupby('HadDiabetes', as_index=False)['HadHeartAttack'].count().rename(
        columns={'HadHeartAttack': 'Case_Count'}
    )

    # 3. Gabungkan
    df_risk = df_pop.merge(df_cases, on='HadDiabetes', how='left').fillna(0)

    # 4. Rasio insiden (%)
    df_risk['Rasio_Insiden (%)'] = (df_risk['Case_Count'] / df_risk['Total_Population'] * 100).round(2)

    # 5. Proporsi kasus absolut (%)
    total_cases = df_risk['Case_Count'].sum()
    df_risk['Proporsi_Kasus (%)'] = (df_risk['Case_Count'] / total_cases * 100).round(1)

    df_risk.rename(columns={'HadDiabetes': 'Status Diabetes', 'Case_Count': 'Count_of_HadHeartAttack'}, inplace=True)

    diabetes_order = ['Yes', 'No, pre-diabetes or borderline diabetes', 'Yes, but only during pregnancy (female)', 'No']
    df_diabetes_risk = df_risk
else:
    df_diabetes_risk = pd.DataFrame(columns=[
        'Status Diabetes', 'Count_of_HadHeartAttack', 'Proporsi_Kasus (%)', 'Total_Population', 'Rasio_Insiden (%)'
    ])


# === VISUALISASI 1: BAR CHART — Proporsi Kasus Absolut ===
def create_bar_chart(df):
    diabetes_order = ['Yes', 'No, pre-diabetes or borderline diabetes', 'Yes, but only during pregnancy (female)', 'No']
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Status Diabetes:N', sort=diabetes_order, title='Status Diabetes', axis=alt.Axis(labelAngle=-45)),
        y=alt.Y('Count_of_HadHeartAttack:Q', title='Jumlah Kasus Serangan Jantung Absolut'),
        color=alt.Color('Count_of_HadHeartAttack:Q',
                        title='Kasus Absolut',
                        scale=alt.Scale(scheme='bluegreen')),
        tooltip=['Status Diabetes', 'Count_of_HadHeartAttack', 'Proporsi_Kasus (%)']
    ).properties(
        title='Proporsi Kasus Serangan Jantung Berdasarkan Status Diabetes'
    ).interactive()
    return chart


# === VISUALISASI 2: LINE CHART — Rasio Insiden ===
def create_ratio_chart(df):
    diabetes_order = ['Yes', 'No, pre-diabetes or borderline diabetes', 'Yes, but only during pregnancy (female)', 'No']
    chart = alt.Chart(df).mark_line(point=True, strokeWidth=3).encode(
        x=alt.X('Status Diabetes:N', sort=diabetes_order, title='Status Diabetes', axis=alt.Axis(labelAngle=-45)),
        y=alt.Y('Rasio_Insiden (%):Q', title='Rasio Insiden (%)'),
        color=alt.value('#1f77b4'),
        tooltip=['Status Diabetes', 'Rasio_Insiden (%)']
    ).properties(
        title='Perbandingan Rasio Insiden Serangan Jantung Berdasarkan Status Diabetes'
    ).interactive()
    return chart


# === TAMPILAN HALAMAN ===
def show_page():
    if DF_FULL is None:
        return

    st.header("Study Case 9: Diabetes vs. Risiko Serangan Jantung")
    st.markdown("---")

    # Bar Chart — Proporsi Kasus Absolut
    st.subheader("1. Bagan Kolom Proporsi Kasus Absolut")
    st.altair_chart(create_bar_chart(df_diabetes_risk), use_container_width=True)

    # Line Chart — Rasio Insiden
    st.subheader("2. Perbandingan Rasio Insiden Serangan Jantung")
    st.altair_chart(create_ratio_chart(df_diabetes_risk), use_container_width=True)

    # Data Rinci
    st.subheader("3. Data Rinci Kasus Absolut, Populasi, dan Rasio Insiden")
    st.dataframe(df_diabetes_risk, hide_index=True)

    # Interpretasi dan Kesimpulan
    st.subheader("4. Interpretasi dan Kesimpulan")

    # Ambil data untuk interpretasi
    ratio_yes = df_diabetes_risk[df_diabetes_risk['Status Diabetes'] == 'Yes']['Rasio_Insiden (%)'].iloc[0]
    ratio_no = df_diabetes_risk[df_diabetes_risk['Status Diabetes'] == 'No']['Rasio_Insiden (%)'].iloc[0]
    risk_factor = (ratio_yes / ratio_no).round(1)

    st.markdown("""
        ### Rumus Perhitungan
        Rasio insiden digunakan untuk mengukur risiko serangan jantung **per kapita** dalam tiap kategori diabetes.
    """)

    st.latex(r"""
        \text{Rasio Insiden (\%)} = \frac{\text{Jumlah Kasus Serangan Jantung}}{\text{Total Populasi}} \times 100
    """)

    st.markdown(f"""
        ---
        ### Hasil Analisis Rasio Insiden

        Berdasarkan perhitungan:
        * **Rasio Insiden Diabetes (Yes):** sekitar **{ratio_yes}%**
        * **Rasio Insiden Non-Diabetes (No):** sekitar **{ratio_no}%**
        
        Maka risiko relatifnya adalah:
    """)

    st.latex(rf"""
        \frac{{\text{{Rasio Insiden}}_{{Diabetes}}}}{{\text{{Rasio Insiden}}_{{Non-Diabetes}}}} = \frac{{{ratio_yes}}}{{{ratio_no}}} \approx {risk_factor}
    """)

    st.markdown(f"""
        ---
        ### Interpretasi

        1. **Risiko Relatif:** Individu dengan diabetes memiliki risiko serangan jantung sekitar **{risk_factor} kali lipat lebih tinggi** dibandingkan individu non-diabetes.
        2. **Beban Kasus:** Meskipun proporsi populasi penderita diabetes lebih kecil, kontribusi kasus serangan jantung mereka cukup besar.
        3. **Faktor Risiko Terkait:** Kadar gula darah tinggi memengaruhi kerusakan pembuluh darah dan mempercepat komplikasi kardiovaskular.

        ---
        ### Kesimpulan
        Temuan ini menunjukkan **hubungan yang kuat antara diabetes dan peningkatan risiko serangan jantung**.  
        Upaya pengendalian gula darah, diet sehat, aktivitas fisik, serta pemantauan tekanan darah dan kolesterol merupakan langkah pencegahan penting untuk mengurangi risiko komplikasi jantung.
    """)

