import snowflake.connector
from sqlalchemy import create_engine
from commonlibs.utils import json_contents, project_path
import pandas as pd


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
    # print(snow_rownum)


    mysql_con = create_engine(f'mysql+pymysql://{json_contents["drpnt_user"]}:{json_contents["drpnt_password"]}'
                              f'@{json_contents["drpnt_host"]}/{json_contents["drpnt_database"]}?ssl_ca={json_contents["drpnt_ssl_ca"]}')
    mysql_con = mysql_con.connect()
    mysql_rownum = mysql_con.execute(f"select count(*) from  {json_contents['drpnt_database']}.{table_name};").fetchone()[0]
    # print(mysql_rownum)
    if mysql_rownum == snow_rownum:
        # print(f"VALIDATE::snowflake-table_name:O_{system_name}_{table_name}-{snow_rownum} == mysql-table_name:{table_name}-{mysql_rownum}")
        return True
    else:
        print(f"UNVALIDATE::snowflake-table_name:O_{system_name}_{table_name}-{snow_rownum} != mysql-table_name:{table_name}-{mysql_rownum}")
        return False

if __name__ == "__main__":
    df = pd.read_excel(f"{project_path}/crawling/code/dpn_table_list.xlsx", index_col=False)
    table_list = df['table_list']
    for table_name in table_list:
        valiedate_data(table_name, system_name="dpn")