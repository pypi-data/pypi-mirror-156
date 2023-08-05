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

from commonlibs.utils import project_path, get_downloads_folder, set_downloads_folder
from ..gcwb_sql.generate_query import execute_truncate_query, execute_insert_query
from ..gcwb_s3.upload_objects import upload_files_to_s3

# In[2]:


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


# # start_day = date(2021, 1, 18)
# start_day = date(2022, 4, 7)
# end_day = date(2022, 4, 8)
#
# print((end_day-start_day).days)
#
# O_GA_DPN_CLIENT = pd.DataFrame()
# O_GA_DPN_CLIENT_CITY = pd.DataFrame()
# O_GA_DPN_GENDER = pd.DataFrame()
# O_GA_DPN_AGE = pd.DataFrame()
# O_GA_DPN_AFFINITY = pd.DataFrame()
# O_GA_DPN_PAGE = pd.DataFrame()
# O_GA_DPN_ORDER = pd.DataFrame()
# O_GA_DPN_PRODUCT = pd.DataFrame()
# O_GA_DPN_ORDER_PRODUCT = pd.DataFrame()
# O_GA_DPN_SEARCH = pd.DataFrame()
# O_GA_DPN_GOAL = pd.DataFrame()
# O_GA_DPN_BEHAVIOR = pd.DataFrame()

# for timedelta_day in range(0, (end_day-start_day).days):
# ★ 일자 변경

# START_DATE = target_day.strftime("%Y-%m-%d")
# END_DATE = target_day.strftime("%Y-%m-%d")
# # START_DATE = "2022-01-01"
# # END_DATE = "2022-01-10"
# print(f"START_DATE: {START_DATE} ~ END: {END_DATE}")


# > ## CLIENT
# ### 1. GA_DPN_CLIENT
def get_GA_DPN_CLIENT(START_DATE, END_DATE):
    print(inspect.currentframe().f_code.co_name, START_DATE, END_DATE)
    ## date hour and minute 수정
    list_user = ['New Visitor', 'Returning Visitor']
    list_device = ['desktop', 'mobile', 'tablet']

    GA_DPN_CLIENT = pd.DataFrame()

    for USER in list_user:
        for DEVICE in list_device:
            Dict_input = {'ids': 'ga:235889212',  # Dr.PNT
                          'start_date': START_DATE,
                          'end_date': END_DATE,
                          'dimensions': 'ga:dateHourMinute,ga:clientId,ga:channelGrouping,ga:source,ga:landingPagePath,ga:exitPagePath,ga:city',
                          'metrics': 'ga:sessions,ga:bounces,ga:pageviews,ga:sessionDuration,ga:transactions,ga:transactionRevenue,ga:goal4Completions',
                          'sort': None,
                          'filters': 'ga:userType==' + USER + ';ga:deviceCategory==' + DEVICE,
                          'start_index': 1,
                          'max_results': 10000}

            DF_tmp = API_Result_DF(Dict_input)
            DF_tmp['userType'] = USER
            DF_tmp['deviceCategory'] = DEVICE

            GA_DPN_CLIENT = pd.concat([GA_DPN_CLIENT, DF_tmp], axis=0)

    GA_DPN_CLIENT = GA_DPN_CLIENT.reset_index(drop=True)
    GA_DPN_CLIENT = pd.concat([GA_DPN_CLIENT.iloc[:, :7], GA_DPN_CLIENT.iloc[:, 14:], GA_DPN_CLIENT.iloc[:, 7:14]],
                              axis=1)
    GA_DPN_CLIENT = GA_DPN_CLIENT.astype({'sessions': int, 'bounces': int, 'pageviews': int, 'sessionDuration': float,
                                          'transactions': int, 'transactionRevenue': float, 'goal4Completions': int})
    GA_DPN_CLIENT.columns = [col.upper() for col in GA_DPN_CLIENT.columns.values]

    GA_DPN_CLIENT['DATE'] = GA_DPN_CLIENT['DATEHOURMINUTE'].apply(lambda x: x[:8])
    GA_DPN_CLIENT['HOURMINUTE'] = GA_DPN_CLIENT['DATEHOURMINUTE'].apply(lambda x: x[8:])
    GA_DPN_CLIENT = pd.concat([GA_DPN_CLIENT.iloc[:, 16:], GA_DPN_CLIENT.iloc[:, 1:16]], axis=1)
    return GA_DPN_CLIENT



# 2. GA_DPN_CLIENT_CITY
def get_GA_DPN_CLIENT_CITY(START_DATE, END_DATE):
    print(inspect.currentframe().f_code.co_name, START_DATE, END_DATE)
    ## date hour and minute 수정
    Dict_input = {'ids': 'ga:235889212',  # Dr.PNT
                  'start_date': START_DATE,
                  'end_date': END_DATE,
                  'dimensions': 'ga:dateHourMinute,ga:clientId,ga:city,ga:country,ga:region',
                  'metrics': 'ga:sessions',
                  'sort': None,
                  'filters': None,
                  'start_index': 1,
                  'max_results': 10000}

    GA_DPN_CLIENT_CITY = API_Result_DF(Dict_input)
    GA_DPN_CLIENT_CITY = GA_DPN_CLIENT_CITY.astype({'sessions': int})
    GA_DPN_CLIENT_CITY.columns = [col.upper() for col in GA_DPN_CLIENT_CITY.columns.values]

    GA_DPN_CLIENT_CITY['DATE'] = GA_DPN_CLIENT_CITY['DATEHOURMINUTE'].apply(lambda x: x[:8])
    GA_DPN_CLIENT_CITY['HOURMINUTE'] = GA_DPN_CLIENT_CITY['DATEHOURMINUTE'].apply(lambda x: x[8:])
    GA_DPN_CLIENT_CITY = pd.concat([GA_DPN_CLIENT_CITY.iloc[:, 6:], GA_DPN_CLIENT_CITY.iloc[:, 1:6]], axis=1)
    return GA_DPN_CLIENT_CITY



# ### 3. GA_DPN_GENDER
def get_GA_DPN_GENDER(START_DATE, END_DATE):
    print(inspect.currentframe().f_code.co_name, START_DATE, END_DATE)
    Dict_input = {'ids':'ga:235889212', #Dr.PNT
                  'start_date':START_DATE,
                  'end_date':END_DATE,
                  'dimensions':'ga:date,ga:userGender',
                  'metrics':'ga:users,ga:newUsers,ga:sessions,ga:bounces,ga:pageviews,ga:sessionDuration,ga:transactions,ga:transactionRevenue,ga:goal4Completions',
                  'sort':None,
                  'filters':None,
                  'start_index':1}

    GA_DPN_GENDER = API_Result_DF(Dict_input)
    GA_DPN_GENDER = GA_DPN_GENDER.astype({'users':int,'newUsers':int,'sessions':int,
                                          'bounces':int,'pageviews':int,'sessionDuration':float,
                                          'transactions':int,'transactionRevenue':float,'goal4Completions':int})
    GA_DPN_GENDER.columns = [col.upper() for col in GA_DPN_GENDER.columns.values]
    return GA_DPN_GENDER


# ### 4. GA_DPN_AGE
def get_GA_DPN_AGE(START_DATE, END_DATE):
    print(inspect.currentframe().f_code.co_name, START_DATE, END_DATE)
    Dict_input = {'ids':'ga:235889212', #Dr.PNT
                  'start_date':START_DATE,
                  'end_date':END_DATE,
                  'dimensions':'ga:date,ga:userAgeBracket',
                  'metrics':'ga:users,ga:newUsers,ga:sessions,ga:bounces,ga:pageviews,ga:sessionDuration,ga:transactions,ga:transactionRevenue,ga:goal4Completions',
                  'sort':None,
                  'filters':None,
                  'start_index':1}

    GA_DPN_AGE = API_Result_DF(Dict_input)
    GA_DPN_AGE = GA_DPN_AGE.astype({'users':int,'newUsers':int,'sessions':int,
                                    'bounces':int,'pageviews':int,'sessionDuration':float,
                                    'transactions':int,'transactionRevenue':float,'goal4Completions':int})
    GA_DPN_AGE.columns = [col.upper() for col in GA_DPN_AGE.columns.values]
    return GA_DPN_AGE



# 5. GA_DPN_AFFINITY
def get_GA_DPN_AFFINITY(START_DATE, END_DATE):
    print(inspect.currentframe().f_code.co_name, START_DATE, END_DATE)
    Dict_input = {'ids':'ga:235889212', #Dr.PNT
                  'start_date':START_DATE,
                  'end_date':END_DATE,
                  'dimensions':'ga:date,ga:interestAffinityCategory',
                  'metrics':'ga:users,ga:newUsers,ga:sessions,ga:bounces,ga:pageviews,ga:sessionDuration,ga:transactions,ga:transactionRevenue,ga:goal4Completions',
                  'sort':None,
                  'filters':None,
                  'start_index':1}

    GA_DPN_AFFINITY = API_Result_DF(Dict_input)
    GA_DPN_AFFINITY = GA_DPN_AFFINITY.astype({'users':int,'newUsers':int,'sessions':int,
                                            'bounces':int,'pageviews':int,'sessionDuration':float,
                                            'transactions':int,'transactionRevenue':float,'goal4Completions':int})
    GA_DPN_AFFINITY.columns = [col.upper() for col in GA_DPN_AFFINITY.columns.values]
    return GA_DPN_AFFINITY

# # # > ## PAGE
# # ### 6. GA_DPN_PAGE
def get_GA_DPN_PAGE(START_DATE, END_DATE):
    print(inspect.currentframe().f_code.co_name, START_DATE, END_DATE)
    Dict_input = {'ids': 'ga:235889212',  # Dr.PNT
                  'start_date': START_DATE,
                  'end_date': END_DATE,
                  'dimensions': 'ga:date,ga:clientId,ga:pagePath,ga:pagePathLevel1',
                  'metrics': 'ga:pageviews,ga:uniquePageviews,ga:entrances,ga:bounces,ga:exits,ga:timeOnPage',
                  'sort': None,
                  'filters': None,
                  'start_index': 1}

    GA_DPN_PAGE = API_Result_DF(Dict_input)
    GA_DPN_PAGE = GA_DPN_PAGE.astype({'pageviews': int, 'uniquePageviews': int, 'entrances': int, 'bounces': int, 'exits': int, 'timeOnPage': float})
    GA_DPN_PAGE.columns = [col.upper() for col in GA_DPN_PAGE.columns.values]

    # page path level2
    Dict_input = {'ids': 'ga:235889212',  # Dr.PNT
                  'start_date': START_DATE,
                  'end_date': END_DATE,
                  'dimensions': 'ga:pagePath,ga:pagePathLevel2',
                  'metrics': 'ga:pageviews',
                  'start_index': 1}
    GA_DPN_PAGE_lv2 = API_Result_DF(Dict_input)
    GA_DPN_PAGE_lv2.columns = [col.upper() for col in GA_DPN_PAGE_lv2.columns.values]

    # page path level3
    Dict_input = {'ids': 'ga:235889212',  # Dr.PNT
                  'start_date': START_DATE,
                  'end_date': END_DATE,
                  'dimensions': 'ga:pagePath,ga:pagePathLevel3',
                  'metrics': 'ga:pageviews',
                  'start_index': 1}
    GA_DPN_PAGE_lv3 = API_Result_DF(Dict_input)
    GA_DPN_PAGE_lv3.columns = [col.upper() for col in GA_DPN_PAGE_lv3.columns.values]

    # page path level4
    Dict_input = {'ids': 'ga:235889212',  # Dr.PNT
                  'start_date': START_DATE,
                  'end_date': END_DATE,
                  'dimensions': 'ga:pagePath,ga:pagePathLevel4',
                  'metrics': 'ga:pageviews',
                  'start_index': 1}
    GA_DPN_PAGE_lv4 = API_Result_DF(Dict_input)
    GA_DPN_PAGE_lv4.columns = [col.upper() for col in GA_DPN_PAGE_lv4.columns.values]
    GA_DPN_PAGE = pd.merge(GA_DPN_PAGE, GA_DPN_PAGE_lv2[['PAGEPATH', 'PAGEPATHLEVEL2']], how='left', left_on='PAGEPATH', right_on='PAGEPATH')
    GA_DPN_PAGE = pd.merge(GA_DPN_PAGE, GA_DPN_PAGE_lv3[['PAGEPATH', 'PAGEPATHLEVEL3']], how='left', left_on='PAGEPATH', right_on='PAGEPATH')
    GA_DPN_PAGE = pd.merge(GA_DPN_PAGE, GA_DPN_PAGE_lv4[['PAGEPATH', 'PAGEPATHLEVEL4']], how='left', left_on='PAGEPATH', right_on='PAGEPATH')

    GA_DPN_PAGE = pd.concat([GA_DPN_PAGE.iloc[:, :4], GA_DPN_PAGE.iloc[:, 10:], GA_DPN_PAGE.iloc[:, 4:10]], axis=1)
    return GA_DPN_PAGE


# # # > ## ORDER, PRODUCT

## 7. GA_DPN_ORDER

def get_GA_DPN_ORDER(START_DATE, END_DATE):
    print(inspect.currentframe().f_code.co_name, START_DATE, END_DATE)
    Dict_input = {'ids': 'ga:235889212',  # Dr.PNT
                  'start_date': START_DATE,
                  'end_date': END_DATE,
                  'dimensions': 'ga:date,ga:clientId,ga:transactionId,ga:channelGrouping,ga:source,ga:medium,ga:city',
                  'metrics': 'ga:transactions,ga:transactionRevenue,ga:transactionTax,ga:transactionShipping,ga:refundAmount,ga:itemQuantity',
                  'sort': None,
                  'filters': None,
                  'start_index': 1}

    GA_DPN_ORDER = API_Result_DF(Dict_input)
    GA_DPN_ORDER = GA_DPN_ORDER.astype({'transactions': int, 'transactionRevenue': float, 'transactionTax': float,
                                        'transactionShipping': float, 'refundAmount': float, 'itemQuantity': int})
    GA_DPN_ORDER.columns = [col.upper() for col in GA_DPN_ORDER.columns.values]
    GA_DPN_ORDER = GA_DPN_ORDER[GA_DPN_ORDER['TRANSACTIONID'] != ''].reset_index(drop=True)
    return GA_DPN_ORDER

# 8. GA_DPN_PRODUCT
def get_GA_DPN_PRODUCT(START_DATE, END_DATE):
    print(inspect.currentframe().f_code.co_name, START_DATE, END_DATE)
    ## 22.06.16 수정 : (API) productCategoryHierarchy 제외

    ## PRODUCT 1
    Dict_input = {'ids': 'ga:235889212',  # Dr.PNT
                  'start_date': START_DATE,
                  'end_date': END_DATE,
                  'dimensions': 'ga:date,ga:clientId,ga:productSku,ga:productName,ga:productListName,ga:productBrand',
                  'metrics': 'ga:itemRevenue,ga:uniquePurchases,ga:itemQuantity,ga:productRefundAmount,ga:quantityAddedToCart,ga:quantityRemovedFromCart',
                  'sort': None,
                  'filters': None,
                  'start_index': 1,
                  'max_results': 10000}

    GA_DPN_PRODUCT_1 = API_Result_DF(Dict_input)
    GA_DPN_PRODUCT_1 = GA_DPN_PRODUCT_1.astype(
        {'itemRevenue': float, 'uniquePurchases': int, 'itemQuantity': int, 'productRefundAmount': float,
         'quantityAddedToCart': int, 'quantityRemovedFromCart': int})
    # PRODUCTSKU,PRODUCTNAME 오류값 수정
    for i in range(len(GA_DPN_PRODUCT_1)):
        try:
            int(GA_DPN_PRODUCT_1['productSku'][i])
        except:
            PRODUCT_NAME = GA_DPN_PRODUCT_1['productSku'][i]
            GA_DPN_PRODUCT_1['productSku'][i] = GA_DPN_PRODUCT_1['productName'][i]
            GA_DPN_PRODUCT_1['productName'][i] = PRODUCT_NAME

    # 중복데이터 통합
    GA_DPN_PRODUCT_1 = GA_DPN_PRODUCT_1.groupby(['date', 'clientId', 'productSku', 'productName',
                                                 'productListName', 'productBrand'])[
        ['itemRevenue', 'uniquePurchases', 'itemQuantity',
         'productRefundAmount', 'quantityAddedToCart',
         'quantityRemovedFromCart']].sum().reset_index()

    ## PRODUCT 2
    Dict_input = {'ids': 'ga:235889212',  # Dr.PNT
                  'start_date': START_DATE,
                  'end_date': END_DATE,
                  'dimensions': 'ga:date,ga:clientId,ga:productSku,ga:productName,ga:productListName,ga:productBrand',
                  'metrics': 'ga:productCheckouts,ga:productAddsToCart,ga:productRemovesFromCart,ga:productDetailViews,ga:productListViews,ga:productListClicks',
                  'sort': None,
                  'filters': None,
                  'start_index': 1,
                  'max_results': 10000}

    GA_DPN_PRODUCT_2 = API_Result_DF(Dict_input)
    GA_DPN_PRODUCT_2 = GA_DPN_PRODUCT_2.astype(
        {'productCheckouts': int, 'productAddsToCart': int, 'productRemovesFromCart': int,
         'productDetailViews': int, 'productListViews': int, 'productListClicks': int})

    # PRODUCTSKU,PRODUCTNAME 오류값 수정
    for i in range(len(GA_DPN_PRODUCT_2)):
        try:
            int(GA_DPN_PRODUCT_2['productSku'][i])
        except:
            PRODUCT_NAME = GA_DPN_PRODUCT_2['productSku'][i]
            GA_DPN_PRODUCT_2['productSku'][i] = GA_DPN_PRODUCT_2['productName'][i]
            GA_DPN_PRODUCT_2['productName'][i] = PRODUCT_NAME

    # 중복데이터 통합
    GA_DPN_PRODUCT_2 = GA_DPN_PRODUCT_2.groupby(['date', 'clientId', 'productSku', 'productName',
                                                 'productListName', 'productBrand'])[
        ['productCheckouts', 'productAddsToCart',
         'productRemovesFromCart', 'productDetailViews',
         'productListViews', 'productListClicks']].sum().reset_index()

    GA_DPN_PRODUCT = pd.merge(GA_DPN_PRODUCT_1, GA_DPN_PRODUCT_2, how='inner',
                              on=['date', 'clientId', 'productSku', 'productName', 'productListName', 'productBrand'])
    GA_DPN_PRODUCT.columns = [col.upper() for col in GA_DPN_PRODUCT.columns.values]

    GA_DPN_PRODUCT['PRODUCTCATEGORYHIERARCHY'] = '(not set)'
    GA_DPN_PRODUCT = pd.concat([GA_DPN_PRODUCT.iloc[:, :6], GA_DPN_PRODUCT.iloc[:, -1:], GA_DPN_PRODUCT.iloc[:, 6:-1]],
                               axis=1)
    return GA_DPN_PRODUCT
#
#
# # ### 9. GA_DPN_ORDER_PRODUCT
def get_GA_DPN_ORDER_PRODUCT(START_DATE, END_DATE):
    print(inspect.currentframe().f_code.co_name, START_DATE, END_DATE)
    Dict_input = {'ids':'ga:235889212', #Dr.PNT
                  'start_date':START_DATE,
                  'end_date':END_DATE,
                  'dimensions':'ga:date,ga:transactionId,ga:productSku,ga:productName',
                  'metrics':'ga:itemRevenue,ga:itemQuantity',
                  'sort':None,
                  'filters':None,
                  'start_index':1}

    GA_DPN_ORDER_PRODUCT = API_Result_DF(Dict_input)
    GA_DPN_ORDER_PRODUCT = GA_DPN_ORDER_PRODUCT.astype({'itemRevenue':float,'itemQuantity':int})
    GA_DPN_ORDER_PRODUCT.columns = [col.upper() for col in GA_DPN_ORDER_PRODUCT.columns.values]
    return GA_DPN_ORDER_PRODUCT


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


#
# # ### 11. GA_DPN_GOAL (※ ga 목표 변경시 컬럼변경)
def get_GA_DPN_GOAL(START_DATE, END_DATE):
    Dict_input = {'ids': 'ga:235889212',  # Dr.PNT
                  'start_date': START_DATE,
                  'end_date': END_DATE,
                  'dimensions': 'ga:date,ga:goalCompletionLocation',
                  'metrics': 'ga:goalCompletionsAll,ga:goalValueAll,ga:goal1Completions,ga:goal1Value,ga:goal2Completions,ga:goal2Value,ga:goal3Completions,ga:goal3Value,ga:goal4Completions,ga:goal4Value',
                  'sort': None,
                  'filters': None,
                  'start_index': 1}

    GA_DPN_GOAL_1 = API_Result_DF(Dict_input)
    GA_DPN_GOAL_1 = GA_DPN_GOAL_1.astype({'goalCompletionsAll': int, 'goalValueAll': float,
                                          'goal1Completions': int, 'goal1Value': float,
                                          'goal2Completions': int, 'goal2Value': float,
                                          'goal3Completions': int, 'goal3Value': float,
                                          'goal4Completions': int, 'goal4Value': float})

    Dict_input = {'ids': 'ga:235889212',  # Dr.PNT
                  'start_date': START_DATE,
                  'end_date': END_DATE,
                  'dimensions': 'ga:date,ga:goalCompletionLocation',
                  'metrics': 'ga:goal5Completions,ga:goal5Value,ga:goal6Completions,ga:goal6Value,ga:goal7Completions,ga:goal7Value,ga:goal8Completions,ga:goal8Value,ga:goal9Completions,ga:goal9Value',
                  'sort': None,
                  'filters': None,
                  'start_index': 1}

    GA_DPN_GOAL_2 = API_Result_DF(Dict_input)
    GA_DPN_GOAL_2 = GA_DPN_GOAL_2.astype({'goal5Completions': int, 'goal5Value': float,
                                          'goal6Completions': int, 'goal6Value': float,
                                          'goal7Completions': int, 'goal7Value': float,
                                          'goal8Completions': int, 'goal8Value': float,
                                          'goal9Completions': int, 'goal9Value': float})

    GA_DPN_GOAL = pd.merge(GA_DPN_GOAL_1, GA_DPN_GOAL_2, how='inner', on=['date', 'goalCompletionLocation'])
    GA_DPN_GOAL.columns = [col.upper() for col in GA_DPN_GOAL.columns.values]
    GA_DPN_GOAL = GA_DPN_GOAL[['DATE', 'GOALCOMPLETIONLOCATION', 'GOALCOMPLETIONSALL', 'GOALVALUEALL',
                               'GOAL1COMPLETIONS', 'GOAL1VALUE', 'GOAL2COMPLETIONS', 'GOAL2VALUE',
                               'GOAL3COMPLETIONS', 'GOAL3VALUE', 'GOAL4COMPLETIONS', 'GOAL4VALUE',
                               'GOAL5COMPLETIONS', 'GOAL5VALUE', 'GOAL6COMPLETIONS', 'GOAL6VALUE',
                               'GOAL7COMPLETIONS', 'GOAL7VALUE', 'GOAL8COMPLETIONS', 'GOAL8VALUE',
                               'GOAL9COMPLETIONS', 'GOAL9VALUE']]
    return GA_DPN_GOAL

# ### 12. GA_DPN_BEHAVIOR
def get_GA_DPN_BEHAVIOR(START_DATE, END_DATE):
    print(inspect.currentframe().f_code.co_name, START_DATE, END_DATE)
    Dict_input = {'ids': 'ga:235889212',  # Dr.PNT
                  'start_date': START_DATE,
                  'end_date': END_DATE,
                  'dimensions': 'ga:date,ga:shoppingStage,ga:userType',
                  'metrics': 'ga:sessions',
                  'sort': None,
                  'filters': None,
                  'start_index': 1}

    GA_DPN_BEHAVIOR = API_Result_DF(Dict_input)
    GA_DPN_BEHAVIOR = GA_DPN_BEHAVIOR.astype({'sessions': int})
    GA_DPN_BEHAVIOR.columns = [col.upper() for col in GA_DPN_BEHAVIOR.columns.values]
    return GA_DPN_BEHAVIOR

# ### 12. GA_DPN_SOCIAL_MEDIUM
def get_GA_DPN_SOCIAL_MEDIUM(START_DATE, END_DATE):
    ## GA_DPN_SOCIAL_MEDIUM
    print(inspect.currentframe().f_code.co_name, START_DATE, END_DATE)
    ## NEW (Client ID 추가)
    ## date hour and minute 수정
    ## 디멘젼 landingPagePath 추가

    Dict_input = {'ids': 'ga:235889212',  # Dr.PNT
                  'start_date': START_DATE,
                  'end_date': END_DATE,
                  'dimensions': 'ga:dateHourMinute,ga:clientId,ga:channelGrouping,ga:source,ga:landingPagePath,ga:socialNetwork,ga:medium',
                  'metrics': 'ga:sessions',
                  'sort': None,
                  'filters': None,
                  'start_index': 1,
                  'max_results': 10000}

    GA_DPN_SOCIAL_MEDIUM = API_Result_DF(Dict_input)
    GA_DPN_SOCIAL_MEDIUM = GA_DPN_SOCIAL_MEDIUM.astype({'sessions': int})
    GA_DPN_SOCIAL_MEDIUM.columns = [col.upper() for col in GA_DPN_SOCIAL_MEDIUM.columns.values]

    GA_DPN_SOCIAL_MEDIUM['DATE'] = GA_DPN_SOCIAL_MEDIUM['DATEHOURMINUTE'].apply(lambda x: x[:8])
    GA_DPN_SOCIAL_MEDIUM['HOURMINUTE'] = GA_DPN_SOCIAL_MEDIUM['DATEHOURMINUTE'].apply(lambda x: x[8:])
    GA_DPN_SOCIAL_MEDIUM = pd.concat([GA_DPN_SOCIAL_MEDIUM.iloc[:, 8:], GA_DPN_SOCIAL_MEDIUM.iloc[:, 1:8]], axis=1)
    return GA_DPN_SOCIAL_MEDIUM

def main():
    O_GA_DPN_CLIENT = pd.DataFrame()
    O_GA_DPN_CLIENT_CITY = pd.DataFrame()
    O_GA_DPN_GENDER = pd.DataFrame()
    O_GA_DPN_AGE = pd.DataFrame()
    O_GA_DPN_AFFINITY = pd.DataFrame()
    O_GA_DPN_PAGE = pd.DataFrame()
    O_GA_DPN_ORDER = pd.DataFrame()
    O_GA_DPN_PRODUCT = pd.DataFrame()
    O_GA_DPN_ORDER_PRODUCT = pd.DataFrame()
    O_GA_DPN_SEARCH = pd.DataFrame()
    O_GA_DPN_GOAL = pd.DataFrame()
    O_GA_DPN_BEHAVIOR = pd.DataFrame()
    O_GA_DPN_SOCIAL_MEDIUM = pd.DataFrame()

    yesterday = date.today() - timedelta(days=1)
    # start_day = yesterday
    start_day = '2022-06-14'
    # end_day = yesterday
    end_day = '2022-06-14'
    date_range = pd.date_range(start_day, end_day)
    for single_date in date_range:
        print(single_date.strftime("%Y-%m-%d"))
        START_DATE = single_date.strftime("%Y-%m-%d")
        END_DATE = single_date.strftime("%Y-%m-%d")
        print(START_DATE, END_DATE)

        O_GA_DPN_CLIENT = pd.concat([O_GA_DPN_CLIENT, get_GA_DPN_CLIENT(START_DATE, END_DATE)])
        O_GA_DPN_CLIENT_CITY = pd.concat([O_GA_DPN_CLIENT_CITY, get_GA_DPN_CLIENT_CITY(START_DATE, END_DATE)])
        O_GA_DPN_GENDER = pd.concat([O_GA_DPN_GENDER, get_GA_DPN_GENDER(START_DATE, END_DATE)])
        O_GA_DPN_AGE = pd.concat([O_GA_DPN_AGE, get_GA_DPN_AGE(START_DATE, END_DATE)])
        O_GA_DPN_AFFINITY = pd.concat([O_GA_DPN_AFFINITY, get_GA_DPN_AFFINITY(START_DATE, END_DATE)])
        O_GA_DPN_PAGE = pd.concat([O_GA_DPN_PAGE, get_GA_DPN_PAGE(START_DATE, END_DATE)])
        O_GA_DPN_ORDER = pd.concat([O_GA_DPN_ORDER, get_GA_DPN_ORDER(START_DATE, END_DATE)])
        O_GA_DPN_PRODUCT = pd.concat([O_GA_DPN_PRODUCT, get_GA_DPN_PRODUCT(START_DATE, END_DATE)])
        O_GA_DPN_ORDER_PRODUCT = pd.concat([O_GA_DPN_ORDER_PRODUCT, get_GA_DPN_ORDER_PRODUCT(START_DATE, END_DATE)])
        O_GA_DPN_SEARCH = pd.concat([O_GA_DPN_SEARCH, get_GA_DPN_SEARCH(START_DATE, END_DATE)])
        O_GA_DPN_GOAL = pd.concat([O_GA_DPN_GOAL, get_GA_DPN_GOAL(START_DATE, END_DATE)])
        O_GA_DPN_BEHAVIOR = pd.concat([O_GA_DPN_BEHAVIOR, get_GA_DPN_BEHAVIOR(START_DATE, END_DATE)])
        O_GA_DPN_SOCIAL_MEDIUM = pd.concat([O_GA_DPN_SOCIAL_MEDIUM, get_GA_DPN_SOCIAL_MEDIUM(START_DATE, END_DATE)])

    O_GA_DPN_CLIENT.to_csv(f"{os.path.join(set_downloads_folder('ga'),'DPN_CLIENT.csv')}", encoding='utf-8-sig',index=False)
    O_GA_DPN_CLIENT_CITY.to_csv(f"{os.path.join(set_downloads_folder('ga'),'DPN_CLIENT_CITY.csv')}",encoding='utf-8-sig', index=False)
    O_GA_DPN_GENDER.to_csv(f"{os.path.join(set_downloads_folder('ga'),'DPN_GENDER.csv')}",encoding='utf-8-sig', index=False)
    O_GA_DPN_AGE.to_csv(f"{os.path.join(set_downloads_folder('ga'),'DPN_AGE.csv')}",encoding='utf-8-sig', index=False)
    O_GA_DPN_AFFINITY.to_csv(f"{os.path.join(set_downloads_folder('ga'),'DPN_AFFINITY.csv')}",encoding='utf-8-sig', index=False)
    O_GA_DPN_PAGE.to_csv(f"{os.path.join(set_downloads_folder('ga'),'DPN_PAGE.csv')}",encoding='utf-8-sig', index=False)
    O_GA_DPN_ORDER.to_csv(f"{os.path.join(set_downloads_folder('ga'),'DPN_ORDER.csv')}",encoding='utf-8-sig', index=False)
    O_GA_DPN_PRODUCT.to_csv(f"{os.path.join(set_downloads_folder('ga'),'DPN_PRODUCT.csv')}",encoding='utf-8-sig', index=False)
    O_GA_DPN_ORDER_PRODUCT.to_csv(f"{os.path.join(set_downloads_folder('ga'),'DPN_ORDER_PRODUCT.csv')}",encoding='utf-8-sig', index=False)
    O_GA_DPN_SEARCH.to_csv(f"{os.path.join(set_downloads_folder('ga'),'DPN_SEARCH.csv')}", encoding='utf-8-sig',index=False)
    O_GA_DPN_GOAL.to_csv(f"{os.path.join(set_downloads_folder('ga'),'DPN_GOAL.csv')}",encoding='utf-8-sig', index=False)
    O_GA_DPN_BEHAVIOR.to_csv(f"{os.path.join(set_downloads_folder('ga'),'DPN_BEHAVIOR.csv')}", encoding='utf-8-sig',index=False)
    O_GA_DPN_SOCIAL_MEDIUM.to_csv(f"{os.path.join(set_downloads_folder('ga'),'DPN_SOCIAL_MEDIUM.csv')}",encoding='utf-8-sig', index=False)

    system_name = "ga"
    set_downloads_folder(system_name)
    file_path = get_downloads_folder(system_name)
    for table_name in ["DPN_CLIENT", "DPN_CLIENT_CITY", "DPN_GENDER", "DPN_AGE", "DPN_AFFINITY", "DPN_PAGE", "DPN_PRODUCT", "DPN_ORDER_PRODUCT", "DPN_SEARCH", "DPN_GOAL", "DPN_BEHAVIOR", "DPN_SOCIAL_MEDIUM", "DPN_ORDER"]:
        upload_files_to_s3(upload_date=datetime.date.today().strftime("%y%m%d"), system_name=system_name, file=table_name+".csv")
        execute_truncate_query(system_name=system_name, table_name=table_name)
        execute_insert_query(system_name=system_name, table_name=table_name, data_date=date.today().strftime("%y%m%d"))

if __name__ == "__main__":
    main()