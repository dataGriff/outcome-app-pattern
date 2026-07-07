import boto3
import json
import pandas as pd

# MinIO/S3 config
S3_ENDPOINT = "http://localhost:9000"
BUCKET = "mybucket"
PREFIX = "events-json-stream/"

s3 = boto3.client(
    's3',
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id='minioadmin',
    aws_secret_access_key='minioadmin',
    region_name='us-east-1'
)

# List all JSONL files in the prefix
objects = s3.list_objects_v2(Bucket=BUCKET, Prefix=PREFIX).get('Contents', [])
all_events = []

for obj in objects:
    key = obj['Key']
    if key.endswith('.jsonl'):
        body = s3.get_object(Bucket=BUCKET, Key=key)['Body'].read().decode()
        for line in body.splitlines():
            if line.strip():
                all_events.append(json.loads(line))

# Load into DataFrame
if all_events:
    df = pd.DataFrame(all_events)
    print(df.head())
    # Example query: filter by a column, e.g., 'colour'
    # print(df[df['colour'] == 'red'])
else:
    print("No events found.")
