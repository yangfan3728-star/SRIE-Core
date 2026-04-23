"""
SRIE System Health & Evolution Dashboard
Streamlit App to visualize system performance and evolution over time.
"""

import streamlit as st
import plotly.express as px
import pandas as pd
import os
import json
import glob
from datetime import datetime

st.set_page_config(page_title="SRIE Evolution Dashboard", layout="wide")
st.title("📊 SRIE System Health & Evolution Dashboard")

base_dir = os.path.dirname(os.path.abspath(__file__))
logs_dir = os.path.join(base_dir, "logs")
reports_dir = os.path.join(base_dir, "reports")

# --- Data Loading ---
@st.cache_data
def load_data():
    intro_data = []
    exec_data = []
    
    # Load Introspection Logs
    for f in glob.glob(os.path.join(logs_dir, "introspection_*.json")):
        try:
            with open(f, 'r') as file:
                data = json.load(file)
                ts = data.get("timestamp", "")
                intro_data.append({
                    "time": ts,
                    "accuracy": data.get("model_performance", {}).get("accuracy"),
                    "f1_score": data.get("model_performance", {}).get("f1_score"),
                    "quality_issues": data.get("code_quality", {}).get("issues_count"),
                    "deps_outdated": data.get("dependency_health", {}).get("outdated_count"),
                    "status": data.get("summary", {}).get("status")
                })
        except: pass

    # Load Orchestrator Reports
    for f in glob.glob(os.path.join(reports_dir, "orchestrator_*.json")):
        try:
            with open(f, 'r') as file:
                data = json.load(file)
                ts = data.get("timestamp", "")
                # Check threshold in actions or result?
                # We assume the plan modified the threshold
                exec_data.append({
                    "time": ts,
                    "status": data.get("status"),
                    "mode": data.get("mode")
                })
        except: pass

    return pd.DataFrame(intro_data), pd.DataFrame(exec_data)

df_intro, df_exec = load_data()

if df_intro.empty:
    st.warning("No introspection data found yet. Run `orchestrator.py` to generate data.")
else:
    # Convert time to datetime
    df_intro['time'] = pd.to_datetime(df_intro['time'])
    df_intro = df_intro.sort_values('time')

    # --- Metrics Row ---
    st.subheader("📈 Key Metrics Trend")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'accuracy' in df_intro.columns and df_intro['accuracy'].dropna().any():
            fig_acc = px.line(df_intro.dropna(subset=['accuracy']), x='time', y='accuracy', markers=True, title="Prediction Accuracy")
            st.plotly_chart(fig_acc, use_container_width=True)
        else:
            st.info("Accuracy data not yet available.")

    with col2:
        if 'quality_issues' in df_intro.columns and df_intro['quality_issues'].dropna().any():
            fig_q = px.line(df_intro.dropna(subset=['quality_issues']), x='time', y='quality_issues', markers=True, title="Code Quality Issues (Lower is Better)")
            st.plotly_chart(fig_q, use_container_width=True)
        else:
            st.info("Code quality data not yet available.")

    with col3:
        if 'deps_outdated' in df_intro.columns and df_intro['deps_outdated'].dropna().any():
            fig_dep = px.bar(df_intro.dropna(subset=['deps_outdated']), x='time', y='deps_outdated', title="Outdated Dependencies")
            st.plotly_chart(fig_dep, use_container_width=True)
        else:
            st.info("Dependency data not yet available.")

    # --- Execution History ---
    st.subheader("🔄 Execution History")
    if not df_exec.empty:
        df_exec['time'] = pd.to_datetime(df_exec['time'])
        st.dataframe(df_exec.sort_values('time', ascending=False).head(10), use_container_width=True)
    else:
        st.info("No execution reports found.")

    # --- System Status ---
    st.subheader("🩺 System Status")
    last_status = df_intro['status'].iloc[-1] if 'status' in df_intro.columns else "UNKNOWN"
    st.success(f"Current Status: {last_status}") if last_status == "HEALTHY" else st.warning(f"Current Status: {last_status}")
