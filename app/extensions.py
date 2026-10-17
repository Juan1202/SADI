import os
import boto3
from botocore.exceptions import ClientError

S3_ENDPOINT = os.environ.get('S3_ENDPOINT', 'http://minio:9000')
S3_ACCESS_KEY = os.environ.get('S3_ACCESS_KEY', 'minioadmin')
S3_SECRET_KEY = os.environ.get('S3_SECRET_KEY', 'minioadmin')
S3_BUCKET = os.environ.get('S3_BUCKET', 'sadi-evidencias')
S3_BUCKET_DOCS = os.environ.get('S3_BUCKET_DOCS', 'sadi-documentacion')

s3_client = boto3.client(
    's3',
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    config=boto3.session.Config(
        signature_version='s3v4',
        connect_timeout=3,
        read_timeout=3,
        retries={'max_attempts': 1}
    )
)


def init_s3_bucket():
    buckets = [S3_BUCKET, S3_BUCKET_DOCS]
    for bucket in buckets:
        try:
            s3_client.head_bucket(Bucket=bucket)
            print(f"Bucket '{bucket}' encontrado.")
        except Exception:
            try:
                s3_client.create_bucket(Bucket=bucket)
                print(f"Bucket '{bucket}' creado exitosamente.")
            except Exception as e:
                print(f"Error creando bucket '{bucket}': {e}")
