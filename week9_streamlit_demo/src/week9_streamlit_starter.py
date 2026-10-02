"""
Streamlit Barebone Starter -- Week 9
========================================
Clone this repo, then run:
    uv run streamlit run src/week9_streamlit_starter.py

This is intentionally minimal. In class we will build it up together:
    - add sidebar filters
    - add KPI metrics
    - add a drilldown chart with a dimension/metric picker
    - publish it to Streamlit Community Cloud

Data source: processed_data_cube.csv, produced by running main.py
(the cube is created by create_cubes() in stage_3_aggregate.py).
"""

from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Home Credit Dashboard", layout="wide")

DATA_PATH = Path(__file__).resolve().parent.parent / "data"/  "processed_data_cube.csv"


@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)


def main():
    st.title("Home Credit Dashboard")
    st.markdown("Starter dashboard -- we'll build this up together in class.")

    df = load_data()

    min_month = int(df["MONTH_APPLIED"].min())
    max_month = int(df["MONTH_APPLIED"].max())

    if "month_range" not in st.session_state:
        st.session_state["month_range"] = (min_month, max_month)

    st.subheader("Filters")
    month_range = st.slider(
        "Month applied range",
        min_value=min_month,
        max_value=max_month,
        value=st.session_state["month_range"],
        key="month_range",
    )

    filtered_df = df[
        (df["MONTH_APPLIED"] >= month_range[0])
        & (df["MONTH_APPLIED"] <= month_range[1])
    ].copy()

    total_applications_raw = filtered_df["total_applications"].sum()
    total_applications = total_applications_raw / 1000
    default_rate = (
        filtered_df["total_defaults"].sum() / total_applications_raw * 100
        if total_applications_raw else 0
    )
    total_credit_millions = filtered_df["total_credit"].sum() / 1_000_000

    kpi_cols = st.columns(3)
    kpi_cols[0].metric("Total Applications", f"{total_applications:,.1f}K")
    kpi_cols[1].metric("Default Rate", f"{default_rate:.2f}%")
    kpi_cols[2].metric("Total Credit", f"${total_credit_millions:,.1f}M")

    st.subheader(f"Data cube preview ({month_range[0]} to {month_range[1]})")
    st.dataframe(filtered_df.head(20), width='stretch')

    st.subheader("Contract type by years employed group")
    years_employed_df = (
        filtered_df.groupby(["YEARS_EMPLOYED_GROUP", "NAME_CONTRACT_TYPE"], as_index=False)
        .agg({"total_applications": "sum"})
        .sort_values(["YEARS_EMPLOYED_GROUP", "total_applications"], ascending=[True, False])
    )
    years_employed_fig = px.bar(
        years_employed_df,
        x="NAME_CONTRACT_TYPE",
        y="total_applications",
        color="YEARS_EMPLOYED_GROUP",
        barmode="group",
        color_discrete_sequence=["#3B82F6", "#10B981", "#8B5CF6"],
        title="Applications by contract type and years employed group",
    )
    st.plotly_chart(years_employed_fig, use_container_width=True)

    st.subheader("Gender group distribution")
    gender_options = sorted(filtered_df["AGE_GENDER_SEGMENT"].dropna().unique().tolist())
    selected_genders = []
    gender_filter_cols = st.columns(min(len(gender_options), 3))

    for i, gender in enumerate(gender_options):
        is_selected = gender_filter_cols[i % len(gender_filter_cols)].checkbox(
            gender,
            value=True,
            key=f"gender_checkbox_{gender}",
        )
        if is_selected:
            selected_genders.append(gender)

    if selected_genders:
        gender_chart_df = (
            filtered_df[filtered_df["AGE_GENDER_SEGMENT"].isin(selected_genders)]
            .groupby("AGE_GENDER_SEGMENT", as_index=False)
            .agg({"total_applications": "sum"})
            .sort_values("total_applications", ascending=False)
        )

        gender_fig = px.bar(
            gender_chart_df,
            x="AGE_GENDER_SEGMENT",
            y="total_applications",
            color="AGE_GENDER_SEGMENT",
            color_discrete_sequence=["#3B82F6", "#10B981", "#8B5CF6"],
            title="Application distribution by gender group",
        )
        gender_fig.update_layout(showlegend=False)
        st.plotly_chart(gender_fig, use_container_width=True)

        burden_df = (
            filtered_df[filtered_df["AGE_GENDER_SEGMENT"].isin(selected_genders)]
            .groupby(["AGE_GENDER_SEGMENT", "BURDEN_CAT"], as_index=False)
            .agg({"total_applications": "sum"})
            .sort_values(["AGE_GENDER_SEGMENT", "BURDEN_CAT"])
        )

        burden_fig = px.bar(
            burden_df,
            x="BURDEN_CAT",
            y="total_applications",
            color="AGE_GENDER_SEGMENT",
            barmode="group",
            color_discrete_sequence=["#3B82F6", "#10B981", "#8B5CF6"],
            title="How gender relates to burden category",
        )
        st.plotly_chart(burden_fig, use_container_width=True)
    else:
        st.info("No gender groups selected. Choose at least one group to display the charts.")


if __name__ == "__main__":
    main()
