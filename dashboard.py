import pandas as pd
import streamlit as st
import plotly.express as px

# ===================
# Page Config
# ===================
st.set_page_config(layout="wide", page_title="Seizure Management Dashboard")

# Query params
query_params = st.query_params
user = "".join(query_params.get("patient_id", [""]))
if user == "":
    user = "47598"

# Hide Streamlit menu and footer
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    [data-testid="stHeader"] a, 
    [data-testid="stMarkdownContainer"] a {
        display: none !important;
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ===================
# Example patient lookup (replace with real patient metadata if available)
# ===================
patient_info = {
    "47597": {"Name": "Surya Prakash", "Age": 56},
    "47598": {"Name": "Sri Latha", "Age": 45}
}

# Get patient name + age
patient_name = patient_info.get(user, {}).get("Name", "Unknown Patient")
patient_age = patient_info.get(user, {}).get("Age", "N/A")

# ===================
# Dashboard Header with Export Button
# ===================
col1, col2 = st.columns([4, 1])  # wider left column

with col1:
    st.markdown(
        f"""
        <div style='text-align: center;'>
            <h1 style='margin-bottom:0;'>⚡ Seizure Management Dashboard</h1>
            <h3 style='color:#555; margin-top:5px;'>
                {patient_name} &nbsp; | &nbsp; Age: {patient_age}
            </h3>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)  # spacer for alignment
    st.download_button(
        label="Export Data",
        data=open("sample.xlsx", "rb").read(),
        file_name=f"{patient_name}_seizure_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ===================
# Load Data
# ===================
file_path = "sample.xlsx"
df1 = pd.read_excel(file_path, sheet_name="Patient Data")
df2 = pd.read_excel(file_path, sheet_name="Type Distribution")
df3 = pd.read_excel(file_path, sheet_name="Side Effects")

df1["Patient_ID"] = df1["Patient_ID"].astype(str)
df2["Patient_ID"] = df2["Patient_ID"].astype(str)
df3["Patient_ID"] = df3["Patient_ID"].astype(str)

df1 = df1[df1['Patient_ID'] == user]
df2 = df2[df2['Patient_ID'] == user]
df3 = df3[df3['Patient_ID'] == user]

df1["ConsultationDate"] = pd.to_datetime(df1["ConsultationDate"], errors="coerce")

# Get global date range for x-axis sync
date_min, date_max = df1["ConsultationDate"].min(), df1["ConsultationDate"].max()


# KPI Metrics with Delta + Colors
# ===================
latest = df1.sort_values("ConsultationDate").iloc[-1]
previous = df1.sort_values("ConsultationDate").iloc[-2] if len(df1) > 1 else latest

col_a, col_b, col_c, col_d = st.columns(4)

# Seizure Count ↓ is better → green
delta_seizure = int(latest["SeizureCount"] - previous["SeizureCount"])
col_a.metric("Last Seizure Count", int(latest["SeizureCount"]),
             delta=delta_seizure,
             delta_color="inverse")  # ↓ = green, ↑ = red

# Avg Duration ↓ is better → green
delta_duration = float(latest["AvgDuration(min)"] - previous["AvgDuration(min)"])
col_b.metric("Avg Duration (min)", float(latest["AvgDuration(min)"]),
             delta=delta_duration,
             delta_color="inverse")  # ↓ = green, ↑ = red

# Medication Adherence ↑ is better → green
delta_adherence = float(latest["MedicationAdherence(%)"] - previous["MedicationAdherence(%)"])
col_c.metric("Medication Adherence (%)", f"{latest['MedicationAdherence(%)']}%",
             delta=f"{delta_adherence:.1f}%",
             delta_color="normal")  # ↑ = green, ↓ = red

# SUDEP Risk ↓ is better → green
delta_risk = int(latest["SUDEP_RiskScore"] - previous["SUDEP_RiskScore"])
col_d.metric("SUDEP Risk Score", int(latest["SUDEP_RiskScore"]),
             delta=delta_risk,
             delta_color="inverse")  # ↓ = green, ↑ = red

# ===================
# Row 2: Seizure Count, Duration, Adherence
# ===================
col1, col2, col3 = st.columns(3)

# ---- Chart 1: Seizure Count ----
with col1:
    st.subheader("Seizure Count Over Time")
    fig = px.line(
        df1, x="ConsultationDate", y="SeizureCount", markers=True,
        labels={"ConsultationDate": "Date", "SeizureCount": "Seizures"},
        color_discrete_sequence=["#FF8800"]
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=8))
    fig.update_layout(
        xaxis_range=[date_min, date_max],
        yaxis_title="Seizure Count"
    )
    st.plotly_chart(fig, use_container_width=True)

# ---- Chart 2: Seizure Duration ----
with col2:
    st.subheader("Seizure Duration Trend")
    fig = px.line(
        df1, x="ConsultationDate", y="AvgDuration(min)", markers=True,
        labels={"ConsultationDate": "Date", "AvgDuration(min)": "Minutes"},
        color_discrete_sequence=["#2ECC71"]
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=8))
    fig.update_layout(
        xaxis_range=[date_min, date_max],
        yaxis_title="Avg Duration (min)"
    )
    st.plotly_chart(fig, use_container_width=True)

# ---- Chart 3: Medication Adherence ----
with col3:
    st.subheader("Medication Adherence (%)")
    fig = px.line(
        df1, x="ConsultationDate", y="MedicationAdherence(%)", markers=True,
        labels={"ConsultationDate": "Date", "MedicationAdherence(%)": "Adherence %"},
        color_discrete_sequence=["#3498DB"]
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=8))
    fig.update_layout(
        xaxis_range=[date_min, date_max],
        yaxis_title="Adherence (%)"
    )
    st.plotly_chart(fig, use_container_width=True)


# ===================
# Row 3: SUDEP Risk + Seizure Type Pie
# ===================
col4, col5 = st.columns(2)

with col4:
    st.subheader("SUDEP Risk Score Trend")
    fig = px.line(
        df1, x="ConsultationDate", y="SUDEP_RiskScore", markers=True,
        labels={"ConsultationDate": "Date", "SUDEP_RiskScore": "Risk Score"},
        color_discrete_sequence=["#E74C3C"]  # clean red
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=8))
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Risk Score"
    )
    st.plotly_chart(fig, use_container_width=True)


with col5:
    st.subheader("Seizure Type Distribution")
    fig = px.pie(df2, names="SeizureType", values="Count",
                 hole=0.3, color_discrete_sequence=px.colors.qualitative.Set3)
    fig.update_traces(textinfo="percent+label")
    st.plotly_chart(fig, use_container_width=True)

# ===================
# Row 4: Side Effects
# ===================
st.subheader("Reported Side Effects")
df3["SideEffect"] = df3["SideEffect"].fillna("None").astype(str).str.strip()
fig = px.bar(df3, x="SideEffect", y="Count",
             text="Count", color="SideEffect",
             color_discrete_sequence=px.colors.qualitative.Set2)
fig.update_layout(xaxis_title="", yaxis_title="Count", showlegend=False)
fig.update_traces(textposition="outside")
st.plotly_chart(fig, use_container_width=True)
