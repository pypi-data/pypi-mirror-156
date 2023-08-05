# 현재달의 전달것을 like절로 가져와 넣는다.
import pandas as pd
from commonlibs.utils import get_downloads_folder, set_downloads_folder, json_contents, project_path, yesterday
from sqlalchemy import create_engine
from datetime import date, timedelta, datetime
import os
import json
import snowflake.connector
from pntshop_crawler import godomall_crawler, downloads_done, modify_csv
import datetime
import sys
from ..gcwb_sql.generate_query import execute_rownum_query, check_duprows, execute_delete_query
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

def pnt_daily(start_day, end_day):
    df = pd.read_excel(f'{os.path.join(os.path.join(os.path.join(project_path, "gcwb_dataload"), "code"), "pnt_table_list.xlsx")}')
    table_list = list(df['table_list'])
    # print(table_list)
    table_list.remove("es_logOrder")
    # print(table_list)
    conn = snowflake.connector.connect(
        user=json_contents['sf_user'],
        password=json_contents['sf_pwd'],
        account=json_contents['sf_host'],
        warehouse=json_contents['sf_wh'],
        database=json_contents['sf_db'],
        schema=json_contents['sf_schema'],
        cache_column_metadata=True
    )

    print(start_day, end_day)
    system_name = "pnt"
    set_downloads_folder(system_name)
    file_path = get_downloads_folder(system_name)

    print(table_list)
    # for table_name in table_list:
    #     print(table_name)
    #     df = pd.read_sql_query(
    #         sql=f"show columns in table {json_contents['sf_db']}.{json_contents['sf_schema']}.O_{system_name}_{table_name};",
    #         con=conn)
    #     df = df.iloc[:-1, :]
    #     # 마지막 load_dttm은 제외한다
    #     column_string = ", ".join(df['column_name'].tolist())
    #     print(f"column_string: {column_string}")
    #     column_string = column_string+", LOAD_DTTM"
    #     print(f"column_string: {column_string}")
    #     REGDT_index = column_string.split(", ").index("REGDT")
    #     print(column_string.split(", ").index("REGDT"))
    #     MODDT_index = column_string.split(", ").index("MODDT")
    #     print(column_string.split(", ").index("MODDT"))
    #
    #     select_string = ", ".join(
    #         [f"${i + 1}" if json.loads(df["data_type"][i])['type'] != "VARIANT" else "parse_json(" + f"${i + 1}" + ")"
    #          for _, i in enumerate(df.index.values.tolist())])
    #     print(f"select_string: {select_string}")
    #     select_string = select_string+", CURRENT_TIMESTAMP()::timestamp_ntz"
    #     print(f"select_string: {select_string}")
    #     # snowflake(target)에서 table이 마지막 컬럼 load_dttm인 것을 제외하고 난 나머지의 컬럼갯수 만큼 csv파일에서 select하여 target과 source의 column갯수를 맞춰 insert한다.
    #     element_type = [json.loads(df["data_type"][i])['type'] for _, i in enumerate(df.index.values.tolist())]
    #     # df_delete = pd.read_csv(os.path.join(file_path, table_name+".csv"))
    #     # df_delete = df_delete[df_delete['modDt']]
    #
    #     df_key = pd.read_sql_query(
    #         sql=f"show columns in table {json_contents['sf_db']}.{json_contents['sf_schema']}.O_{system_name}_{table_name};",
    #         con=conn)
    #     delete_column = ", ".join([df_key['column_name'][i] for _, i in enumerate(df_key.index.values.tolist()) if
    #                                (df_key['null?'][i] == "NOT_NULL")])
    #     delete_query = f"""
    #     SELECT {select_string}
    #     from @GCWB/{system_name}/{date.today().strftime("%y%m%d")}/{table_name}.csv (FILE_FORMAT=>'O_{system_name}_{table_name}')
    #      WHERE ${REGDT_index+1} BETWEEN '{start_day[0:4] + '-' + start_day[4:6] + '-' + start_day[6:8]}' AND '{end_day[0:4] + '-' + end_day[4:6] + '-' + end_day[6:8]}' or ${MODDT_index+1} BETWEEN '{start_day[0:4] + '-' + start_day[4:6] + '-' + start_day[6:8]}' AND '{end_day[0:4] + '-' + end_day[4:6] + '-' + end_day[6:8]}'
    #     """
    #     delete_df = pd.read_sql_query(
    #         f"{delete_query}"
    #         , con=conn)
    #     print(delete_df['$1'])
    #     for key_value in delete_df['$1']:
    #         delete_query = f"DELETE FROM GCWB_WDB.ODS.O_{system_name}_{table_name} WHERE {delete_column}='{key_value}'"
    #         execute_delete_query(delete_query=delete_query)
    #     # stmt = f"TRUNCATE TABLE {json_contents['sf_db']}.{json_contents['sf_schema']}.O_{system_name}_{table_name};"
    #     # cur = conn.cursor()
    #     # cur.execute(stmt)
    #     stmt = f"""
    #     INSERT INTO {json_contents['sf_db']}.{json_contents['sf_schema']}.O_{system_name}_{table_name} ({column_string}) SELECT {select_string}
    #     from @GCWB/{system_name}/{date.today().strftime("%y%m%d")}/{table_name}.csv (FILE_FORMAT=>'O_{system_name}_{table_name}')
    #      WHERE ${REGDT_index+1} BETWEEN '{start_day[0:4] + '-' + start_day[4:6] + '-' + start_day[6:8]}' AND '{end_day[0:4] + '-' + end_day[4:6] + '-' + end_day[6:8]}' or ${MODDT_index+1} BETWEEN '{start_day[0:4] + '-' + start_day[4:6] + '-' + start_day[6:8]}' AND '{end_day[0:4] + '-' + end_day[4:6] + '-' + end_day[6:8]}'
    #     """
    #     print(f"{stmt}")
    #     cur = conn.cursor()
    #     cur.execute(stmt)

    # es_logorder만 regdt존재
    table_name = "es_logOrder"
    df = pd.read_sql_query(
        sql=f"show columns in table {json_contents['sf_db']}.{json_contents['sf_schema']}.O_{system_name}_{table_name};",
        con=conn)
    df = df.iloc[:-1, :]
    # 마지막 load_dttm은 제외한다
    column_string = ", ".join(df['column_name'].tolist())
    print(f"column_string: {column_string}")
    column_string = column_string+", LOAD_DTTM"
    print(f"column_string: {column_string}")
    REGDT_index = column_string.split(", ").index("REGDT")
    print(column_string.split(", ").index("REGDT"))

    select_string = ", ".join(
        [f"${i + 1}" if json.loads(df["data_type"][i])['type'] != "VARIANT" else "parse_json(" + f"${i + 1}" + ")"
         for _, i in enumerate(df.index.values.tolist())])
    print(f"select_string: {select_string}")
    select_string = select_string+", CURRENT_TIMESTAMP()::timestamp_ntz"
    print(f"select_string: {select_string}")
    # snowflake(target)에서 table이 마지막 컬럼 load_dttm인 것을 제외하고 난 나머지의 컬럼갯수 만큼 csv파일에서 select하여 target과 source의 column갯수를 맞춰 insert한다.
    element_type = [json.loads(df["data_type"][i])['type'] for _, i in enumerate(df.index.values.tolist())]

    df_key = pd.read_sql_query(
        sql=f"show columns in table {json_contents['sf_db']}.{json_contents['sf_schema']}.O_{system_name}_{table_name};",
        con=conn)
    delete_column = ", ".join([df_key['column_name'][i] for _, i in enumerate(df_key.index.values.tolist()) if
                               (df_key['null?'][i] == "NOT_NULL")])
    delete_query = f"""
    SELECT {select_string}
    from @GCWB/{system_name}/{date.today().strftime("%y%m%d")}/{table_name}.csv (FILE_FORMAT=>'O_{system_name}_{table_name}')
    WHERE ${REGDT_index + 1} BETWEEN '{start_day[0:4] + '-' + start_day[4:6] + '-' + start_day[6:8]}' AND '{end_day[0:4] + '-' + end_day[4:6] + '-' + end_day[6:8]}'
    """
    delete_df = pd.read_sql_query(
        f"{delete_query}"
        , con=conn)
    print(delete_df['$1'])
    for key_value in delete_df['$1']:
        delete_query = f"DELETE FROM GCWB_WDB.ODS.O_{system_name}_{table_name} WHERE {delete_column}='{key_value}'"
        execute_delete_query(delete_query=delete_query)
    stmt = f"""
    INSERT INTO {json_contents['sf_db']}.{json_contents['sf_schema']}.O_{system_name}_{table_name} ({column_string}) SELECT {select_string}
    from @GCWB/{system_name}/{date.today().strftime("%y%m%d")}/{table_name}.csv (FILE_FORMAT=>'O_{system_name}_{table_name}')
    WHERE ${REGDT_index+1} BETWEEN '{start_day[0:4] + '-' + start_day[4:6] + '-' + start_day[6:8]}' AND '{end_day[0:4] + '-' + end_day[4:6] + '-' + end_day[6:8]}'
    """
    print(f"{stmt}")
    cur = conn.cursor()
    cur.execute(stmt)

def main():
    system_name = "pnt"
    code_folder = os.path.join(os.path.join(os.path.join(project_path, "gcwb_dataload"), "code"), f"{system_name}_table_list.xlsx")
    df = pd.read_excel(f"{code_folder}", index_col=False)
    table_list = df["table_list"]
    total_rows = 0

    for table_name in table_list:
        check_duprows(table_name=table_name, system_name=system_name)
        total_rows = total_rows + execute_rownum_query(system_name=system_name, table_name=table_name)
    print(total_rows)

    # 파라미터가 없을때 즉, yesterday만 가져올때, daily배치
    if len(sys.argv) == 1:
        print(len(sys.argv) == 1)
        today = date.today() - timedelta(days=0)
        start_day = yesterday
        end_day = today
        pnt_daily(start_day=start_day.strftime("%Y%m%d"),
                  end_day=end_day.strftime("%Y%m%d"))
    # 파라미터가 있을때 즉, date를 range로 넣어서 실행할때
    else:
        print("else")
        start_day = sys.argv[1]
        end_day = sys.argv[2]
        pnt_daily(start_day=datetime.date(int(start_day.split("-")[0]), int(start_day.split("-")[1]),
                                          int(start_day.split("-")[2])).strftime("%Y%m%d"),
                  end_day=datetime.date(int(end_day.split("-")[0]), int(end_day.split("-")[1]),
                                        int(end_day.split("-")[2]) + 1).strftime("%Y%m%d"))

    total_rows = 0
    for table_name in table_list:
        total_rows = total_rows + execute_rownum_query(system_name=system_name, table_name=table_name)
        check_duprows(table_name=table_name, system_name=system_name)
    print(total_rows)

if __name__ == "__main__":
    main()