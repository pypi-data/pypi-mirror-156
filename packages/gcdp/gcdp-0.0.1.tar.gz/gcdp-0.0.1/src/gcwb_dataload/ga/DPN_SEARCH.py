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

# # > ## OTHER
#
# # ### 10. GA_DPN_SEARCH
def get_GA_DPN_SEARCH(START_DATE, END_DATE):
    print(inspect.currentframe().f_code.co_name, START_DATE, END_DATE)
    Dict_input = {'ids':'ga:235889212', #Dr.PNT
                  'start_date':START_DATE,
                  'end_date':END_DATE,
                  'dimensions':'ga:date,ga:searchKeyword,ga:searchCategory,ga:searchStartPage',
                  'metrics':'ga:searchSessions,ga:searchUniques,ga:searchResultViews,ga:searchExits,ga:searchRefinements,ga:searchDuration,ga:searchDepth',
                  'sort':None,
                  'filters':None,
                  'start_index':1}

    GA_DPN_SEARCH = API_Result_DF(Dict_input)
    GA_DPN_SEARCH = GA_DPN_SEARCH.astype({'searchSessions':int,'searchUniques':int,'searchResultViews':int,'searchExits':int,
                                            'searchRefinements':int,'searchDuration':float,'searchDepth':int})
    GA_DPN_SEARCH.columns = [col.upper() for col in GA_DPN_SEARCH.columns.values]
    return GA_DPN_SEARCH

def main(start_day, end_day):
    service_name = os.path.basename(__file__).replace(".py", "")
    O_GA_DPN_SEARCH = pd.DataFrame()
    # yesterday = date.today() - timedelta(days=1)
    # start_day = yesterday
    # end_day = yesterday
    date_range = pd.date_range(start_day, end_day)
    for single_date in date_range:
        print(single_date.strftime("%Y-%m-%d"))
        START_DATE = single_date.strftime("%Y-%m-%d")
        END_DATE = single_date.strftime("%Y-%m-%d")
        print(START_DATE, END_DATE)
        O_GA_DPN_SEARCH = pd.concat([O_GA_DPN_SEARCH, get_GA_DPN_SEARCH(START_DATE, END_DATE)])

    O_GA_DPN_SEARCH.to_csv(f"{os.path.join(set_downloads_folder('ga'),f'{service_name}.csv')}", encoding='utf-8-sig', index=False)

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