#!/usr/bin/env python
# coding: utf-8

# # ga : Dr.PNT몰 데이터 (GA_DPN)
# https://community.snowflake.com/s/article/maxi-expressions-exceeded
# > # 환경세팅

# In[1]:
# https://stackoverflow.com/questions/1060279/iterating-through-a-range-of-dates-in-python

import pandas as pd
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import boto3
import os
import inspect
from datetime import date, timedelta
import datetime
import json
import snowflake.connector

# In[2]:

project_path = os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__), os.pardir), os.pardir))

with open(f"{project_path}/secret.json", "r") as fp:
    json_contents=json.loads(fp.read())



def execute_insert_query(system_name, table_name, data_date):
    """
    generate insert query
    table에 데이터를 넣는 방법이 copy into stmt와 insert into select stmt이다.
    show columns in table {table_name}; 쿼리를 통해 컬럼들을 추출하고
    컬럼수만큼 string_source concatnate
    컬럼스트링도 for문 돌면서 concatnate
    string_source = f"T.${i},"
    column_str = column_str + ", " + row[2]
    table_str = table_str + string_source
    :param system_name, table_name:
    :return:
    """
    conn = snowflake.connector.connect(
        user=json_contents['sf_user'],
        password=json_contents['sf_pwd'],
        account=json_contents['sf_host'],
        warehouse=json_contents['sf_wh'],
        database=json_contents['sf_db'],
        schema=json_contents['sf_schema'],
        cache_column_metadata=True
    )

    df = pd.read_sql_query(
        sql=f"show columns in table {json_contents['sf_db']}.{json_contents['sf_schema']}.O_{system_name}_{table_name};",
        con=conn)
    df = df.iloc[:-1, :]
    # 마지막 load_dttm은 제외한다
    column_string = ", ".join(df['column_name'].tolist())
    print(f"column_string: {column_string}")
    column_string = column_string+", LOAD_DTTM"
    print(f"column_string: {column_string}")

    select_string = ", ".join(
        [f"T.${i + 1}" if json.loads(df["data_type"][i])['type'] != "VARIANT" else "parse_json(" + f"T.${i + 1}" + ")"
         for _, i in enumerate(df.index.values.tolist())])
    print(f"select_string: {select_string}")
    select_string = select_string+", CURRENT_TIMESTAMP()::timestamp_ntz"
    print(f"select_string: {select_string}")
    # snowflake(target)에서 table이 마지막 컬럼 load_dttm인 것을 제외하고 난 나머지의 컬럼갯수 만큼 csv파일에서 select하여 target과 source의 column갯수를 맞춰 insert한다.
    element_type = [json.loads(df["data_type"][i])['type'] for _, i in enumerate(df.index.values.tolist())]
    stmt = f"INSERT INTO {json_contents['sf_db']}.{json_contents['sf_schema']}.O_{system_name}_{table_name} ({column_string}) SELECT {select_string} from @GCWB/{system_name}/{data_date}/{table_name}.csv (FILE_FORMAT=>'O_{system_name}_{table_name}') as T;"
    print(f"stmt : {stmt}")
    cur = conn.cursor()
    cur.execute(stmt)

def execute_delete_query(system_name, table_name):
    conn = snowflake.connector.connect(
        user=json_contents['sf_user'],
        password=json_contents['sf_pwd'],
        account=json_contents['sf_host'],
        warehouse=json_contents['sf_wh'],
        database=json_contents['sf_db'],
        schema=json_contents['sf_schema'],
        cache_column_metadata=True
    )
    df = pd.read_csv(os.path.join(get_downloads_folder("ga"), f"{table_name}.csv"), encoding='utf-8')
    stmt = f"DELETE FROM GCWB_WDB.ODS.O_{system_name}_{table_name} WHERE DATE BETWEEN {df['DATE'].min()} AND {df['DATE'].max()};"
    print(f"stmt : {stmt}")
    cur = conn.cursor()
    cur.execute(stmt)

def execute_rownum_query(system_name, table_name):
    conn = snowflake.connector.connect(
        user=json_contents['sf_user'],
        password=json_contents['sf_pwd'],
        account=json_contents['sf_host'],
        warehouse=json_contents['sf_wh'],
        database=json_contents['sf_db'],
        schema=json_contents['sf_schema'],
        cache_column_metadata=True
    )
    df = pd.read_csv(os.path.join(get_downloads_folder("ga"), f"{table_name}.csv"), encoding='utf-8')
    rownum_stmt = f"SELECT COUNT(*) FROM GCWB_WDB.ODS.O_{system_name}_{table_name};"
    print(f"rownum : {rownum_stmt}")
    cur = conn.cursor()
    rownum = cur.execute(rownum_stmt).fetchone()
    print(rownum)
    return rownum

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

def set_downloads_folder(system_name):
    """
    set downloads folder
    system_name = "pnt"||"dpn"||"ga"
    :param system_name:
    :return:
    """
    # project폴더의 하위downloads폴더
    downloads_folder = os.path.join(project_path, "downloads")
    system_folder = os.path.join(downloads_folder, system_name)
    today_folder = os.path.join(system_folder, date.today().strftime('%y%m%d'))
    download_folder_fullpath = today_folder
    if not os.path.exists(downloads_folder):
        os.makedirs(downloads_folder)
    if not os.path.exists(system_folder):
        os.makedirs(system_folder)
    if not os.path.exists(today_folder):
        os.makedirs(today_folder)

    print(f"{download_folder_fullpath} download folder fullpath: {download_folder_fullpath}")
    return download_folder_fullpath

def get_downloads_folder(system_name):
    download_folder_fullpath = os.path.join(os.path.join(os.path.join(project_path, "downloads"), system_name), date.today().strftime('%y%m%d'))
    # print(f"{system_name} download folder fullpath: {system_folder}")
    return download_folder_fullpath

def get_service(api_name, api_version, scopes, key_file_location):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
            key_file_location, scopes=scopes)

    # Build the service object.
    service = build(api_name, api_version, credentials=credentials)

    return service

# Define the auth scopes to request.
scope = 'https://www.googleapis.com/auth/analytics.readonly'
key_file_location = f'{os.path.join(project_path,"prj-ga-api-088316594eb2.json")}' ## Key 파일위치 입력

# Authenticate and construct service.
service = get_service(
        api_name='analytics',
        api_version='v3',
        scopes=[scope],
        key_file_location=key_file_location)

# Get a list of all Google Analytics accounts for this user
accounts = service.management().accounts().list().execute()

if accounts.get('items'):
    # Get the first Google Analytics account.
    account = accounts.get('items')[0].get('id')

    # Get a list of all the properties for the first account.
    properties = service.management().webproperties().list(accountId=account).execute()


# In[3]:

def API_Result_DF(DICT_INPUT):
    result = service.data().ga().get(**DICT_INPUT).execute()

    if result['totalResults'] == 0:  ##데이터 없을 경우
        Page_total = 1  # 전체 페이지번호
        Page_now = 1  # 현재 페이지번호
        DF_result = pd.DataFrame(columns=[col['name'].replace('ga:', '') for col in result['columnHeaders']])
    else:
        Page_total = (result['totalResults'] - 1) // 10000 + 1  # 전체 페이지번호
        Page_now = 1  # 현재 페이지번호
        DF_result = pd.DataFrame(result['rows'],
                                 columns=[col['name'].replace('ga:', '') for col in result['columnHeaders']])

    while Page_now != Page_total:
        Page_now += 1
        DICT_INPUT['start_index'] = (Page_now - 1) * 10000 + 1

        result_tmp = service.data().ga().get(**DICT_INPUT).execute()

        DF_result_tmp = pd.DataFrame(result_tmp['rows'],
                                     columns=[col['name'].replace('ga:', '') for col in result_tmp['columnHeaders']])

        DF_result = pd.concat([DF_result, DF_result_tmp], axis=0)

    DF_result = DF_result.reset_index(drop=True)

    return DF_result