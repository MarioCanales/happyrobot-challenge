import streamlit as st
import pandas as pd
import requests
import os
import plotly.express as px
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
API_KEY = os.getenv("SERVICE_API_KEY", "my-super-secret-password")

st.set_page_config(page_title="Freight Sales Dashboard", layout="wide")

st.title("🚛 Inbound Carrier Sales Dashboard")

# --- Fetch Data ---
@st.cache_data(ttl=5) # Cache data for 5 seconds
def fetch_data():
    headers = {"X-API-Key": API_KEY}
    try:
        response = requests.get(f"{API_URL}/logs", headers=headers)
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        else:
            st.error(f"Error fetching data: {response.status_code}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Connection error: {e}")
        return pd.DataFrame()

df = fetch_data()

if not df.empty:
    # --- Metrics Section ---
    st.header("Real-time Performance")
    
    # Calculate Metrics
    total_calls = len(df)
    booked_loads = len(df[df['outcome'] == 'booked'])
    failed_negs = len(df[df['outcome'] == 'negotiation_failed'])
    
    # Revenue Calculation (Sum of rates)
    revenue = df['offered_rate'].sum() if 'offered_rate' in df.columns else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Calls", total_calls)
    col2.metric("Loads Booked", booked_loads)
    col3.metric("Negotiations Failed", failed_negs)
    col4.metric("Total Revenue", f"${revenue:,.2f}")

    st.markdown("---")

    # --- Charts Section ---
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Call Outcomes")
        if 'outcome' in df.columns:
            outcome_counts = df['outcome'].value_counts().reset_index()
            outcome_counts.columns = ['outcome', 'count']
            fig_outcome = px.pie(outcome_counts, values='count', names='outcome', hole=0.4)
            st.plotly_chart(fig_outcome, use_container_width=True)

    with c2:
        st.subheader("Carrier Sentiment")
        if 'sentiment' in df.columns:
            sentiment_counts = df['sentiment'].value_counts().reset_index()
            sentiment_counts.columns = ['sentiment', 'count']
            fig_sent = px.bar(sentiment_counts, x='sentiment', y='count', color='sentiment')
            st.plotly_chart(fig_sent, use_container_width=True)

    # --- Raw Data Table ---
    st.subheader("Recent Call Logs")
    st.dataframe(df[['created_at', 'carrier_mc', 'load_id_ref', 'offered_rate', 'outcome', 'sentiment']])

else:
    st.info("No call data available yet. Waiting for calls...")

# Manual Refresh Button
if st.button('Refresh Data'):
    st.rerun()