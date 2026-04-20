import pandas as pd


def recommend_category(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["user_id", "recommended_category"])

    category_df = df.dropna(subset=["category"])

    if category_df.empty:
        return pd.DataFrame(columns=["user_id", "recommended_category"])

    recommendations = (
        category_df.groupby(["user_id", "category"])
        .size()
        .reset_index(name="count")
        .sort_values(["user_id", "count"], ascending=[True, False])
        .drop_duplicates(subset=["user_id"])
        [["user_id", "category"]]
        .rename(columns={"category": "recommended_category"})
    )

    return recommendations