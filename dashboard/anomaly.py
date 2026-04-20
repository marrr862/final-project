import pandas as pd

def analyze_users(df: pd.DataFrame) -> pd.DataFrame:
    user_activity = df["user_id"].value_counts().reset_index()
    user_activity.columns = ["user_id", "event_count"]

    user_activity["fraud_score"] = user_activity["event_count"] / user_activity["event_count"].max()

    def segment(x):
        if x <= 2:
            return "low"
        elif x <= 4:
            return "medium"
        else:
            return "high"

    user_activity["segment"] = user_activity["event_count"].apply(segment)

    user_activity["status"] = user_activity["event_count"].apply(
        lambda x: "suspicious" if x > 4 else "normal"
    )

    return user_activity