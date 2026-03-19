import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time

# --- SYSTEM CONFIGURATION ---
st.set_page_config(page_title="HPCL Nexus | Global Command", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

# --- SESSION STATE INITIALIZATION (FIXED FOR DOUBLE-CLICK BUG) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'booting' not in st.session_state:
    st.session_state.booting = False
# We now rely on the widget's native 'key' to manage theme state
if 'ui_theme' not in st.session_state:
    st.session_state.ui_theme = 'Dark (SCADA)'

# --- DATA GENERATOR ---
@st.cache_data
def load_base_data():
    np.random.seed(42)
    dates = pd.date_range(start="2024-01-01", periods=90, freq='D')
    regions = ['North', 'South', 'East', 'West']
    products = ['Petrol (MS)', 'Diesel (HSD)', 'LPG', 'Lubricants', 'Aviation Fuel']
    
    data = []
    for d in dates:
        for r in regions:
            for p in products:
                base_vol = 5000 if p != 'LPG' else 15000
                data.append({
                    'Date': d,
                    'Region': r,
                    'Product': p,
                    'Volume_kL': np.random.normal(base_vol, base_vol*0.2),
                    'Base_Revenue': np.random.uniform(15, 60),
                    'Base_Cost': np.random.uniform(10, 50),
                    'AI_Forecast_Demand': np.random.normal(base_vol*1.05, base_vol*0.1)
                })
    return pd.DataFrame(data)

base_df = load_base_data()

# --- THEME CSS INJECTION (ADDED SMOOTH TRANSITIONS) ---
def inject_theme(theme_choice):
    if theme_choice == 'Dark (SCADA)':
        bg, card, text, accent, border, shadow = "#070b14", "#111827", "#e2e8f0", "#ff003c", "#374151", "0 0 20px rgba(255, 0, 60, 0.05)"
        st.markdown("<style>.stApp {background-color: #070b14;}</style>", unsafe_allow_html=True)
    else:
        bg, card, text, accent, border, shadow = "#f8fafc", "#ffffff", "#0f172a", "#2563eb", "#e2e8f0", "0 10px 15px -3px rgba(0, 0, 0, 0.1)"
        st.markdown("<style>.stApp {background-color: #f8fafc;}</style>", unsafe_allow_html=True)

    css = f"""
    <style>
        /* 1. SMOOTH TRANSITION ENGINE */
        .stApp, .stApp > header, [data-testid="stSidebar"], div[data-testid="stMetric"], 
        h1, h2, h3, h4, p, span, .css-1r6slb0, .css-12oz5g7 {{
            transition: background-color 0.4s ease-in-out, color 0.4s ease-in-out, 
                        border-color 0.4s ease-in-out, box-shadow 0.4s ease-in-out !important;
        }}

        /* 2. HIDE DEFAULT ELEMENTS */
        #MainMenu {{ visibility: hidden; }}
        footer {{ visibility: hidden; }}
        header {{ background-color: transparent !important; }}
        
        /* 3. TYPOGRAPHY */
        h1, h2, h3, h4, p, span {{ color: {text} !important; font-family: 'Inter', sans-serif; }}
        
        /* 4. METRIC CARDS */
        div[data-testid="stMetric"] {{
            background-color: {card} !important;
            padding: 20px;
            border-radius: 12px;
            border-top: 3px solid {accent};
            box-shadow: {shadow};
            border: 1px solid {border};
        }}
        div[data-testid="stMetric"]:hover {{ 
            transform: translateY(-4px); 
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.15); 
        }}
        
        /* 5. TABS & SIDEBAR */
        .stTabs [data-baseweb="tab-list"] {{ gap: 24px; padding-bottom: 10px; }}
        .stTabs [data-baseweb="tab"] {{ height: 55px; font-size: 18px; font-weight: 700; background-color: transparent; }}
        [data-testid="stSidebar"] {{ background-color: {card}; border-right: 1px solid {border}; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    return 'plotly_dark' if theme_choice == 'Dark (SCADA)' else 'plotly_white'

# --- 1. LOGIN & BOOT SEQUENCE ---
if not st.session_state.logged_in:
    st.markdown("<style>.stApp { background-color: #030712; }</style>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.write("")
        st.write("")
        st.write("")
        st.markdown("<h1 style='text-align: center; color: #ff003c; letter-spacing: 4px;'>HPCL NEXUS CORE</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748b; font-family: monospace;'>Level 5 Enterprise Authorization Required</p>", unsafe_allow_html=True)
        st.write("")

        if st.session_state.booting:
            loader_css = """
            <style>
            .loader { border: 4px solid rgba(255, 0, 60, 0.1); border-left-color: #ff003c; border-radius: 50%; width: 60px; height: 60px; animation: spin 1s cubic-bezier(0.4, 0, 0.2, 1) infinite; margin: 0 auto; }
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            .terminal { text-align: center; color: #00ff9d; font-family: monospace; margin-top: 20px; font-size: 14px;}
            </style>
            <div class="loader"></div>
            <div class="terminal" id="term-text">Establishing Secure Uplink to SCADA Nodes...</div>
            """
            st.markdown(loader_css, unsafe_allow_html=True)
            time.sleep(2.0) 
            st.session_state.logged_in = True
            st.session_state.booting = False
            st.rerun()
            
        else:
            with st.form("login_form"):
                username = st.text_input("Administrator ID", value="Admin")
                password = st.text_input("Cryptographic Protocol", type="password", value="admin123")
                submitted = st.form_submit_button("INITIATE HANDSHAKE", use_container_width=True)
                
                if submitted:
                    if username == "Admin" and password == "admin123":
                        st.session_state.booting = True
                        st.rerun()
                    else:
                        st.error("⚠️ AUTHENTICATION FAILED. INCIDENT LOGGED.")

# --- 2. MAIN APPLICATION (THE WAR ROOM) ---
else:
    # Top Bar
    top_col1, top_col2, top_col3 = st.columns([4, 2, 1])
    with top_col1:
        st.markdown(f"## ⚡ HPCL Central Command Node")
        st.caption("Active Session: Admin | Clearance: MAX | Encryption: 256-bit AES")
    
    with top_col2:
        # FIXED: Removed manual session state assignment. We now use the 'key' attribute.
        # This completely resolves the "double-click" bug.
        st.selectbox("UI Protocol", ['Dark (SCADA)', 'Executive (Light)'], key='ui_theme', label_visibility="collapsed")
    
    with top_col3:
        if st.button("TERMINATE SESSION", use_container_width=True, type="primary"):
            st.session_state.logged_in = False
            st.rerun()
            
    # Apply theme based on the natively managed widget key
    current_theme = st.session_state.ui_theme
    plotly_theme = inject_theme(current_theme)
    theme_accent = '#ff003c' if current_theme == 'Dark (SCADA)' else '#2563eb'
    theme_fill = 'rgba(255, 0, 60, 0.15)' if current_theme == 'Dark (SCADA)' else 'rgba(37, 99, 235, 0.15)'
    color_seq = px.colors.sequential.Inferno if current_theme == 'Dark (SCADA)' else px.colors.sequential.Blues

    # --- SIDEBAR: RUNTIME DATA INJECTION ---
    with st.sidebar:
        st.markdown("### 🎛️ Simulation Parameters")
        st.caption("Manipulate core variables to forecast operational impact in real-time.")
        st.markdown("---")
        
        st.markdown("**Level 1: Strategic Overrides**")
        crude_multiplier = st.slider("Global Crude Cost Index ($/bbl)", 0.5, 2.0, 1.0, 0.1)
        demand_multiplier = st.slider("Market Demand Surge/Drop", 0.5, 1.5, 1.0, 0.05)
        
        st.markdown("---")
        st.markdown("**Level 2/3: Operational Anomalies**")
        throughput_efficiency = st.slider("Refinery Yield Efficiency (%)", 70, 100, 95)
        pipeline_latency = st.slider("Pipeline Network Latency (ms)", 10, 200, 25)

    # Apply Simulation Modifiers
    df = base_df.copy()
    df['Cost_Cr'] = df['Base_Cost'] * crude_multiplier
    df['Volume_kL'] = df['Volume_kL'] * demand_multiplier
    df['Revenue_Cr'] = (df['Base_Revenue'] * demand_multiplier) * (throughput_efficiency / 100)
    df['Profit_Cr'] = df['Revenue_Cr'] - df['Cost_Cr']

    st.markdown("---")

    # --- NAVIGATION TABS ---
    tab1, tab2, tab3 = st.tabs([
        "🌐 Level 1: EIS", 
        "📊 Level 2: MIS", 
        "⚙️ Level 3: TPS"
    ])

    # --- TAB 1: EXECUTIVE INFORMATION SYSTEM ---
    with tab1:
        st.markdown("#### Strategic Executive Intelligence & Market Matrix")
        
        total_rev = df['Revenue_Cr'].sum()
        total_prof = df['Profit_Cr'].sum()
        target_prof = base_df['Base_Revenue'].sum() - base_df['Base_Cost'].sum()
        prof_delta = ((total_prof - target_prof) / target_prof) * 100

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Adjusted Revenue (YTD)", f"₹{total_rev:,.1f} Cr", f"{int(demand_multiplier*100 - 100)}% Demand Shift", delta_color="normal")
        kpi2.metric("Simulated Net Profit", f"₹{total_prof:,.1f} Cr", f"{prof_delta:.1f}% vs Baseline", delta_color="normal" if prof_delta >=0 else "inverse")
        kpi3.metric("Refinery Throughput Target", f"{throughput_efficiency}%", "Override Active" if throughput_efficiency < 100 else "Optimal")
        kpi4.metric("AI Predictive Demand Q3", f"{df['AI_Forecast_Demand'].sum() * demand_multiplier:,.0f} kL", "Algorithm Synced")

        st.write("")
        c1, c2 = st.columns([2, 1])
        
        with c1:
            st.markdown("**Live Financial Trajectory vs Predictive AI Model**")
            trend_df = df.groupby('Date')[['Revenue_Cr', 'Cost_Cr']].sum().reset_index()
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(x=trend_df['Date'], y=trend_df['Revenue_Cr'], name='Gross Revenue', fill='tozeroy', fillcolor=theme_fill, line=dict(color=theme_accent, width=3)))
            fig_trend.add_trace(go.Scatter(x=trend_df['Date'], y=trend_df['Cost_Cr'], name='Operating Cost', line=dict(color='#8b5cf6', width=2, dash='dot')))
            fig_trend.update_layout(template=plotly_theme, height=350, margin=dict(t=10, b=10, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig_trend, use_container_width=True)

        with c2:
            st.markdown("**Enterprise Risk Radar (Live)**")
            risk_crude = min(5, crude_multiplier * 2.5)
            risk_op = min(5, (100 - throughput_efficiency) / 5)
            fig_radar = go.Figure(data=go.Scatterpolar(
              r=[risk_crude, 2.0, 1.5, risk_op, 3.2],
              theta=['Market Risk', 'Liquidity', 'Compliance', 'Operational', 'Geopolitical'],
              fill='toself', fillcolor=theme_fill, line_color=theme_accent
            ))
            fig_radar.update_layout(template=plotly_theme, polar=dict(radialaxis=dict(visible=True, range=[0, 5])), height=350, margin=dict(t=30, b=30), paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_radar, use_container_width=True)

    # --- TAB 2: MANAGEMENT INFORMATION SYSTEM ---
    with tab2:
        st.markdown("#### Tactical Supply Chain & Inventory Mechanics")
        
        col_a, col_b = st.columns([1, 1])
        
        with col_a:
            st.markdown("**Regional Yield Margin Heatmap**")
            pivot = df.pivot_table(values='Profit_Cr', index='Product', columns='Region', aggfunc='mean')
            fig_heat = px.imshow(pivot, text_auto=".1f", aspect="auto", color_continuous_scale=color_seq, template=plotly_theme)
            fig_heat.update_layout(height=400, margin=dict(t=10), paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_heat, use_container_width=True)
            
        with col_b:
            st.markdown("**Product Distribution Sunburst (Volume)**")
            fig_sun = px.sunburst(df, path=['Region', 'Product'], values='Volume_kL', template=plotly_theme, color_discrete_sequence=color_seq)
            fig_sun.update_layout(height=400, margin=dict(t=10, b=10, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_sun, use_container_width=True)

    # --- TAB 3: TRANSACTION PROCESSING SYSTEM ---
    with tab3:
        st.markdown("#### Real-Time SCADA Telemetry & Cryptographic Ledger")
        
        gauge_col1, gauge_col2, gauge_col3 = st.columns(3)
        gauge_color = "#00ff9d" if current_theme == 'Dark (SCADA)' else theme_accent
        
        def make_gauge(val, title, max_val=100, reverse_color=False):
            color = "#ff003c" if (reverse_color and val > 100) or (not reverse_color and val < 80) else gauge_color
            fig = go.Figure(go.Indicator(
                mode = "gauge+number", value = val,
                title = {'text': title, 'font': {'size': 14}},
                gauge = {'axis': {'range': [None, max_val]}, 'bar': {'color': color}, 'borderwidth': 0, 'bgcolor': "rgba(150,150,150,0.1)"}))
            fig.update_layout(template=plotly_theme, height=220, margin=dict(t=30, b=10), paper_bgcolor='rgba(0,0,0,0)')
            return fig

        v_load = throughput_efficiency - np.random.randint(1, 5)
        m_load = throughput_efficiency - np.random.randint(0, 3)
        
        gauge_col1.plotly_chart(make_gauge(m_load, "Mumbai Unit Load %"), use_container_width=True)
        gauge_col2.plotly_chart(make_gauge(v_load, "Visakh Unit Load %"), use_container_width=True)
        gauge_col3.plotly_chart(make_gauge(pipeline_latency, "Network Latency (ms)", 250, True), use_container_width=True)

        st.markdown("**Live Node Ledger (Auto-Syncing)**")
        
        live_df = df.sample(6).sort_values('Date', ascending=False).reset_index(drop=True)
        live_df['Hash_Protocol'] = [f"0x{np.random.bytes(5).hex().upper()}" for _ in range(6)]
        live_df['Integrity'] = ["VERIFIED" if pipeline_latency < 150 else "WARN_LATENCY" for _ in range(6)]
        live_df = live_df[['Hash_Protocol', 'Region', 'Product', 'Volume_kL', 'Integrity']]
        
        st.dataframe(live_df, use_container_width=True, hide_index=True)