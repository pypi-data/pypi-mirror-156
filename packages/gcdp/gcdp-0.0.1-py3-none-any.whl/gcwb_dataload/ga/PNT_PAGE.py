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
from gcwb_dataload.ga.clibs import service, API_Result_DF
from commonlibs.utils import set_downloads_folder
from ..gcwb_sql.generate_query import execute_delete_query_ga, execute_rownum_query, execute_insert_query
from ..gcwb_s3.upload_objects import upload_files_to_s3

# Get a list of all Google Analytics accounts for this user
accounts = service.management().accounts().list().execute()

if accounts.get('items'):
    # Get the first Google Analytics account.
    account = accounts.get('items')[0].get('id')

    # Get a list of all the properties for the first account.
    properties = service.management().webproperties().list(accountId=account).execute()


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


def main(start_day, end_day):
    service_name = os.path.basename(__file__).replace(".py", "")
    O_GA_PNT_PAGE = pd.DataFrame()
    # yesterday = date.today() - timedelta(days=1)
    # start_day = '2022-05-29'
    # end_day = '2022-05-29'
    date_range = pd.date_range(start_day, end_day)
    for single_date in date_range:
        print(single_date.strftime("%Y-%m-%d"))
        START_DATE = single_date.strftime("%Y-%m-%d")
        END_DATE = single_date.strftime("%Y-%m-%d")
        print(START_DATE, END_DATE)
        O_GA_PNT_PAGE = pd.concat([O_GA_PNT_PAGE, get_GA_PNT_PAGE(START_DATE, END_DATE)])

    O_GA_PNT_PAGE.to_csv(f"{os.path.join(set_downloads_folder('ga'),f'{service_name}.csv')}", encoding='utf-8-sig', index=False)

    system_name = "ga"
    set_downloads_folder(system_name)
    upload_files_to_s3(upload_date=datetime.date.today().strftime("%y%m%d"),
                       system_name=system_name,
                       file=f"{service_name}.csv")
    execute_delete_query_ga(system_name=system_name,
                         table_name=f"{service_name}")  # download폴더내 csv파일에 있는 날짜를 FROM TO에서 있으면 지운다.
    execute_insert_query(system_name=system_name,
                         table_name=f"{service_name}",
                         data_date=date.today().strftime("%y%m%d"))


if __name__ == "__main__":
    import sys
    yesterday = date.today() - timedelta(days=1)
    # 파라미터가 없을때 즉, yesterday만 가져올때, daily배치
    if len(sys.argv) == 1:
        print(len(sys.argv) == 1)
        start_day = yesterday
        end_day = yesterday
        main(start_day=start_day, end_day=end_day)
    # 파라미터가 있을때 즉, date를 range로 넣어서 실행할때
    else:
        print("else")
        start_day = sys.argv[1]
        end_day = sys.argv[2]
        main(start_day=start_day, end_day=end_day)
    table_name = os.path.basename(__file__).replace(".py", "")
    execute_rownum_query(system_name="GA", table_name=table_name)