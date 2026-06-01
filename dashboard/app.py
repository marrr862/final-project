import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from collections import Counter
from io import BytesIO
st.set_page_config(
    page_title="User Behavior Analytics Dashboard",
    layout="wide"
)

API_URL = "https://web-production-30c3e.up.railway.app"

st.title("📊 User Behavior Analytics Dashboard")
st.info(
    """
    📌 System Summary

    • FastAPI Backend
    • PostgreSQL Database
    • Kafka Streaming
    • Fraud Detection
    • Recommendation System
    • Engagement Analytics
    • Session Analytics
    • Railway Cloud Deployment
    """
)
st.caption("Cloud-connected dashboard using Railway FastAPI backend")
st.sidebar.header("Live Controls")

auto_refresh = st.sidebar.checkbox("Enable Auto Refresh")

if auto_refresh:
    st.rerun()
# Sidebar
st.sidebar.header("Settings")
api_url = st.sidebar.text_input("API URL", API_URL)

if st.sidebar.button("Refresh Data"):
    st.rerun()

# API helper
def get_data(endpoint):
    try:
        response = requests.get(f"{api_url}{endpoint}", timeout=10)
        if response.status_code == 200:
            return response.json()
        st.error(f"Error {response.status_code}: {response.text}")
        return None
    except Exception as e:
        st.error(f"Could not connect to API: {e}")
        return None

# API status
health = get_data("/health")

if health:
    st.success("✅ Cloud API is online")
else:
    st.error("❌ Cloud API is not available")
    st.stop()

# Load data
events = get_data("/events")
summary = get_data("/analytics/summary")
users = get_data("/analytics/users")
pages = get_data("/analytics/pages")
event_types = get_data("/analytics/events")
categories = get_data("/analytics/categories")
fraud_users = get_data("/fraud/users")

if not events:
    st.warning("No events found.")
    st.stop()

df = pd.DataFrame(events)

if "timestamp" in df.columns:
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="mixed", errors="coerce")

# Filters
st.sidebar.header("Filters")

user_filter = st.sidebar.selectbox(
    "User ID",
    ["All"] + sorted(df["user_id"].dropna().astype(str).unique().tolist())
)

event_filter = st.sidebar.selectbox(
    "Event Type",
    ["All"] + sorted(df["event_type"].dropna().astype(str).unique().tolist())
)

page_filter = st.sidebar.selectbox(
    "Page",
    ["All"] + sorted(df["page"].dropna().astype(str).unique().tolist())
)

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Quick Search")

search_user = st.sidebar.text_input("Search User ID")


filtered_df = df.copy()

if user_filter != "All":
    filtered_df = filtered_df[filtered_df["user_id"].astype(str) == user_filter]

if event_filter != "All":
    filtered_df = filtered_df[filtered_df["event_type"] == event_filter]

if page_filter != "All":
    filtered_df = filtered_df[filtered_df["page"] == page_filter]

if search_user:
    filtered_df = filtered_df[
        filtered_df["user_id"].astype(str).str.contains(search_user)
    ]


# KPI cards
st.subheader("Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Events", summary.get("total_events", 0))
col2.metric("Total Users", summary.get("total_users", 0))
col3.metric("Top Page", summary.get("top_page", "N/A"))
col4.metric("Top Event", summary.get("top_event_type", "N/A"))

st.markdown("---")


st.markdown("---")
st.subheader("🛠 Admin Analytics Panel")

admin1, admin2, admin3, admin4, admin5 = st.columns(5)

most_active_user = filtered_df["user_id"].value_counts().idxmax()
top_category = filtered_df["category"].value_counts().idxmax()

suspicious_count = 0
if fraud_users:
    fraud_df = pd.DataFrame(fraud_users)
    suspicious_count = len(fraud_df[fraud_df["status"] == "suspicious"])

admin1.metric("Total Events", len(filtered_df))
admin2.metric("Total Users", filtered_df["user_id"].nunique())
admin3.metric("Most Active User", most_active_user)
admin4.metric("Suspicious Users", suspicious_count)
admin5.metric("Top Category", top_category)
st.markdown("---")
st.subheader("🥇 Top Users Leaderboard")

top_users = (
    filtered_df["user_id"]
    .value_counts()
    .reset_index()
)

top_users.columns = ["user_id", "events"]

st.dataframe(top_users.head(10), use_container_width=True)

fig_top = px.bar(
    top_users.head(10),
    x="user_id",
    y="events",
    title="Most Active Users"
)

st.plotly_chart(fig_top, use_container_width=True)


st.markdown("---")
st.subheader("📋 Data Quality")

q1, q2, q3 = st.columns(3)

q1.metric("Rows", len(filtered_df))
q2.metric("Missing Values", int(filtered_df.isna().sum().sum()))
q3.metric("Unique Users", filtered_df["user_id"].nunique())
# Charts
c1, c2 = st.columns(2)

with c1:
    st.subheader("Event Types")
    if event_types:
        event_df = pd.DataFrame(event_types)
        fig = px.bar(event_df, x="event_type", y="count", title="Events by Type")
        st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Top Pages")
    if pages:
        pages_df = pd.DataFrame(pages)
        fig = px.bar(pages_df, x="page", y="count", title="Page Popularity")
        st.plotly_chart(fig, use_container_width=True)

c3, c4 = st.columns(2)

with c3:
    st.subheader("Categories")
    if categories:
        cat_df = pd.DataFrame(categories)
        fig = px.pie(cat_df, names="category", values="count", title="Category Distribution")
        st.plotly_chart(fig, use_container_width=True)

with c4:
    st.subheader("Events Over Time")
    if "timestamp" in filtered_df.columns:
        time_df = (
            filtered_df.groupby(filtered_df["timestamp"].dt.floor("min"))
            .size()
            .reset_index(name="count")
        )
        fig = px.line(time_df, x="timestamp", y="count", title="Events per Minute")
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# User analytics
st.subheader("User Analytics")

if users:
    users_df = pd.DataFrame(users)
    st.dataframe(users_df, use_container_width=True)

    if "segment" in users_df.columns:
        segment_df = users_df["segment"].value_counts().reset_index()
        segment_df.columns = ["segment", "count"]
        fig = px.pie(segment_df, names="segment", values="count", title="User Segments")
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Fraud users
st.subheader("Fraud / Suspicious Users")

if fraud_users:
    fraud_df = pd.DataFrame(fraud_users)

    suspicious_df = fraud_df[fraud_df["status"] == "suspicious"]

    if suspicious_df.empty:
        st.success("No suspicious users detected.")
    else:
        st.error("Suspicious users detected!")
        st.dataframe(suspicious_df, use_container_width=True)

    fig = px.bar(
        fraud_df,
        x="user_id",
        y="fraud_score",
        color="status",
        title="Fraud Score by User"
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Recommendation section
st.subheader("Recommendation Test")

recommend_user_id = st.number_input("Enter User ID", min_value=1, step=1)

if st.button("Get Recommendation"):
    recommendation = get_data(f"/recommendations/{recommend_user_id}")
    if recommendation:
        st.success("Recommendation generated")
        st.json(recommendation)

st.markdown("---")
st.markdown("---")

st.subheader("🏆 Top Active Users")

engagement = get_data("/analytics/engagement")

if engagement:
    engagement_df = pd.DataFrame(engagement)

    st.dataframe(
        engagement_df.head(10),
        use_container_width=True
    )

    fig = px.bar(
        engagement_df.head(10),
        x="user_id",
        y="engagement_score",
        color="engagement_level",
        title="Top User Engagement Scores"
    )

    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

st.subheader("🧩 Session Analytics")

session_df = (
    filtered_df.groupby("user_id")
    .agg(
        session_events=("id", "count"),
        first_event=("timestamp", "min"),
        last_event=("timestamp", "max")
    )
    .reset_index()
)

session_df["session_duration_minutes"] = (
    (session_df["last_event"] - session_df["first_event"]).dt.total_seconds() / 60
).round(2)

def get_session_type(count):
    if count <= 3:
        return "Short Session"
    elif count <= 7:
        return "Medium Session"
    else:
        return "Long Session"

session_df["session_type"] = session_df["session_events"].apply(get_session_type)

st.dataframe(session_df, use_container_width=True)

fig_session = px.bar(
    session_df,
    x="user_id",
    y="session_events",
    color="session_type",
    title="Session Events by User"
)

st.plotly_chart(fig_session, use_container_width=True)



st.markdown("---")

st.subheader("🚨 Anomaly Alerts Panel")

if fraud_users:
    fraud_df = pd.DataFrame(fraud_users)

    suspicious_df = fraud_df[fraud_df["status"] == "suspicious"]

    total_suspicious = len(suspicious_df)
    max_fraud_score = fraud_df["fraud_score"].max()
    most_risky_user = fraud_df.sort_values("fraud_score", ascending=False).iloc[0]["user_id"]

    a1, a2, a3 = st.columns(3)

    a1.metric("Suspicious Users", total_suspicious)
    a2.metric("Max Fraud Score", round(max_fraud_score, 2))
    a3.metric("Most Risky User", most_risky_user)

    if total_suspicious > 0:
        st.error("High-risk user behavior detected.")
        st.dataframe(suspicious_df, use_container_width=True)
    else:
        st.success("No high-risk users detected.")


st.markdown("---")

st.subheader("📈 User Behavior Timeline")

if not filtered_df.empty and "timestamp" in filtered_df.columns:
    timeline_df = filtered_df.dropna(subset=["timestamp"]).sort_values("timestamp")

    if not timeline_df.empty:
        fig_timeline = px.scatter(
            timeline_df,
            x="timestamp",
            y="user_id",
            color="event_type",
            symbol="event_type",
            size="product_id",
            title="User Events Over Time",
            hover_data=["page", "category", "product_id"]
        )

        st.plotly_chart(fig_timeline, use_container_width=True)
    else:
        st.info("No valid timestamp data available for timeline.")


st.markdown("---")
st.subheader("🔥 Trending Analytics")

t1, t2 = st.columns(2)

with t1:
    st.write("Trending Pages")
    trending_pages = filtered_df["page"].value_counts().reset_index()
    trending_pages.columns = ["page", "count"]
    st.dataframe(trending_pages.head(10), use_container_width=True)

with t2:
    st.write("Trending Categories")
    trending_categories = filtered_df["category"].value_counts().reset_index()
    trending_categories.columns = ["category", "count"]
    st.dataframe(trending_categories.head(10), use_container_width=True)



# Latest events
st.subheader("Latest Events")

st.dataframe(filtered_df.head(50), use_container_width=True)

# CSV export
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download Filtered Events as CSV",
    data=csv,
    file_name="filtered_events.csv",
    mime="text/csv"
)
excel_buffer = BytesIO()

with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
    filtered_df.to_excel(writer, index=False, sheet_name="Events")

excel_buffer.seek(0)

st.download_button(
    label="Download Filtered Events as Excel",
    data=excel_buffer,
    file_name="filtered_events.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)