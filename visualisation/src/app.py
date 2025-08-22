import streamlit as st
import time
import pandas as pd
import boto3
import json
import plotly.express as px

S3_ENDPOINT = "http://minio:9000"
BUCKET = "mybucket"
PREFIX = "events-json-stream/"

## @st.cache_data(show_spinner=False)
def load_events():
    s3 = boto3.client(
        's3',
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id='minioadmin',
        aws_secret_access_key='minioadmin',
        region_name='us-east-1'
    )
    objects = s3.list_objects_v2(Bucket=BUCKET, Prefix=PREFIX).get('Contents', [])
    all_events = []
    for obj in objects:
        key = obj['Key']
        if key.endswith('.jsonl'):
            body = s3.get_object(Bucket=BUCKET, Key=key)['Body'].read().decode()
            for line in body.splitlines():
                if line.strip():
                    all_events.append(json.loads(line))
    if all_events:
        df = pd.DataFrame(all_events)
        # If 'data' column exists and is a dict, extract 'colour' from it
        if 'data' in df.columns:
            df['colour'] = df['data'].apply(lambda x: x.get('colour') if isinstance(x, dict) and 'colour' in x else None)
        return df
    else:
        return pd.DataFrame()

def main():

    st.title("MinIO Event Visualisation")
    st.session_state['last_refresh'] = time.time()
    # Add a manual refresh button
    if st.button("🔄 Refresh Data"):
        st.rerun()

    # Auto-refresh every 5 seconds
    df = load_events()
    if df.empty:
        st.warning("No events found.")
    else:
        st.text("Last Refreshed: {}".format(time.ctime(st.session_state['last_refresh'])))
        st.metric(label="Total Events", value=len(df))
        # Show top 10 latest events
        df_sorted = df.sort_values(by='time', ascending=False).head(10)
        st.dataframe(df_sorted)
        st.markdown("---")
        # Visualisation: Aggregate count by 'colour' if present
        if 'colour' in df.columns:
            st.subheader("Event Count by Colour")
            colour_counts = df['colour'].value_counts().reset_index()
            colour_counts.columns = ['colour', 'count']
            # Define color mapping
            color_map = {'green': 'green', 'amber': 'orange', 'red': 'red'}
            colour_counts['bar_color'] = colour_counts['colour'].map(color_map).fillna('gray')
            fig = px.bar(
                colour_counts,
                x='colour',
                y='count',
                color='colour',
                color_discrete_map=color_map,
                text='count',
            )
            fig.update_traces(marker_line_color='black', marker_line_width=1)
            fig.update_layout(showlegend=False, xaxis_title='Colour', yaxis_title='Count')
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
