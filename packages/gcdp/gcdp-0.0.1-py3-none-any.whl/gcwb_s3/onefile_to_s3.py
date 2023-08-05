import boto3
import os
from datetime import date
from src.commonlibs.utils import json_contents, project_path


def upload_file_to_s3(source_file_path, target_file_path):
    AWS_ACCESS_KEY_ID = json_contents['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = json_contents['AWS_SECRET_ACCESS_KEY']
    AWS_DEFAULT_REGION = json_contents['AWS_DEFAULT_REGION']
    AWS_BUCKET_NAME = json_contents['AWS_BUCKET_NAME']


    client = boto3.client('s3',
                          aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                          region_name=AWS_DEFAULT_REGION)

    # Upload a file
    upload_file_bucket = AWS_BUCKET_NAME
    upload_file_key = target_file_path
    # upload_file_key = f'{date.today().strftime("%y%m%d")}/{system_name}/{file}'
    #Filename: source path, Bucket: 업로드 하려고 하는 AWS S3의 버킷 이름, Key: 업로드 하려고 하는 AWS의 target path
    client.upload_file(Filename=source_file_path, Bucket =upload_file_bucket, Key=upload_file_key)

if __name__ == "__main__":
    source_file_path = os.path.join(os.path.join(project_path, "sql_"), "copyinto_pnt.sql_")
    target_file_path = f"{date.today().strftime('%y%m%d')}/sql_/copyinto_pnt.sql_"
    print(f"{source_file_path} -> s3://gccorps3/{target_file_path}")
    upload_file_to_s3(source_file_path, target_file_path)

    source_file_path = os.path.join(os.path.join(project_path, "sql_"), "truncate_pnt.sql_")
    target_file_path = f"{date.today().strftime('%y%m%d')}/sql_/truncate_pnt.sql_"
    print(f"{source_file_path} -> s3://gccorps3/{target_file_path}")
    upload_file_to_s3(source_file_path, target_file_path)
