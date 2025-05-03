import streamlit as st
import altair as alt
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="SIGAP AI-Powered Security System", layout="wide")

# Custom CSS for fonts and colors
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&family=Roboto:wght@400;700&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Roboto', sans-serif;
        background-color: #1a2529;
        color: white;
    }
    h1, h2 {
        font-family: 'Roboto Mono', monospace;
    }
    .title-text {
        font-size: 40px;
        font-weight: 800;
        line-height: 1;
    }
    .subtitle-text {
        font-size: 16px;
        letter-spacing: 0.1em;
        margin-top: -6px;
        font-weight: 300;
    }
    .section {
        background-color: #152022;
        border-radius: 12px;
        padding: 20px;
    }
    .card {
    background-color: #152022;
    border-radius: 16px;
    padding: 24px;
    }
    </style>
""", unsafe_allow_html=True)

# Header
col1, col2 = st.columns([7, 1])
with col1:
    st.markdown("""
        <div class="text-center">
            <h1 class="title-text">SIGAP</h1>
            <p class="subtitle-text">AI-POWERED SECURITY SYSTEM</p>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.image("logo.jpeg", width=200)


st.markdown("---")

# Main Sections
grid1, grid2, grid3 = st.columns([2, 1, 1])

with grid1:
    # Activity History
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("ACTIVITY HISTORY")

    # Sample data for chart
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    suspicious = [2, 1, 0, 1, 3, 4, 2]
    visitors = [5, 7, 4, 6, 8, 9, 6]

    df = pd.DataFrame({
        'Day': days * 2,
        'Count': suspicious + visitors,
        'Category': ['Suspicious']*7 + ['Visitors']*7
    })

    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Day', sort=days),
        y='Count',
        color=alt.Color('Category', scale=alt.Scale(range=['#3a7f8a', '#7a8a8f'])),
        tooltip=['Category', 'Count']
    ).properties(
        width='container', height=200
    )

    st.altair_chart(chart, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with grid2:
    # Alert
    st.markdown(
    """
    <section style="
        background-color: #152022;
        border-radius: 0.5rem;
        padding: 1.25rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
    ">
        <h4 style="
            margin-bottom: 0.75rem;
        ">ALERT</h4>
        <img src="https://storage.googleapis.com/a1aa/image/09e32bab-8769-42ec-df9c-9f420b1160c0.jpg" alt="Red triangular warning icon with exclamation mark" style="width: 64px; height: 64px; margin-bottom: 1rem;"/>
        <p style="
            max-width: 280px;
            font-size: 1rem;
            line-height: 1.4;
            margin: 0 auto;
        ">Suspicious behavior detected: Person looking into winidows</p>
        <br>
        <p>5 menit yang lalu</p>
    </section>
    """,
    unsafe_allow_html=True,
)
    
with grid3:
    # row1, row2 = st.columns(2)
    
    # with row1:
        st.markdown('<div class="card" style="margin-bottom:16px;"><div style="display:flex; align-items:center; gap:16px;"><div style="background:#3B9B7A;border-radius:16px;width:64px;height:64px;display:flex;align-items:center;justify-content:center;font-weight:800;">ON</div><h4>Camera Status</h4></div></div>', unsafe_allow_html=True)
    # with row2:
    #     st.write('halo')
        
    # col1, col2 = st.columns(2)
    # with col1:
        st.markdown('<div class="card"><div style="display:flex; align-items:center; gap:16px;"><div style="background: red;border-radius:16px;width:64px;height:64px;display:flex;align-items:center;justify-content:center;font-weight:800;">ON</div><h4>Camera Status</h4></div></div>', unsafe_allow_html=True)
        
    # with col2:
    #     st.write('jalp')
        
    
        

# Second row
grid3, grid4, grid5 = st.columns(3)

with grid3:
    st.markdown(
    """
    <section style="
        background-color: #152022;
        border-radius: 16px;
        padding: 1.25rem;
        padding-bottom: 1.9rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1.25rem;
    ">
        <h4 style="
            margin: 0;
        ">Deteksi Terakhir</h4>
        <div style="
            display: flex;
            align-items: center;
            gap: 1.25rem;
        ">
            <div style="
                background-color: #3a7f8a;
                border-radius: 0.5rem;
                padding: 1rem;
                width: 80px;
                height: 80px;
                display: flex;
                justify-content: center;
                align-items: center;
            ">
                <img src="https://storage.googleapis.com/a1aa/image/12b9b0ed-2fbc-469c-f7b2-aaf65a7d0875.jpg" alt="Icon of a delivery person standing next to a box in teal color" style="width: 48px; height: 48px;"/>
            </div>
            <p style="
                font-size: 1.125rem;
                line-height: 1.2;
                margin: 0;
            ">Paket</p>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

with grid4:
    st.markdown(
    """
    <section style="
        background-color: #152022;
        border-radius: 16px;
        padding-x: 2.3rem;
        padding-bottom: 3.2rem;
        padding-top: 24px;
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        gap: 1rem;
    ">
        <h4 
        style="
            # align-self: flex-start;
        ">Deteksi Hari ini</h4>
        <div style="
            display: flex;
            justify-content: center;
            flex-direction: row;
            align-items: center;
            text-align: center;
            gap: 1rem;
            width: 100%;
        ">
            <div>
                <p style="
                    color: #3a7f8a;
                    font-size: 2.5rem;
                    font-weight: 600;
                    line-height: 1;
                    margin: 0;
                ">5</p>
                <p style="
                    font-size: 0.75rem;
                    letter-spacing: 0.1em;
                    margin: 0;
                ">SUSPICIOUS</p>
            </div>
            <div>
                <p style="
                    color: #3a7f8a;
                    font-size: 2.5rem;
                    font-weight: 600;
                    line-height: 1;
                    margin: 0;
                ">12</p>
                <p style="
                    font-size: 0.75rem;
                    letter-spacing: 0.1em;
                    margin: 0;
                ">VISITORS</p>
            </div>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

    
    
with grid5:
    st.markdown('<div class="card"><h4>Riwayat Deteksi</h4><ul style="list-style: none;"><li>🟠 Gerakan Berbahaya (30m)</li><li>🟢 Kurir (1h)</li><li> 🟢 Tamu (3h)</li></ul></div>', unsafe_allow_html=True)


grid1, grid2 = st.columns(2)

with grid1:
    st.markdown('<div class="card" style="margin-top: 24px;"><h4>Heat Map Deteksi Berbahaya</h4></div>', unsafe_allow_html=True)
    
    jam = list(range(24))

# Data dummy: Jumlah deteksi per jam (simulasi)
    np.random.seed(42)
    jumlah_deteksi_per_jam = np.random.poisson(lam=3, size=24)

    # Buat DataFrame
    df = pd.DataFrame({
        'Jam': jam,
        'Jumlah_Deteksi': jumlah_deteksi_per_jam
    })

    data_matrix = np.array([jumlah_deteksi_per_jam])  # shape (1,24)

    # Plot heatmap
    fig = px.imshow(
        data_matrix,
        labels=dict(x="Jam (0–23)", color="Jumlah Deteksi"),
        x=jam,
        y=[''],  
        color_continuous_scale="Reds",
        aspect='auto'
    )

    fig.update_layout(
        template="plotly_dark",
        coloraxis_colorbar=dict(title="Jumlah"),
        xaxis=dict(dtick=1),
        yaxis_visible=False,
        height=200
    )

    st.plotly_chart(fig, use_container_width=True)

    rata2 = np.mean(jumlah_deteksi_per_jam)
    jam_rentan = df[df['Jumlah_Deteksi'] > rata2]['Jam'].tolist()

    
    
with grid2:
    st.markdown("### 🛡️ Jam Rentan (Di atas rata-rata deteksi):")
    st.write(f"Jam: {jam_rentan}")