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

def main(start_day, end_day):
    service_name = os.path.basename(__file__).replace(".py", "")
    O_GA_PNT_GOAL = pd.DataFrame()
    # yesterday = date.today() - timedelta(days=1)
    # start_day = '2022-05-29'
    # end_day = '2022-05-29'
    date_range = pd.date_range(start_day, end_day)
    for single_date in date_range:
        print(single_date.strftime("%Y-%m-%d"))
        START_DATE = single_date.strftime("%Y-%m-%d")
        END_DATE = single_date.strftime("%Y-%m-%d")
        print(START_DATE, END_DATE)
        O_GA_PNT_GOAL = pd.concat([O_GA_PNT_GOAL, get_GA_PNT_GOAL(START_DATE, END_DATE)])

    O_GA_PNT_GOAL.to_csv(f"{os.path.join(set_downloads_folder('ga'),f'{service_name}.csv')}", encoding='utf-8-sig', index=False)

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