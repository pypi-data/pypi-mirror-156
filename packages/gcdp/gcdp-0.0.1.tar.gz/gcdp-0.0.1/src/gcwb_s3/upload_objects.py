import boto3
import os
from datetime import date
from commonlibs.utils import json_contents, project_path, get_downloads_folder

def upload_files_to_s3(upload_date, system_name, file):
    AWS_ACCESS_KEY_ID = json_contents['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = json_contents['AWS_SECRET_ACCESS_KEY']
    AWS_DEFAULT_REGION = json_contents['AWS_DEFAULT_REGION']
    AWS_BUCKET_NAME = json_contents['AWS_BUCKET_NAME']

    client = boto3.client('s3',
                          aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                          region_name=AWS_DEFAULT_REGION)

    # Upload the files
    folder_path = os.path.join(os.path.join(os.path.join(project_path, "downloads"), system_name), upload_date)
    # for file in os.listdir(folder_path):
    print(f"upload file to s3: {file}")
    upload_file_bucket = AWS_BUCKET_NAME
    upload_file_key = f'{system_name}/{upload_date}/{file}'
    # upload_file_key = f'{date.today().strftime("%y%m%d")}/{system_name}/{file}'
    # Filename: source path,
    # Bucket: 업로드 하려고 하는 AWS S3의 버킷 이름
    # Key: 업로드 하려고 하는 AWS의 target path

    client.upload_file(Filename=os.path.join(folder_path, f"{file}"), Bucket =upload_file_bucket, Key=upload_file_key)

if __name__ == "__main__":
    global upload_date
    upload_date = date.today().strftime('%y%m%d')
    for file in os.listdir(get_downloads_folder("ga")):
        print(file)
        upload_files_to_s3(upload_date=upload_date, system_name="ga", file=file)

