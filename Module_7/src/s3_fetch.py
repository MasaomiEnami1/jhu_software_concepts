"""
Module to securely fetch data from AWS S3.
"""
import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

def download_s3_file(bucket_name, s3_file_key, local_filename):
    """
    Downloads a file from S3 using credentials from a .env file.
    """
    load_dotenv()  # Securely loads your keys into the environment

    # Initialize session without hardcoding keys in the script
    session = boto3.Session(
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION')
    )
    s3_client = session.client('s3')

    try:
        print(f"Downloading {s3_file_key} from {bucket_name}...")
        s3_client.download_file(bucket_name, s3_file_key, local_filename)
        print(f"Successfully saved as {local_filename}")
        return True
    except ClientError as err:
        print(f"Error: {err}")
        return False
    