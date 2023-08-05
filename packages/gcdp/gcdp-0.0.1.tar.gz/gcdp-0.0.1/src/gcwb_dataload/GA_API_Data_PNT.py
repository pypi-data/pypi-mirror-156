#!/usr/bin/env python
# coding: utf-8

# # ga : PNT샵 데이터 (GA_PNT)

# > # 환경세팅

# In[2]:


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

project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

with open(f"{project_path}/secret.json", "r") as fp:
    json_contents=json.loads(fp.read())

def execute_truncate_query(system_name, table_name):
    conn = snowflake.connector.connect(
        user=json_contents['sf_user'],
        password=json_contents['sf_pwd'],
        account=json_contents['sf_host'],
        warehouse=json_contents['sf_wh'],
        database=json_contents['sf_db'],
        schema=json_contents['sf_schema'],
        cache_column_metadata=True
    )

    cur = conn.cursor()

    query = f"truncate table {json_contents['sf_db']}.{json_contents['sf_schema']}.O_{system_name}_{table_name};"
    print(f"Execute query of snowflake: {query}")
    rs = cur.execute(query)
    return rs

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
    system_name = "pnt"||"dpn"
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


# In[4]:


def API_Result_DF(DICT_INPUT):
    result = service.data().ga().get(**DICT_INPUT).execute()

    if result['totalResults']==0 : ##데이터 없을 경우
        Page_total = 1 # 전체 페이지번호
        Page_now = 1 # 현재 페이지번호
        DF_result = pd.DataFrame(columns=[col['name'].replace('ga:','') for col in result['columnHeaders']])
    else :
        Page_total = (result['totalResults']-1)//10000+1 # 전체 페이지번호
        Page_now = 1 # 현재 페이지번호
        DF_result = pd.DataFrame(result['rows'], columns=[col['name'].replace('ga:','') for col in result['columnHeaders']])

    while Page_now != Page_total :
        Page_now += 1
        DICT_INPUT['start_index'] = (Page_now-1)*10000+1

        result_tmp = service.data().ga().get(**DICT_INPUT).execute()

        DF_result_tmp = pd.DataFrame(result_tmp['rows'],
                                     columns=[col['name'].replace('ga:','') for col in result_tmp['columnHeaders']])

        DF_result = pd.concat([DF_result, DF_result_tmp], axis=0)

    DF_result = DF_result.reset_index(drop=True)

    return DF_result

# > ## CLIENT
# ### 1. GA_PNT_CLIENT

def get_GA_PNT_CLIENT(START_DATE, END_DATE):
    print(inspect.currentframe().f_code.co_name, START_DATE, END_DATE)
    ## date hour and minute 수정

    list_user = ['New Visitor', 'Returning Visitor']
    list_device = ['desktop', 'mobile', 'tablet']

    GA_PNT_CLIENT = pd.DataFrame()

    for USER in list_user:
        for DEVICE in list_device:
            Dict_input = {'ids': 'ga:253231372',  # PNT샵
                          'start_date': START_DATE,
                          'end_date': END_DATE,
                          'dimensions': 'ga:dateHourMinute,ga:clientId,ga:channelGrouping,ga:source,ga:landingPagePath,ga:exitPagePath,ga:city',
                          'metrics': 'ga:sessions,ga:bounces,ga:pageviews,ga:sessionDuration,ga:transactions,ga:transactionRevenue,ga:goal1Completions,ga:goal6Completions',
                          'sort': None,
                          'filters': 'ga:userType==' + USER + ';ga:deviceCategory==' + DEVICE,
                          'start_index': 1,
                          'max_results': 10000}

            DF_tmp = API_Result_DF(Dict_input)
            DF_tmp['userType'] = USER
            DF_tmp['deviceCategory'] = DEVICE

            GA_PNT_CLIENT = pd.concat([GA_PNT_CLIENT, DF_tmp], axis=0)

    GA_PNT_CLIENT = GA_PNT_CLIENT.reset_index(drop=True)
    GA_PNT_CLIENT = pd.concat([GA_PNT_CLIENT.iloc[:, :7], GA_PNT_CLIENT.iloc[:, 15:], GA_PNT_CLIENT.iloc[:, 7:15]],
                              axis=1)
    GA_PNT_CLIENT = GA_PNT_CLIENT.astype({'sessions': int, 'bounces': int, 'pageviews': int, 'sessionDuration': float,
                                          'transactions': int, 'transactionRevenue': float, 'goal1Completions': int,
                                          'goal6Completions': int})
    GA_PNT_CLIENT.columns = [col.upper() for col in GA_PNT_CLIENT.columns.values]

    GA_PNT_CLIENT['DATE'] = GA_PNT_CLIENT['DATEHOURMINUTE'].apply(lambda x: x[:8])
    GA_PNT_CLIENT['HOURMINUTE'] = GA_PNT_CLIENT['DATEHOURMINUTE'].apply(lambda x: x[8:])
    GA_PNT_CLIENT = pd.concat([GA_PNT_CLIENT.iloc[:, 17:], GA_PNT_CLIENT.iloc[:, 1:17]], axis=1)
    return GA_PNT_CLIENT



        # ### 2. GA_PNT_CLIENT_CITY
def get_GA_PNT_CLIENT_CITY(START_DATE, END_DATE):
    print(inspect.currentframe().f_code.co_name, START_DATE, END_DATE)
    ## date hour and minute 수정

    Dict_input = {'ids': 'ga:253231372',  # PNT샵
                  'start_date': START_DATE,
                  'end_date': END_DATE,
                  'dimensions': 'ga:dateHourMinute,ga:clientId,ga:city,ga:country,ga:region',
                  'metrics': 'ga:sessions',
                  'sort': None,
                  'filters': None,
                  'start_index': 1,
                  'max_results': 10000}

    GA_PNT_CLIENT_CITY = API_Result_DF(Dict_input)
    GA_PNT_CLIENT_CITY = GA_PNT_CLIENT_CITY.astype({'sessions': int})
    GA_PNT_CLIENT_CITY.columns = [col.upper() for col in GA_PNT_CLIENT_CITY.columns.values]

    GA_PNT_CLIENT_CITY['DATE'] = GA_PNT_CLIENT_CITY['DATEHOURMINUTE'].apply(lambda x: x[:8])
    GA_PNT_CLIENT_CITY['HOURMINUTE'] = GA_PNT_CLIENT_CITY['DATEHOURMINUTE'].apply(lambda x: x[8:])
    GA_PNT_CLIENT_CITY = pd.concat([GA_PNT_CLIENT_CITY.iloc[:, 6:], GA_PNT_CLIENT_CITY.iloc[:, 1:6]], axis=1)
    return GA_PNT_CLIENT_CITY

        # ### 3. GA_PNT_GENDER
def get_GA_PNT_GENDER(START_DATE, END_DATE):
    print(inspect.currentframe().f_code.co_name, START_DATE, END_DATE)
    Dict_input = {'ids':'ga:253231372', #PNT샵
                  'start_date':START_DATE,
                  'end_date':END_DATE,
                  'dimensions':'ga:date,ga:userGender',
                  'metrics':'ga:users,ga:newUsers,ga:sessions,ga:bounces,ga:pageviews,ga:sessionDuration,ga:transactions,ga:transactionRevenue,ga:goal1Completions,ga:goal6Completions',
                  'sort':None,
                  'filters':None,
                  'start_index':1}

    GA_PNT_GENDER = API_Result_DF(Dict_input)
    GA_PNT_GENDER = GA_PNT_GENDER.astype({'users':int,'newUsers':int,'sessions':int,
                                          'bounces':int,'pageviews':int,'sessionDuration':float,
                                          'transactions':int,'transactionRevenue':float,
                                          'goal1Completions':int,'goal1Completions':int})
    GA_PNT_GENDER.columns = [col.upper() for col in GA_PNT_GENDER.columns.values]
    return GA_PNT_GENDER

        # ### 4. GA_PNT_AGE
def get_GA_PNT_AGE(START_DATE, END_DATE):
    print(inspect.currentframe().f_code.co_name, START_DATE, END_DATE)
    Dict_input = {'ids':'ga:253231372', #PNT샵
                  'start_date':START_DATE,
                  'end_date':END_DATE,
                  'dimensions':'ga:date,ga:userAgeBracket',
                  'metrics':'ga:users,ga:newUsers,ga:sessions,ga:bounces,ga:pageviews,ga:sessionDuration,ga:transactions,ga:transactionRevenue,ga:goal1Completions,ga:goal6Completions',
                  'sort':None,
                  'filters':None,
                  'start_index':1}

    GA_PNT_AGE = API_Result_DF(Dict_input)
    GA_PNT_AGE = GA_PNT_AGE.astype({'users':int,'newUsers':int,'sessions':int,
                                          'bounces':int,'pageviews':int,'sessionDuration':float,
                                          'transactions':int,'transactionRevenue':float,
                                          'goal1Completions':int,'goal1Completions':int})
    GA_PNT_AGE.columns = [col.upper() for col in GA_PNT_AGE.columns.values]
    return GA_PNT_AGE

        # ### 5. GA_PNT_AFFINITY
def get_GA_PNT_AFFINITY(START_DATE, END_DATE):
    print(inspect.currentframe().f_code.co_name, START_DATE, END_DATE)
    Dict_input = {'ids':'ga:253231372', #PNT샵
                  'start_date':START_DATE,
                  'end_date':END_DATE,
                  'dimensions':'ga:date,ga:interestAffinityCategory',
                  'metrics':'ga:users,ga:newUsers,ga:sessions,ga:bounces,ga:pageviews,ga:sessionDuration,ga:transactions,ga:transactionRevenue,ga:goal1Completions,ga:goal6Completions',
                  'sort':None,
                  'filters':None,
                  'start_index':1}

    GA_PNT_AFFINITY = API_Result_DF(Dict_input)
    GA_PNT_AFFINITY = GA_PNT_AFFINITY.astype({'users':int,'newUsers':int,'sessions':int,
                                          'bounces':int,'pageviews':int,'sessionDuration':float,
                                          'transactions':int,'transactionRevenue':float,
                                          'goal1Completions':int,'goal1Completions':int})
    GA_PNT_AFFINITY.columns = [col.upper() for col in GA_PNT_AFFINITY.columns.values]
    return GA_PNT_AFFINITY


        # > ## PAGE
        # ### 6. GA_PNT_PAGE
def get_GA_PNT_PAGE(START_DATE, END_DATE):
    print(inspect.currentframe().f_code.co_name, START_DATE, END_DATE)
    Dict_input = {'ids': 'ga:253231372',  # PNT샵
                  'start_date': START_DATE,
                  'end_date': END_DATE,
                  'dimensions': 'ga:date,ga:clientId,ga:pagePath,ga:pagePathLevel1',
                  'metrics': 'ga:pageviews,ga:uniquePageviews,ga:entrances,ga:bounces,ga:exits,ga:timeOnPage',
                  'sort': None,
                  'filters': None,
                  'start_index': 1}

    GA_PNT_PAGE = API_Result_DF(Dict_input)
    GA_PNT_PAGE = GA_PNT_PAGE.astype(
        {'pageviews': int, 'uniquePageviews': int, 'entrances': int, 'bounces': int, 'exits': int,
         'timeOnPage': float})
    GA_PNT_PAGE.columns = [col.upper() for col in GA_PNT_PAGE.columns.values]

    # page path level2
    Dict_input = {'ids': 'ga:253231372',  # PNT샵
                  'start_date': START_DATE,
                  'end_date': END_DATE,
                  'dimensions': 'ga:pagePath,ga:pagePathLevel2',
                  'metrics': 'ga:pageviews',
                  'start_index': 1}
    GA_PNT_PAGE_lv2 = API_Result_DF(Dict_input)
    GA_PNT_PAGE_lv2.columns = [col.upper() for col in GA_PNT_PAGE_lv2.columns.values]

    # page path level3
    Dict_input = {'ids': 'ga:253231372',  # PNT샵
                  'start_date': START_DATE,
                  'end_date': END_DATE,
                  'dimensions': 'ga:pagePath,ga:pagePathLevel3',
                  'metrics': 'ga:pageviews',
                  'start_index': 1}
    GA_PNT_PAGE_lv3 = API_Result_DF(Dict_input)
    GA_PNT_PAGE_lv3.columns = [col.upper() for col in GA_PNT_PAGE_lv3.columns.values]

    # page path level4
    Dict_input = {'ids': 'ga:253231372',  # PNT샵
                  'start_date': START_DATE,
                  'end_date': END_DATE,
                  'dimensions': 'ga:pagePath,ga:pagePathLevel4',
                  'metrics': 'ga:pageviews',
                  'start_index': 1}
    GA_PNT_PAGE_lv4 = API_Result_DF(Dict_input)
    GA_PNT_PAGE_lv4.columns = [col.upper() for col in GA_PNT_PAGE_lv4.columns.values]

    GA_PNT_PAGE = pd.merge(GA_PNT_PAGE, GA_PNT_PAGE_lv2[['PAGEPATH', 'PAGEPATHLEVEL2']], how='left',
                           left_on='PAGEPATH', right_on='PAGEPATH')
    GA_PNT_PAGE = pd.merge(GA_PNT_PAGE, GA_PNT_PAGE_lv3[['PAGEPATH', 'PAGEPATHLEVEL3']], how='left',
                           left_on='PAGEPATH', right_on='PAGEPATH')
    GA_PNT_PAGE = pd.merge(GA_PNT_PAGE, GA_PNT_PAGE_lv4[['PAGEPATH', 'PAGEPATHLEVEL4']], how='left',
                           left_on='PAGEPATH', right_on='PAGEPATH')
    GA_PNT_PAGE = pd.concat([GA_PNT_PAGE.iloc[:, :4], GA_PNT_PAGE.iloc[:, 10:], GA_PNT_PAGE.iloc[:, 4:10]], axis=1)
    return GA_PNT_PAGE

        # > ## ORDER, PRODUCT
        # ### 7. GA_PNT_ORDER
def get_GA_PNT_ORDER(START_DATE, END_DATE):
    print(inspect.currentframe().f_code.co_name, START_DATE, END_DATE)
    Dict_input = {'ids': 'ga:253231372',  # PNT샵
                  'start_date': START_DATE,
                  'end_date': END_DATE,
                  'dimensions': 'ga:date,ga:clientId,ga:transactionId,ga:channelGrouping,ga:source,ga:medium,ga:city',
                  'metrics': 'ga:transactions,ga:transactionRevenue,ga:transactionTax,ga:transactionShipping,ga:refundAmount,ga:itemQuantity',
                  'sort': None,
                  'filters': None,
                  'start_index': 1}

    GA_PNT_ORDER = API_Result_DF(Dict_input)
    GA_PNT_ORDER = GA_PNT_ORDER.astype({'transactions': int, 'transactionRevenue': float, 'transactionTax': float,
                                        'transactionShipping': float, 'refundAmount': float, 'itemQuantity': int})
    GA_PNT_ORDER.columns = [col.upper() for col in GA_PNT_ORDER.columns.values]
    GA_PNT_ORDER = GA_PNT_ORDER[GA_PNT_ORDER['TRANSACTIONID'] != ''].reset_index(drop=True)
    return GA_PNT_ORDER

        # ### 8. GA_PNT_PRODUCT
def get_GA_PNT_PRODUCT(START_DATE, END_DATE):
    print(inspect.currentframe().f_code.co_name, START_DATE, END_DATE)
    ## 22.06.16 수정 : (API) productCategoryHierarchy 제외

    ## PRODUCT 1
    Dict_input = {'ids': 'ga:253231372',  # PNT샵
                  'start_date': START_DATE,
                  'end_date': END_DATE,
                  'dimensions': 'ga:date,ga:clientId,ga:productSku,ga:productName,ga:productListName,ga:productBrand',
                  'metrics': 'ga:itemRevenue,ga:uniquePurchases,ga:itemQuantity,ga:productRefundAmount,ga:quantityAddedToCart,ga:quantityRemovedFromCart',
                  'sort': None,
                  'filters': None,
                  'start_index': 1,
                  'max_results': 10000}

    GA_PNT_PRODUCT_1 = API_Result_DF(Dict_input)
    GA_PNT_PRODUCT_1 = GA_PNT_PRODUCT_1.astype(
        {'itemRevenue': float, 'uniquePurchases': int, 'itemQuantity': int, 'productRefundAmount': float,
         'quantityAddedToCart': int, 'quantityRemovedFromCart': int})
    # PRODUCTSKU,PRODUCTNAME 오류값 수정
    for i in range(len(GA_PNT_PRODUCT_1)):
        try:
            int(GA_PNT_PRODUCT_1['productSku'][i])
        except:
            PRODUCT_NAME = GA_PNT_PRODUCT_1['productSku'][i]
            GA_PNT_PRODUCT_1['productSku'][i] = GA_PNT_PRODUCT_1['productName'][i]
            GA_PNT_PRODUCT_1['productName'][i] = PRODUCT_NAME

    # 중복데이터 통합
    GA_PNT_PRODUCT_1 = GA_PNT_PRODUCT_1.groupby(['date', 'clientId', 'productSku', 'productName',
                                                 'productListName', 'productBrand'])[
        ['itemRevenue', 'uniquePurchases', 'itemQuantity',
         'productRefundAmount', 'quantityAddedToCart',
         'quantityRemovedFromCart']].sum().reset_index()

    ## PRODUCT 2
    Dict_input = {'ids': 'ga:253231372',  # PNT샵
                  'start_date': START_DATE,
                  'end_date': END_DATE,
                  'dimensions': 'ga:date,ga:clientId,ga:productSku,ga:productName,ga:productListName,ga:productBrand',
                  'metrics': 'ga:productCheckouts,ga:productAddsToCart,ga:productRemovesFromCart,ga:productDetailViews,ga:productListViews,ga:productListClicks',
                  'sort': None,
                  'filters': None,
                  'start_index': 1,
                  'max_results': 10000}

    GA_PNT_PRODUCT_2 = API_Result_DF(Dict_input)
    GA_PNT_PRODUCT_2 = GA_PNT_PRODUCT_2.astype(
        {'productCheckouts': int, 'productAddsToCart': int, 'productRemovesFromCart': int,
         'productDetailViews': int, 'productListViews': int, 'productListClicks': int})

    # PRODUCTSKU,PRODUCTNAME 오류값 수정
    for i in range(len(GA_PNT_PRODUCT_2)):
        try:
            int(GA_PNT_PRODUCT_2['productSku'][i])
        except:
            PRODUCT_NAME = GA_PNT_PRODUCT_2['productSku'][i]
            GA_PNT_PRODUCT_2['productSku'][i] = GA_PNT_PRODUCT_2['productName'][i]
            GA_PNT_PRODUCT_2['productName'][i] = PRODUCT_NAME

    # 중복데이터 통합
    GA_PNT_PRODUCT_2 = GA_PNT_PRODUCT_2.groupby(['date', 'clientId', 'productSku', 'productName',
                                                 'productListName', 'productBrand'])[
        ['productCheckouts', 'productAddsToCart',
         'productRemovesFromCart', 'productDetailViews',
         'productListViews', 'productListClicks']].sum().reset_index()

    GA_PNT_PRODUCT = pd.merge(GA_PNT_PRODUCT_1, GA_PNT_PRODUCT_2, how='inner',
                              on=['date', 'clientId', 'productSku', 'productName', 'productListName', 'productBrand'])
    GA_PNT_PRODUCT.columns = [col.upper() for col in GA_PNT_PRODUCT.columns.values]

    GA_PNT_PRODUCT['PRODUCTCATEGORYHIERARCHY'] = '(not set)'
    GA_PNT_PRODUCT = pd.concat([GA_PNT_PRODUCT.iloc[:, :6], GA_PNT_PRODUCT.iloc[:, -1:], GA_PNT_PRODUCT.iloc[:, 6:-1]],
                               axis=1)
    return GA_PNT_PRODUCT

        # ### 9. GA_PNT_ORDER_PRODUCT
def get_GA_PNT_ORDER_PRODUCT(START_DATE, END_DATE):
    print(inspect.currentframe().f_code.co_name, START_DATE, END_DATE)
    Dict_input = {'ids':'ga:253231372', #PNT샵
                  'start_date':START_DATE,
                  'end_date':END_DATE,
                  'dimensions':'ga:date,ga:transactionId,ga:productSku,ga:productName',
                  'metrics':'ga:itemRevenue,ga:itemQuantity',
                  'sort':None,
                  'filters':None,
                  'start_index':1}

    GA_PNT_ORDER_PRODUCT = API_Result_DF(Dict_input)
    GA_PNT_ORDER_PRODUCT = GA_PNT_ORDER_PRODUCT.astype({'itemRevenue':float,'itemQuantity':int})
    GA_PNT_ORDER_PRODUCT.columns = [col.upper() for col in GA_PNT_ORDER_PRODUCT.columns.values]
    return GA_PNT_ORDER_PRODUCT


        # > ## OTHER

        # ### 10. GA_PNT_SEARCH
def get_GA_PNT_SEARCH(START_DATE, END_DATE):
    print(inspect.currentframe().f_code.co_name, START_DATE, END_DATE)
    Dict_input = {'ids':'ga:253231372', #PNT샵
                  'start_date':START_DATE,
                  'end_date':END_DATE,
                  'dimensions':'ga:date,ga:searchKeyword,ga:searchCategory,ga:searchStartPage',
                  'metrics':'ga:searchSessions,ga:searchUniques,ga:searchResultViews,ga:searchExits,ga:searchRefinements,ga:searchDuration,ga:searchDepth',
                  'sort':None,
                  'filters':None,
                  'start_index':1}

    GA_PNT_SEARCH = API_Result_DF(Dict_input)
    GA_PNT_SEARCH = GA_PNT_SEARCH.astype({'searchSessions':int,'searchUniques':int,'searchResultViews':int,'searchExits':int,
                                            'searchRefinements':int,'searchDuration':float,'searchDepth':int})
    GA_PNT_SEARCH.columns = [col.upper() for col in GA_PNT_SEARCH.columns.values]
    return GA_PNT_SEARCH

        # ### 11. GA_PNT_GOAL (※ ga 목표 변경시 컬럼변경)
def get_GA_PNT_GOAL(START_DATE, END_DATE):
    print(inspect.currentframe().f_code.co_name, START_DATE, END_DATE)
    Dict_input = {'ids': 'ga:253231372',  # PNT샵
                  'start_date': START_DATE,
                  'end_date': END_DATE,
                  'dimensions': 'ga:date,ga:goalCompletionLocation',
                  'metrics': 'ga:goalCompletionsAll,ga:goalValueAll,ga:goal1Completions,ga:goal1Value,ga:goal2Completions,ga:goal2Value,ga:goal3Completions,ga:goal3Value,ga:goal4Completions,ga:goal4Value',
                  'sort': None,
                  'filters': None,
                  'start_index': 1}

    GA_PNT_GOAL_1 = API_Result_DF(Dict_input)
    GA_PNT_GOAL_1 = GA_PNT_GOAL_1.astype({'goalCompletionsAll': int, 'goalValueAll': float,
                                          'goal1Completions': int, 'goal1Value': float,
                                          'goal2Completions': int, 'goal2Value': float,
                                          'goal3Completions': int, 'goal3Value': float,
                                          'goal4Completions': int, 'goal4Value': float})

    Dict_input = {'ids': 'ga:253231372',  # PNT샵
                  'start_date': START_DATE,
                  'end_date': END_DATE,
                  'dimensions': 'ga:date,ga:goalCompletionLocation',
                  'metrics': 'ga:goal5Completions,ga:goal5Value,ga:goal6Completions,ga:goal6Value,ga:goal7Completions,ga:goal7Value,ga:goal8Completions,ga:goal8Value,ga:goal9Completions,ga:goal9Value',
                  'sort': None,
                  'filters': None,
                  'start_index': 1}

    GA_PNT_GOAL_2 = API_Result_DF(Dict_input)
    GA_PNT_GOAL_2 = GA_PNT_GOAL_2.astype({'goal5Completions': int, 'goal5Value': float,
                                          'goal6Completions': int, 'goal6Value': float,
                                          'goal7Completions': int, 'goal7Value': float,
                                          'goal8Completions': int, 'goal8Value': float,
                                          'goal9Completions': int, 'goal9Value': float})

    GA_PNT_GOAL = pd.merge(GA_PNT_GOAL_1, GA_PNT_GOAL_2, how='inner', on=['date', 'goalCompletionLocation'])
    GA_PNT_GOAL.columns = [col.upper() for col in GA_PNT_GOAL.columns.values]
    GA_PNT_GOAL = GA_PNT_GOAL[['DATE', 'GOALCOMPLETIONLOCATION', 'GOALCOMPLETIONSALL', 'GOALVALUEALL',
                               'GOAL1COMPLETIONS', 'GOAL1VALUE', 'GOAL2COMPLETIONS', 'GOAL2VALUE',
                               'GOAL3COMPLETIONS', 'GOAL3VALUE', 'GOAL4COMPLETIONS', 'GOAL4VALUE',
                               'GOAL5COMPLETIONS', 'GOAL5VALUE', 'GOAL6COMPLETIONS', 'GOAL6VALUE',
                               'GOAL7COMPLETIONS', 'GOAL7VALUE', 'GOAL8COMPLETIONS', 'GOAL8VALUE',
                               'GOAL9COMPLETIONS', 'GOAL9VALUE']]
    return GA_PNT_GOAL

        # ### 12. GA_PNT_BEHAVIOR
def get_GA_PNT_BEHAVIOR(START_DATE, END_DATE):
    print(inspect.currentframe().f_code.co_name, START_DATE, END_DATE)
    Dict_input = {'ids': 'ga:253231372',  # PNT샵
                  'start_date': START_DATE,
                  'end_date': END_DATE,
                  'dimensions': 'ga:date,ga:searchKeyword,ga:searchCategory,ga:searchStartPage',
                  'metrics': 'ga:searchSessions,ga:searchUniques,ga:searchResultViews,ga:searchExits,ga:searchRefinements,ga:searchDuration,ga:searchDepth',
                  'sort': None,
                  'filters': None,
                  'start_index': 1}

    GA_PNT_SEARCH = API_Result_DF(Dict_input)
    GA_PNT_SEARCH = GA_PNT_SEARCH.astype(
        {'searchSessions': int, 'searchUniques': int, 'searchResultViews': int, 'searchExits': int,
         'searchRefinements': int, 'searchDuration': float, 'searchDepth': int})
    GA_PNT_SEARCH.columns = [col.upper() for col in GA_PNT_SEARCH.columns.values]
    return GA_PNT_SEARCH



        # ### 13. GA_PNT_SOCIAL_MEDIUM
def get_GA_PNT_SOCIAL_MEDIUM(START_DATE, END_DATE):
    print(inspect.currentframe().f_code.co_name, START_DATE, END_DATE)
    ##GA_PNT_SOCIAL_MEDIUM
    ## NEW (Client ID 추가)
    ## date hour and minute 수정
    ## 디멘젼 landingPagePath 추가

    Dict_input = {'ids': 'ga:253231372',  # PNT샵
                  'start_date': START_DATE,
                  'end_date': END_DATE,
                  'dimensions': 'ga:dateHourMinute,ga:clientId,ga:channelGrouping,ga:source,ga:landingPagePath,ga:socialNetwork,ga:medium',
                  'metrics': 'ga:sessions',
                  'sort': None,
                  'filters': None,
                  'start_index': 1,
                  'max_results': 10000}

    GA_PNT_SOCIAL_MEDIUM = API_Result_DF(Dict_input)
    GA_PNT_SOCIAL_MEDIUM = GA_PNT_SOCIAL_MEDIUM.astype({'sessions': int})
    GA_PNT_SOCIAL_MEDIUM.columns = [col.upper() for col in GA_PNT_SOCIAL_MEDIUM.columns.values]

    GA_PNT_SOCIAL_MEDIUM['DATE'] = GA_PNT_SOCIAL_MEDIUM['DATEHOURMINUTE'].apply(lambda x: x[:8])
    GA_PNT_SOCIAL_MEDIUM['HOURMINUTE'] = GA_PNT_SOCIAL_MEDIUM['DATEHOURMINUTE'].apply(lambda x: x[8:])
    GA_PNT_SOCIAL_MEDIUM = pd.concat([GA_PNT_SOCIAL_MEDIUM.iloc[:, 8:], GA_PNT_SOCIAL_MEDIUM.iloc[:, 1:8]], axis=1)
    return GA_PNT_SOCIAL_MEDIUM

if __name__ == "__main__":
    O_GA_PNT_CLIENT = pd.DataFrame()
    O_GA_PNT_CLIENT_CITY = pd.DataFrame()
    O_GA_PNT_GENDER = pd.DataFrame()
    O_GA_PNT_AGE = pd.DataFrame()
    O_GA_PNT_AFFINITY = pd.DataFrame()
    O_GA_PNT_PAGE = pd.DataFrame()
    O_GA_PNT_ORDER = pd.DataFrame()
    O_GA_PNT_PRODUCT = pd.DataFrame()
    O_GA_PNT_ORDER_PRODUCT = pd.DataFrame()
    O_GA_PNT_SEARCH = pd.DataFrame()
    O_GA_PNT_GOAL = pd.DataFrame()
    O_GA_PNT_BEHAVIOR = pd.DataFrame()
    O_GA_PNT_SOCIAL_MEDIUM = pd.DataFrame()

    yesterday = date.today() - timedelta(days=1)
    # start_day = yesterday
    start_day = '2022-01-01'
    # end_day = yesterday
    end_day = '2022-05-31'
    date_range = pd.date_range(start_day, end_day)
    for single_date in date_range:
        print(single_date.strftime("%Y-%m-%d"))
        START_DATE = single_date.strftime("%Y-%m-%d")
        END_DATE = single_date.strftime("%Y-%m-%d")
        print(START_DATE, END_DATE)

        O_GA_PNT_CLIENT = pd.concat([O_GA_PNT_CLIENT, get_GA_PNT_CLIENT(START_DATE, END_DATE)])
        O_GA_PNT_CLIENT_CITY = pd.concat([O_GA_PNT_CLIENT_CITY, get_GA_PNT_CLIENT_CITY(START_DATE, END_DATE)])
        O_GA_PNT_GENDER = pd.concat([O_GA_PNT_GENDER, get_GA_PNT_GENDER(START_DATE, END_DATE)])
        O_GA_PNT_AGE = pd.concat([O_GA_PNT_AGE, get_GA_PNT_AGE(START_DATE, END_DATE)])
        O_GA_PNT_AFFINITY = pd.concat([O_GA_PNT_AFFINITY, get_GA_PNT_AFFINITY(START_DATE, END_DATE)])
        O_GA_PNT_PAGE = pd.concat([O_GA_PNT_PAGE, get_GA_PNT_PAGE(START_DATE, END_DATE)])
        O_GA_PNT_ORDER = pd.concat([O_GA_PNT_ORDER, get_GA_PNT_ORDER(START_DATE, END_DATE)])
        O_GA_PNT_PRODUCT = pd.concat([O_GA_PNT_PRODUCT, get_GA_PNT_PRODUCT(START_DATE, END_DATE)])
        O_GA_PNT_ORDER_PRODUCT = pd.concat([O_GA_PNT_ORDER_PRODUCT, get_GA_PNT_ORDER_PRODUCT(START_DATE, END_DATE)])
        O_GA_PNT_SEARCH = pd.concat([O_GA_PNT_SEARCH, get_GA_PNT_SEARCH(START_DATE, END_DATE)])
        O_GA_PNT_GOAL = pd.concat([O_GA_PNT_GOAL, get_GA_PNT_GOAL(START_DATE, END_DATE)])
        O_GA_PNT_BEHAVIOR = pd.concat([O_GA_PNT_BEHAVIOR, get_GA_PNT_BEHAVIOR(START_DATE, END_DATE)])
        O_GA_PNT_SOCIAL_MEDIUM = pd.concat([O_GA_PNT_SOCIAL_MEDIUM, get_GA_PNT_SOCIAL_MEDIUM(START_DATE, END_DATE)])


    O_GA_PNT_CLIENT.to_csv(f"{os.path.join(set_downloads_folder('ga'),'PNT_CLIENT.csv')}", encoding='utf-8-sig',index=False)
    O_GA_PNT_CLIENT_CITY.to_csv(f"{os.path.join(set_downloads_folder('ga'),'PNT_CLIENT_CITY.csv')}",encoding='utf-8-sig', index=False)
    O_GA_PNT_GENDER.to_csv(f"{os.path.join(set_downloads_folder('ga'),'PNT_GENDER.csv')}",encoding='utf-8-sig', index=False)
    O_GA_PNT_AGE.to_csv(f"{os.path.join(set_downloads_folder('ga'),'PNT_AGE.csv')}",encoding='utf-8-sig', index=False)
    O_GA_PNT_AFFINITY.to_csv(f"{os.path.join(set_downloads_folder('ga'),'PNT_AFFINITY.csv')}",encoding='utf-8-sig', index=False)
    O_GA_PNT_PAGE.to_csv(f"{os.path.join(set_downloads_folder('ga'),'PNT_PAGE.csv')}",encoding='utf-8-sig', index=False)
    O_GA_PNT_ORDER.to_csv(f"{os.path.join(set_downloads_folder('ga'),'PNT_ORDER.csv')}",encoding='utf-8-sig', index=False)
    O_GA_PNT_PRODUCT.to_csv(f"{os.path.join(set_downloads_folder('ga'),'PNT_PRODUCT.csv')}",encoding='utf-8-sig', index=False)
    O_GA_PNT_ORDER_PRODUCT.to_csv(f"{os.path.join(set_downloads_folder('ga'),'PNT_ORDER_PRODUCT.csv')}",encoding='utf-8-sig', index=False)
    O_GA_PNT_SEARCH.to_csv(f"{os.path.join(set_downloads_folder('ga'),'PNT_SEARCH.csv')}", encoding='utf-8-sig',index=False)
    O_GA_PNT_GOAL.to_csv(f"{os.path.join(set_downloads_folder('ga'),'PNT_GOAL.csv')}",encoding='utf-8-sig', index=False)
    O_GA_PNT_BEHAVIOR.to_csv(f"{os.path.join(set_downloads_folder('ga'),'PNT_BEHAVIOR.csv')}", encoding='utf-8-sig',index=False)
    O_GA_PNT_SOCIAL_MEDIUM.to_csv(f"{os.path.join(set_downloads_folder('ga'),'PNT_SOCIAL_MEDIUM.csv')}",encoding='utf-8-sig', index=False)

    system_name = "ga"
    set_downloads_folder(system_name)
    file_path = get_downloads_folder(system_name)
    for table_name in ["PNT_CLIENT", "PNT_CLIENT_CITY", "PNT_GENDER", "PNT_AGE", "PNT_AFFINITY", "PNT_PAGE", "PNT_PRODUCT", "PNT_ORDER_PRODUCT", "PNT_SEARCH", "PNT_GOAL", "PNT_BEHAVIOR", "PNT_SOCIAL_MEDIUM", "PNT_ORDER"]:
        upload_files_to_s3(upload_date=datetime.date.today().strftime("%y%m%d"), system_name=system_name, file=table_name+".csv")
        execute_truncate_query(system_name=system_name, table_name=table_name)
        execute_insert_query(system_name=system_name, table_name=table_name, data_date=date.today().strftime("%y%m%d"))
