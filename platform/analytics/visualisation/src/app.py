import streamlit as st
import time
import os
import io
import json
import pandas as pd
import boto3
import plotly.express as px

S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://seaweedfs:8333")
BUCKET = os.getenv("BUCKET", "mybucket")
OPERATIONAL_PREFIX = "colour-operational/"
PERFORMANCE_KEY = "colour-performance/colour-performance.parquet"

COLOUR_MAP = {"green": "green", "amber": "orange", "red": "red"}


def _s3():
    return boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "demokey"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "demosecret"),
        region_name=os.getenv("AWS_REGION", "us-east-1"),
    )


def load_operational():
    """The colour-operational data product: the flat per-event JSONL stream."""
    s3 = _s3()
    objects = s3.list_objects_v2(Bucket=BUCKET, Prefix=OPERATIONAL_PREFIX).get("Contents", [])
    rows = []
    for obj in objects:
        if not obj["Key"].endswith(".jsonl"):
            continue
        body = s3.get_object(Bucket=BUCKET, Key=obj["Key"])["Body"].read().decode()
        for line in body.splitlines():
            if line.strip():
                rows.append(json.loads(line))
    return pd.DataFrame(rows)


def load_performance():
    """The colour-performance data product: the curated daily Parquet aggregate."""
    s3 = _s3()
    try:
        body = s3.get_object(Bucket=BUCKET, Key=PERFORMANCE_KEY)["Body"].read()
    except s3.exceptions.NoSuchKey:
        return pd.DataFrame()
    return pd.read_parquet(io.BytesIO(body))


def render_operational():
    st.subheader("Operational Awareness")
    st.caption("React to what's happening now — every colour generation, in granular detail.")
    df = load_operational()
    if df.empty:
        st.warning("No events yet. Generate a colour to see activity.")
        return
    st.metric(label="Total events (all time)", value=len(df))
    st.markdown("**Latest activity**")
    st.dataframe(df.sort_values(by="timestamp", ascending=False).head(10), use_container_width=True)
    counts = df["colour"].value_counts().reset_index()
    counts.columns = ["colour", "count"]
    fig = px.bar(
        counts, x="colour", y="count", color="colour",
        color_discrete_map=COLOUR_MAP, text="count",
    )
    fig.update_traces(marker_line_color="black", marker_line_width=1)
    fig.update_layout(showlegend=False, xaxis_title="Colour", yaxis_title="Count")
    st.plotly_chart(fig, use_container_width=True)


def render_performance():
    st.subheader("Performance & Status")
    st.caption("How colours trend over time, and where things stand right now.")
    df = load_performance()
    if df.empty:
        st.warning("No aggregate yet. The summariser writes colour-performance on its next run.")
        return

    # Current status: the latest day's counts per colour.
    latest_date = df["date"].max()
    st.markdown(f"**Current status — {latest_date}**")
    today = df[df["date"] == latest_date]
    cols = st.columns(len(COLOUR_MAP))
    for col, colour in zip(cols, COLOUR_MAP):
        value = int(today.loc[today["colour"] == colour, "count"].sum())
        col.metric(label=colour.capitalize(), value=value)

    # Performance over time: daily counts per colour.
    st.markdown("**Daily trend**")
    fig = px.bar(
        df.sort_values("date"), x="date", y="count", color="colour",
        color_discrete_map=COLOUR_MAP, barmode="group", text="count",
    )
    fig.update_layout(xaxis_title="Day", yaxis_title="Count", legend_title="Colour")
    st.plotly_chart(fig, use_container_width=True)


def main():
    st.title("Colour Data Products")
    st.session_state["last_refresh"] = time.time()
    if st.button("🔄 Refresh"):
        st.rerun()
    st.caption("Last refreshed: {}".format(time.ctime(st.session_state["last_refresh"])))

    operational_tab, performance_tab = st.tabs(["Operational Awareness", "Performance"])
    with operational_tab:
        render_operational()
    with performance_tab:
        render_performance()


if __name__ == "__main__":
    main()
