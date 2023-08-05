
from commonlibs.utils import json_contents, project_path, get_downloads_folder
import pandas as pd
import snowflake.connector
import json
import os
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

# def execute_insert_query_pnt(system_name, table_name, data_date):
#     """
#     generate insert query
#     table에 데이터를 넣는 방법이 copy into stmt와 insert into select stmt이다.
#     show columns in table {table_name}; 쿼리를 통해 컬럼들을 추출하고
#     컬럼수만큼 string_source concatnate
#     컬럼스트링도 for문 돌면서 concatnate
#     string_source = f"T.${i},"
#     column_str = column_str + ", " + row[2]
#     table_str = table_str + string_source
#     :param system_name, table_name:
#     :return:
#     """
#     conn = snowflake.connector.connect(
#         user=json_contents['sf_user'],
#         password=json_contents['sf_pwd'],
#         account=json_contents['sf_host'],
#         warehouse=json_contents['sf_wh'],
#         database=json_contents['sf_db'],
#         schema=json_contents['sf_schema'],
#         cache_column_metadata=True
#     )
#
#     cur = conn.cursor()
#     print(system_name)
#     query = f"show columns in table {json_contents['sf_db']}.{json_contents['sf_schema']}.O_{system_name}_{table_name};"
#     # print(query)
#     rows = cur.execute(query)
#     i = 0
#     table_str, column_str = "", ""
#     for row in rows:
#         i = i + 1
#         all_type = json.loads(row[3])
#         # print(all_type["type"])
#         # print(row)
#         string_source = f"T.${i},"
#         if (all_type["type"] == "VARIANT"):
#             string_source = f"parse_json({string_source})".replace(",", "")+","
#         if i==1 and system_name=="pnt":
#             if table_name != "es_couponOfflineCode":
#                 string_source = f'replace({string_source}'+ '\'\"\')'+'::number'+","
#             else:
#                 string_source = f'replace({string_source}'+ '\'\"\')'+","
#         column_str = column_str + ", " + row[2]
#         table_str = table_str + string_source
#         # print(column_str)
#     # column_str은 끝의 쉼표와 띄어쓰기, table_str은 끝의 쉼표만 제거해야 해서 -2, -1
#     column_str = column_str[2:]
#     table_str = table_str[:-1]
#     # print(f"table_str = {table_str}")
#     # print(f"column_str = {column_str}")
#     result = f"INSERT INTO {json_contents['sf_db']}.{json_contents['sf_schema']}.O_{system_name.upper()}_{table_name}({column_str}) SELECT {table_str} from @GCWB/{data_date}/{system_name}/{table_name}.csv (FILE_FORMAT=>'O_{system_name}_{table_name}') as T;".replace(", from", " from")
#     print(f"execute query of snowflake: {result}")
#     cur = conn.cursor()
#
#     cur.execute(result)

def get_insert_query(system_name, table_name, data_date):
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
    # df = df.iloc[:-1, :]
    print(df.index.values)

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

def execute_truncate_query(system_name, table_name):
    conn = snowflake.connector.connect(
        user=json_contents['sf_user'],
        password=json_contents['sf_pwd'],
        account=json_contents['sf_host'],
        warehouse=json_contents['sf_wh'],
        database=json_contents['sf_db'],
        schema=json_contents['sf_schema']
    )

    cur = conn.cursor()

    query = f"truncate table {json_contents['sf_db']}.{json_contents['sf_schema']}.O_{system_name}_{table_name};"
    print(f"Execute query of snowflake: {query}")
    rs = cur.execute(query)
    return rs


def generate_truncate_query():
    conn = snowflake.connector.connect(
        user=json_contents['sf_user'],
        password=json_contents['sf_pwd'],
        account=json_contents['sf_host'],
        warehouse=json_contents['sf_wh'],
        database=json_contents['sf_db'],
        schema=json_contents['sf_schema']
    )

    cur = conn.cursor()

    df = pd.read_excel(f"{project_path}/crawling/code/dpn_table_list.xlsx", index_col=False)
    table_list = df['table_list']
    [cur.execute(f"truncate o_dpn_{table_name};") for table_name in table_list]

    df = pd.read_excel(f"{project_path}/crawling/code/pnt_table_list.xlsx", index_col=False)
    table_list = df['table_list']
    [cur.execute(f"truncate o_pnt_{table_name};") for table_name in table_list]
    # for table_name in table_list:
    #     query = f"truncate o_pnt_{table_name};"
    #     # print(query)
    #     rs = cur.execute(query)

def execute_delete_query_ga(system_name, table_name):
    conn = snowflake.connector.connect(
        user=json_contents['sf_user'],
        password=json_contents['sf_pwd'],
        account=json_contents['sf_host'],
        warehouse=json_contents['sf_wh'],
        database=json_contents['sf_db'],
        schema=json_contents['sf_schema']
    )
    df = pd.read_csv(os.path.join(get_downloads_folder(system_name), f"{table_name}.csv"), encoding='utf-8')
    stmt = f"DELETE FROM GCWB_WDB.ODS.O_{system_name}_{table_name} WHERE DATE BETWEEN {df['DATE'].min()} AND {df['DATE'].max()};"
    print(f"stmt : {stmt}")
    cur = conn.cursor()
    cur.execute(stmt)

def execute_delete_query(delete_query):
    conn = snowflake.connector.connect(
        user=json_contents['sf_user'],
        password=json_contents['sf_pwd'],
        account=json_contents['sf_host'],
        warehouse=json_contents['sf_wh'],
        database=json_contents['sf_db'],
        schema=json_contents['sf_schema']
    )
    print(f"stmt : {delete_query}")
    cur = conn.cursor()
    cur.execute(delete_query)

def execute_rownum_query(system_name, table_name):
    conn = snowflake.connector.connect(
        user=json_contents['sf_user'],
        password=json_contents['sf_pwd'],
        account=json_contents['sf_host'],
        warehouse=json_contents['sf_wh'],
        database=json_contents['sf_db'],
        schema=json_contents['sf_schema']
    )
    rownum_stmt = f"SELECT COUNT(*) FROM GCWB_WDB.ODS.O_{system_name}_{table_name};"
    # print(f"{table_name} rownum : {rownum_stmt}")
    cur = conn.cursor()
    rownum = cur.execute(rownum_stmt).fetchone()
    print(f"{table_name}:\t{rownum[0]} rows")
    return rownum[0]

def check_duprows(system_name, table_name):
    conn = snowflake.connector.connect(
        user=json_contents['sf_user'],
        password=json_contents['sf_pwd'],
        account=json_contents['sf_host'],
        warehouse=json_contents['sf_wh'],
        database=json_contents['sf_db'],
        schema=json_contents['sf_schema']
    )

    df = pd.read_sql_query(
        sql=f"show columns in table {json_contents['sf_db']}.{json_contents['sf_schema']}.O_{system_name}_{table_name};",
        con=conn)
    select_string = ", ".join([df['column_name'][i] for _, i in enumerate(df.index.values.tolist()) if(df['null?'][i]=="NOT_NULL")])
    if(select_string == ""):
        print(f"{table_name} doesn't exist primary key")
        return f"{table_name} doesn't exist primary key"
    # print(select_string)
    val_duprows_stmt = f"SELECT {select_string}, COUNT(1) FROM GCWB_WDB.ODS.O_{system_name}_{table_name} GROUP BY {select_string} HAVING COUNT(1) >1;"
    print(val_duprows_stmt)
    rows = conn.cursor().execute(val_duprows_stmt).fetchall()
    # print(rows)
    if not rows:
        pass
        # print(f"{table_name} is not duplicated")
    else:
        print(f"ERROR:: {table_name} IS DUPLICATED")
        print(rows[0])

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        # for system_name in ["ga","pnt", "dpn"]:
        for system_name in ["dpn"]:
            code_folder = os.path.join(os.path.join(os.path.join(project_path, "gcwb_dataload"), "code"),
                                       f"{system_name}_table_list.xlsx")
            df = pd.read_excel(f"{code_folder}", index_col=False)
            table_list = list(df["table_list"])
            if (system_name == "dpn"):
                table_list.remove("t_product_tag")
                table_list.remove("t_order_status_log")
                table_list.remove("t_point_use")
            total_rows = 0
            for table_name in table_list:
                # print(table_name)
                check_duprows(f"{system_name}", table_name)
                total_rows = total_rows + execute_rownum_query(system_name=system_name, table_name=table_name)
            print(f"system_name: {system_name}  total_rows: {total_rows} rows")

    else:
        system_name = sys.argv[1]
        code_folder = os.path.join(os.path.join(os.path.join(project_path, "gcwb_dataload"), "code"),
                                   f"{system_name}_table_list.xlsx")
        df = pd.read_excel(f"{code_folder}", index_col=False)
        table_list = list(df["table_list"])
        if (system_name == "dpn"):
            table_list.remove("t_product_tag")
            table_list.remove("t_order_status_log")
            table_list.remove("t_point_use")
        total_rows = 0
        for table_name in table_list:
            # print(table_name)
            check_duprows(f"{system_name}", table_name)
            total_rows = total_rows + execute_rownum_query(system_name=system_name, table_name=table_name)
        print(f"system_name: {system_name}  total_rows: {total_rows} rows")

        print(" ================================================================================================== ")
