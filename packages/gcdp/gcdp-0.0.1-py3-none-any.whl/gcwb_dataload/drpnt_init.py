import pandas as pd
from sqlalchemy import create_engine
import datetime
import os
import snowflake.connector
import json
import boto3
from datetime import date
from commonlibs.utils import set_downloads_folder, get_downloads_folder, json_contents, project_path
from ..gcwb_sql.generate_query import execute_truncate_query, execute_insert_query
from ..gcwb_s3.upload_objects import upload_files_to_s3


if __name__ == "__main__":
    system_name = "dpn"
    set_downloads_folder(system_name)
    file_path = get_downloads_folder(system_name)
    print(f'{json_contents["drpnt_user"]}, {json_contents["drpnt_password"]}, {json_contents["drpnt_host"]}, {json_contents["drpnt_port"]},'
          f'{json_contents["drpnt_database"]}, {json_contents["drpnt_ssl_cert"]}')

    conn = create_engine(f'mysql+pymysql://{json_contents["drpnt_user"]}:{json_contents["drpnt_password"]}'
                         f'@{json_contents["drpnt_host"]}/{json_contents["drpnt_database"]}?ssl_ca={json_contents["drpnt_ssl_ca"]}')

    df = pd.read_excel(f"{project_path}/gcwb_dataload/code/dpn_table_list.xlsx", index_col=False)
    table_list = df['table_list']
    print(table_list)
    for table_name in table_list:
        print(f"{table_name} 초기 적재")
        tbl = pd.read_sql_query(f"SELECT * FROM {json_contents['drpnt_database']}.{table_name}", con=conn)
        tbl.to_csv(f'{os.path.join(file_path, table_name+".csv")}', index=False, header=True, encoding='utf-8-sig')
        upload_files_to_s3(upload_date=datetime.date.today().strftime("%y%m%d"), system_name=system_name, file=f"{table_name}.csv")
        execute_truncate_query(system_name=system_name, table_name=table_name)
        execute_insert_query(system_name=system_name, table_name=table_name, data_date=datetime.date.today().strftime("%y%m%d"))

    table_name = "es_order"
    tbl = pd.read_sql_query(f"SELECT * FROM {json_contents['drpnt_database']}.{table_name}", con=conn)
    # 첫번째 row는 쓰레기 데이터라 제거 하기 위해 아래 코드 필요
    tbl = tbl.iloc[1: , :]
    tbl.to_csv(f'{os.path.join(file_path, table_name+".csv")}', index=False, header=True, encoding='utf-8-sig')
    upload_files_to_s3(upload_date=datetime.date.today().strftime("%y%m%d"), system_name=system_name, file=f"{table_name}.csv")
    execute_truncate_query(system_name=system_name, table_name=table_name)
    execute_insert_query(system_name=system_name, table_name=table_name, data_date=datetime.date.today().strftime("%y%m%d"))


