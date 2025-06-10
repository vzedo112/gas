import streamlit as st
import pandas as pd
import plotly.express as px
import os
import statsmodels.api as sm

st.set_page_config(page_title="Gas vs HDD Dashboard", layout="wide")

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("gas/gas.csv", dtype=str)
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
    df["Year"] = df["Year"].astype(str)
    df["Month"] = df["Month"].astype(str)
    df["Hdd"] = pd.to_numeric(df["Hdd"], errors="coerce")
    df["Gas (kWh)"] = pd.to_numeric(df["Gas (kWh)"], errors="coerce")
    return df

df = load_data()

# --- Sidebar Filters ---
st.markdown("**Gas vs HDD Dashbaord**")

col1, col2 = st.columns(2)

# Year Filter
years = ["All"] + sorted(df["Year"].unique().tolist())
with col1:
    selected_years = st.multiselect("Select Year(s)", options=years, default=["All"])

# Month Filter

months = ["All"] + sorted(df["Month"].unique().tolist(), key=lambda x: pd.to_datetime(x, format='%b').month if x != "All" else 0)
with col2:
    selected_months = st.multiselect("Select Month(s)", options=months, default=["All"])

# --- Apply Filters ---
filtered_df = df.copy()
if "All" not in selected_years:
    filtered_df = filtered_df[filtered_df["Year"].isin(selected_years)]
if "All" not in selected_months:
    filtered_df = filtered_df[filtered_df["Month"].isin(selected_months)]

# --- Regression Analysis Chart (Gas vs HDD) ---

col3 = st.columns(1)[0]

with col3:
    group_by = st.selectbox(
        "Group regression by:",
        options=["Year", "Month (per Year)"],
        index=0
    )

if group_by == "Year":
    color_col = "Year"
else:
    filtered_df["Month-Year"] = filtered_df["Month"] + "-" + filtered_df["Year"]
    color_col = "Month-Year"
st.divider()
if not filtered_df.empty:
    fig = px.scatter(
        filtered_df,
        x="Hdd",
        y="Gas (kWh)",
        color=color_col,
        trendline="ols",
        hover_data=["Date", "Year", "Month"],
        title=f"Gas Usage vs Heating Degree Days (HDD) by {color_col}",
    )
    fig.update_layout(
        template="plotly_white",
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True)
    )
    st.plotly_chart(fig, use_container_width=True)
    st.divider()
    # --- R^2 Calculation for Each Group ---
    r2_results = {}
    for group in filtered_df[color_col].unique():
        df_group = filtered_df[filtered_df[color_col] == group]
        if len(df_group) > 1 and df_group["Hdd"].notna().sum() > 1 and df_group["Gas (kWh)"].notna().sum() > 1:
            X = df_group["Hdd"]
            y = df_group["Gas (kWh)"]
            X = sm.add_constant(X)
            model = sm.OLS(y, X, missing='drop').fit()
            r2 = model.rsquared
            r2_results[group] = r2
        else:
            r2_results[group] = None

    st.markdown(f"**R² (Coefficient of Determination) for Each {color_col}:**")
    for group, r2 in sorted(r2_results.items(), key=lambda x: x[0]):
        if r2 is not None:
            st.markdown(f"- **{group}**: {r2:.3f}")
        else:
            st.markdown(f"- **{group}**: Not enough data")
else:
    st.warning("No data available for the selected filters.")

