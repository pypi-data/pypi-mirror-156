from cloudpathlib import S3Client
from commonlibs.utils import json_contents, set_downloads_folder, get_downloads_folder
import boto3



def all_backup():
    s3 = boto3.resource('s3',
                         aws_access_key_id = json_contents['AWS_ACCESS_KEY_ID'],
                         aws_secret_access_key = json_contents['AWS_SECRET_ACCESS_KEY'])
    # for bucket in s3.buckets.all():
    #     print(bucket.name)
    #     client = S3Client(aws_access_key_id = json_contents['AWS_ACCESS_KEY_ID'], aws_secret_access_key = json_contents['AWS_SECRET_ACCESS_KEY'])
    #     s3_path = f"s3://{bucket.name}"
    #     set_downloads_folder("backup")
    #     download_path = get_downloads_folder("backup")
    #     cp = client.CloudPath(f"{s3_path}")
    #     cp.download_to(f"{download_path}")

    client = S3Client(aws_access_key_id = json_contents['AWS_ACCESS_KEY_ID'], aws_secret_access_key = json_contents['AWS_SECRET_ACCESS_KEY'])
    s3_path = f"s3://gcwb-sf/220530"
    set_downloads_folder("backup")
    download_path = get_downloads_folder("backup")
    cp = client.CloudPath(f"{s3_path}")
    cp.download_to(f"{download_path}")

if __name__ == "__main__":
    all_backup()