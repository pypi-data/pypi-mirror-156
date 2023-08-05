#!/usr/bin/python

import os
import sys
import boto3
from datetime import date
# get an access token, local (from) directory, and s3 (to) directory
# from the command-line
local_directory = os.path.join(os.path.join(sys.path[1], "downloads"), date.today().strftime('%y%m%d'))
bucket = "gccorps3"
destination = date.today().strftime('%y%m%d')

client = boto3.client('s3')

# enumerate local files recursively
for root, dirs, files in os.walk(local_directory):

  for filename in files:

    # construct the full local path
    local_path = os.path.join(root, filename)

    # construct the full Dropbox path
    relative_path = os.path.relpath(local_path, local_directory)
    s3_path = os.path.join(destination, relative_path)

    # relative_path = os.path.relpath(os.path.join(root, filename))

    print('Searching "%s" in "%s"' % (s3_path, bucket))
    try:
        # client.head_object(Bucket=bucket, Key=s3_path)
        print("Path found on s3! Skipping %sgcdp." % s3_path)

        # try:
            # client.delete_object(Bucket=bucket, Key=s3_path)
        # except:
            # print "Unable to delete %s..." % s3_path
    except:
        print("Uploading %s..." % s3_path)
        # client.upload_file(local_path, bucket, s3_path)