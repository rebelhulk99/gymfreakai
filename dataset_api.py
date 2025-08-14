from usda_fdc import FdcClient
import boto3
from botocore.client import Config
import json
import time
import os
import kagglehub



# USDA API key
usda_api_key = #"api key"

# AWS S3 credentials and config
aws_access_key_id = #'key'
aws_secret_access_key = #'key'
region_name = #'your-region-name'
bucket_name = #'your-bucket-name'

# Initialize clients
client = FdcClient(usda_api_key)
s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name,
    config=Config(signature_version='s3v4')
)

page = 1
page_size = 100

while True:
    try:
        results = client.search("", page_number=page, page_size=page_size)
        foods = results.foods
        if not foods:
            print("No more data. Exiting.")
            break

        all_results = [
            {"fdc_id": food.fdc_id, "description": food.description, "data_type": food.data_type}
            for food in foods
        ]

        file_name = f'usda_page_{page}.json'
        with open(file_name, 'w') as f:
            json.dump(all_results, f)

        s3.upload_file(file_name, bucket_name, file_name)
        print(f"Uploaded page {page} with {len(foods)} items")

        os.remove(file_name)  # Clean up local file

        page += 1
        time.sleep(1)  # To respect API rate limits
    except Exception as e:
        print(f"Error on page {page}: {e}")
        break
