import snowflake.connector
from commonlibs.utils import json_contents, project_path, get_downloads_folder
import pandas as pd
import os

def valiedate_data(table_name, system_name):
    """
    매핑되는 snowflake와 mysql의 테이블의 row갯수가 같은지 validate하는 함수
    :param table_name:
    :param system_name:
    :return:
    """
    snow_con = snowflake.connector.connect(
        user=json_contents['sf_user'],
        password=json_contents['sf_password'],
        account=json_contents['sf_account'],
        warehouse=json_contents['sf_warehouse'],
        database=json_contents['sf_database'],
        schema=json_contents['sf_schema'],
        cache_column_metadata=True
    )

    cur = snow_con.cursor()


    snow_rownum = cur.execute(f"select count(*) from {json_contents['sf_database']}.{json_contents['sf_schema']}.O_{system_name}_{table_name};").fetchone()[0]
    #
    print(f"snowflake 데이터 length: {snow_rownum}")
    csv_filepath = f"{os.path.join(get_downloads_folder(system_name), table_name+'.csv')}"
    # print(csv_filepath)
    df = pd.read_csv(csv_filepath, encoding='utf-16')
    print(f"csv 데이터 length: {len(df.index)}")

    if snow_rownum == len(df.index):
        print(f"VALIDATE::snowflake-table_name:O_{system_name}_{table_name}-{snow_rownum} == pntshop-table_name:{table_name}-{len(df.index)}")
        return True
    else:
        print(f"UNVALIDATE::snowflake-table_name:O_{system_name}_{table_name}-{snow_rownum} != pntshop-table_name:{table_name}-{len(df.index)}")
        return False

if __name__ == "__main__":
    df = pd.read_excel(f"{project_path}/crawling/code/pnt_table_list.xlsx", index_col=False)
    table_list = df['table_list']
    for table_name in table_list:
        valiedate_data(table_name, system_name="pnt")