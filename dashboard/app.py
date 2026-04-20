from recommendation import recommend_category
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from anomaly import analyze_users

st.set_page_config(page_title="User Behavior Dashboard", layout="wide")

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/user_events_db"
engine = create_engine(DATABASE_URL)

st.title("📊 User Behavior Analytics Dashboard")

# Load data
query = "SELECT * FROM events ORDER BY id DESC;"
df = pd.read_sql(query, engine)

if df.empty:
    st.warning("No events found in database.")
    st.stop()

# Prepare data
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Sidebar filters
st.sidebar.header("Filters")

user_ids = ["All"] + sorted(df["user_id"].dropna().astype(str).unique().tolist())
event_types = ["All"] + sorted(df["event_type"].dropna().astype(str).unique().tolist())
pages = ["All"] + sorted(df["page"].dropna().astype(str).unique().tolist())

selected_user = st.sidebar.selectbox("User ID", user_ids)
selected_event = st.sidebar.selectbox("Event Type", event_types)
selected_page = st.sidebar.selectbox("Page", pages)

filtered_df = df.copy()

if selected_user != "All":
    filtered_df = filtered_df[filtered_df["user_id"].astype(str) == selected_user]

if selected_event != "All":
    filtered_df = filtered_df[filtered_df["event_type"] == selected_event]

if selected_page != "All":
    filtered_df = filtered_df[filtered_df["page"] == selected_page]

if filtered_df.empty:
    st.warning("No data for selected filters.")
    st.stop()

# KPI cards
total_events = len(filtered_df)
total_users = filtered_df["user_id"].nunique()

top_page = (
    filtered_df["page"].mode().iloc[0]
    if filtered_df["page"].dropna().shape[0] > 0
    else "N/A"
)

top_event = (
    filtered_df["event_type"].mode().iloc[0]
    if filtered_df["event_type"].dropna().shape[0] > 0
    else "N/A"
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Events", total_events)
col2.metric("Total Users", total_users)
col3.metric("Top Page", top_page)
col4.metric("Top Event", top_event)

st.markdown("---")

# Charts row 1
c1, c2 = st.columns(2)

with c1:
    st.subheader("Event Type Distribution")
    event_counts = filtered_df["event_type"].value_counts().reset_index()
    event_counts.columns = ["event_type", "count"]
    fig1 = px.bar(
        event_counts,
        x="event_type",
        y="count",
        title="Events by Type"
    )
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    st.subheader("Top Pages")
    page_counts = filtered_df["page"].value_counts().reset_index()
    page_counts.columns = ["page", "count"]
    fig2 = px.bar(
        page_counts,
        x="page",
        y="count",
        title="Page Popularity"
    )
    st.plotly_chart(fig2, use_container_width=True)

# Charts row 2
c3, c4 = st.columns(2)

with c3:
    st.subheader("Active Users")
    user_counts = filtered_df["user_id"].value_counts().reset_index()
    user_counts.columns = ["user_id", "count"]
    fig3 = px.bar(
        user_counts,
        x="user_id",
        y="count",
        title="User Activity"
    )
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    st.subheader("Events Over Time")
    time_counts = (
        filtered_df.groupby(filtered_df["timestamp"].dt.floor("min"))
        .size()
        .reset_index(name="count")
    )
    fig4 = px.line(
        time_counts,
        x="timestamp",
        y="count",
        title="Events per Minute"
    )
    st.plotly_chart(fig4, use_container_width=True)

# Extra charts
c5, c6 = st.columns(2)

with c5:
    st.subheader("Category Distribution")
    category_df = filtered_df.dropna(subset=["category"])
    if not category_df.empty:
        category_counts = category_df["category"].value_counts().reset_index()
        category_counts.columns = ["category", "count"]
        fig5 = px.pie(
            category_counts,
            names="category",
            values="count",
            title="Categories"
        )
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("No category data available.")

with c6:
    st.subheader("Top Products")
    product_df = filtered_df.dropna(subset=["product_id"])
    if not product_df.empty:
        product_counts = product_df["product_id"].value_counts().reset_index()
        product_counts.columns = ["product_id", "count"]
        fig6 = px.bar(
            product_counts,
            x="product_id",
            y="count",
            title="Top Products"
        )
        st.plotly_chart(fig6, use_container_width=True)
    else:
        st.info("No product data available.")

st.markdown("---")

# Basic insights
st.subheader("Insights")

most_active_user_simple = filtered_df["user_id"].value_counts().idxmax()
most_active_user_count_simple = filtered_df["user_id"].value_counts().max()

insight_text = f"""
- Most active user: **{most_active_user_simple}** with **{most_active_user_count_simple}** events  
- Most popular page: **{top_page}**  
- Most frequent event type: **{top_event}**  
- Unique users in current selection: **{total_users}**
"""
st.markdown(insight_text)

st.markdown("---")

# User analysis
st.subheader("User Analysis (Fraud & Segmentation)")

user_analysis = analyze_users(filtered_df)

st.dataframe(user_analysis, use_container_width=True)

suspicious = user_analysis[user_analysis["status"] == "suspicious"]

if not suspicious.empty:
    st.error("🚨 Suspicious users detected!")
    st.dataframe(suspicious, use_container_width=True)
else:
    st.success("No suspicious users detected.")

st.subheader("User Segments")

segment_counts = user_analysis["segment"].value_counts().reset_index()
segment_counts.columns = ["segment", "count"]

fig7 = px.pie(segment_counts, names="segment", values="count", title="User Segmentation")
st.plotly_chart(fig7, use_container_width=True)

st.subheader("Smart Insights")

most_active_user = user_analysis.loc[user_analysis["event_count"].idxmax()]

smart_insight_text = f"""
🔍 **System Insights:**

- Most active user: **{most_active_user['user_id']}** with **{most_active_user['event_count']}** events  
- Fraud risk level (max): **{round(user_analysis['fraud_score'].max(), 2)}**  
- Dominant user segment: **{user_analysis['segment'].mode().iloc[0]}**
"""

st.markdown(smart_insight_text)

st.markdown("---")


st.markdown("---")
st.subheader("Recommendations")

recommendation_df = recommend_category(filtered_df)

if recommendation_df.empty:
    st.info("No recommendation data available.")
else:
    st.dataframe(recommendation_df, use_container_width=True)

    fig8 = px.bar(
        recommendation_df,
        x="user_id",
        y="recommended_category",
        title="Recommended Category by User"
    )
    st.plotly_chart(fig8, use_container_width=True)
# Latest events
st.subheader("Latest Events")
st.dataframe(filtered_df.head(20), use_container_width=True)