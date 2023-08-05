import json
import os.path

import requests
import math
from sqlalchemy import create_engine
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
import numpy as np
from sqlalchemy.sql import text as sa_text
from datetime import date

project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

with open(f"{os.path.join(project_path, 'secret.json')}", "r") as json_read:
    info = json.loads(json_read.read())

class public_data_gokr():
    def __init__(self, tablename, url_prefix, url_parameters, connection_string):
        self.tablename = tablename
        self.url = url_prefix+url_parameters
        self.connection_string=connection_string

    def crawler(self):
        print(self.url)
        res = requests.get(url=self.url).text
        jsondata = json.loads(res)
        totalcount = jsondata['response']['body']['totalCount']
        maxpageno = math.ceil(totalcount/numOfRows)
        print(totalcount, maxpageno)
        engine = self.connect_db("snowflake")
        total_df = pd.DataFrame()
        for pageno in range(1, maxpageno + 1):
        # for pageno in range(1, 3):
            url = f"{self.url}&pageNo={pageno}"
            print(pageno, end=' ')
            res = requests.get(url=url, allow_redirects=False).text
            jsondata = json.loads(res)
            items = jsondata['response']['body']['items']
            df = pd.DataFrame(items)
            df['REGT_ID'] = 'yjjo'
            df['REG_DTTM'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # print(df)
            total_df = pd.concat([total_df, df])
            if ((pageno % 40) == 0):
                print()
        total_df.columns = total_df.columns.str.lower()
        print(total_df)
        # total_df.to_sql(name=f"{self.tablename}".lower(), index=False, con=engine, if_exists='append', chunksize=16000, dtype={
        #     'ENTRPS':sqlalchemy.types.VARCHAR(128),
        #     'PRDUCT':sqlalchemy.types.VARCHAR(1024),
        #     'STTEMNT_NO':sqlalchemy.types.VARCHAR(1024),
        #     'REGIST_DT':sqlalchemy.types.VARCHAR(1024),
        #     'REGT_ID':sqlalchemy.types.VARCHAR(10),
        #     'REG_DTTM':sqlalchemy.types.DATE})
        print()



    def connect_db(self, dbms_type):
        if dbms_type == "snowflake":
            # 'snowflake://<user_login_name>:<password>@<account_identifier>/<database_name>/<schema_name>?warehouse=<warehouse_name>&role=<role_name>'
            self.connection_string = f'snowflake://{info["sf_user"]}:{info["sf_pwd"]}@' \
                                     f'{info["sf_host"]}/{info["sf_db"]}/{info["sf_schema"]}?' \
                                     f'warehouse={info["sf_wh"]}&role={info["sf_role"]}'
        elif dbms_type == "mysql":
            self.connection_string = f'mysql+pymysql://{info["mysql_user"]}:{info["mysql_pwd"]}@' \
                                     f'{info["mysql_host"]}:{info["mysql_port"]}/{info["mysql_db"]}'
            print(self.connection_string)
        elif dbms_type == "postgres":
            self.connection_string = f'postgresql+psycopg2://{info["postgres_user"]}:{info["postgres_pwd"]}@' \
                                     f'{info["postgres_host"]}:{info["postgres_port"]}/{info["postgres_db"]}'
        elif dbms_type == "mssql":
            self.connection_string = f'mssql+pymssql://{info["mssql_user"]}:{info["mssql_pwd"]}@' \
                                     f'{info["mssql_host"]}:{info["mssql_port"]}/{info["mssql_db"]}'
        else:
            raise "UNSUPPORTED DBMS"

        return create_engine(self.connection_string)

class RestDeInfo(public_data_gokr):
    def connect_db(self, dbms_type):
        if dbms_type == "snowflake":
            info["sf_schema"] = 'DW'
            # 'snowflake://<user_login_name>:<password>@<account_identifier>/<database_name>/<schema_name>?warehouse=<warehouse_name>&role=<role_name>'
            self.connection_string = f'snowflake://{info["sf_user"]}:{info["sf_pwd"]}@' \
                                     f'{info["sf_host"]}/{info["sf_db"]}/{info["sf_schema"]}?' \
                                     f'warehouse={info["sf_wh"]}&role={info["sf_role"]}'
        elif dbms_type == "mysql":
            self.connection_string = f'mysql+pymysql://{info["mysql_user"]}:{info["mysql_pwd"]}@' \
                                     f'{info["mysql_host"]}:{info["mysql_port"]}/{info["mysql_db"]}'
            print(self.connection_string)
        elif dbms_type == "postgres":
            self.connection_string = f'postgresql+psycopg2://{info["postgres_user"]}:{info["postgres_pwd"]}@' \
                                     f'{info["postgres_host"]}:{info["postgres_port"]}/{info["postgres_db"]}'
        elif dbms_type == "mssql":
            self.connection_string = f'mssql+pymssql://{info["mssql_user"]}:{info["mssql_pwd"]}@' \
                                     f'{info["mssql_host"]}:{info["mssql_port"]}/{info["mssql_db"]}'
        else:
            raise "UNSUPPORTED DBMS"

        return create_engine(self.connection_string)

    def crawler(self):
        def month_year_iter(start_month, start_year, end_month, end_year):
            ym_start = 12 * start_year + start_month - 1
            ym_end = 12 * end_year + end_month - 1
            for ym in range(ym_start, ym_end):
                y, m = divmod(ym, 12)
                yield y, m + 1
        engine = self.connect_db("snowflake")
        info_arr=[]
        # 201701~current year and month
        for year, month in month_year_iter(1, 2017, int(date.today().strftime("%m"))+1, int(date.today().strftime("%Y"))):
            if month<10:
                month = "0"+str(month)
            url = f"{self.url}&solYear={year}&solMonth={month}"
            print(year, month, url)
            res = requests.get(url=url)
            soup = BeautifulSoup(res.content, 'html.parser')
            items = soup.find_all('item')
            print(items)
            for idx, item in enumerate(items):
                info = {}
                info['dateKind'.lower()] = item.find('dateKind'.lower()) if item.find('dateKind'.lower()) == None else item.find('dateKind'.lower()).get_text()
                info['dateName'.lower()] = item.find('dateName'.lower()) if item.find('dateName'.lower()) == None else item.find('dateName'.lower()).get_text()
                info['isHoliday'.lower()] = item.find('isHoliday'.lower()) if item.find('isHoliday'.lower()) == None else item.find('isHoliday'.lower()).get_text()
                info['locdate'] = item.find('locdate') if item.find('locdate') == None else item.find('locdate').get_text()
                info['seq'] = item.find('seq') if item.find('seq') == None else item.find('seq').get_text()
                info_arr.append(info)
        df = pd.DataFrame(info_arr)
        df = df.replace(np.nan, value="")
        df.rename(columns={'datekind':'HOL_KND_CD'}, inplace=True)
        df.rename(columns={'datename':'HOL_NM'}, inplace=True)
        df.rename(columns={'isholiday':'GOF_HOL_YN'}, inplace=True)
        df.rename(columns={'locdate':'BASE_DD'}, inplace=True)
        df.rename(columns={'seq':'BASE_DD_SEQ'}, inplace=True)
        df['LOAD_DTTM'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        engine.execute(sa_text(f"TRUNCATE TABLE GCWB_WDB.DW.WSTC_HOL;").execution_options(autocommit=True))
        df.to_sql('WSTC_HOL', con=engine, if_exists="append", index=False)

if __name__ == "__main__":
    numOfRows=100
    pdb = RestDeInfo(tablename="RestDeInfo",
                     url_prefix="http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo?",
                     url_parameters=f"numOfRows={numOfRows}&serviceKey={info['serviceKey']}",
                     connection_string=None)
    pdb.crawler()


"""
References
https://stackoverflow.com/questions/42079419/truncate-table-not-working-with-sql-server-sqlalchemy-engine-and-pandas
"""