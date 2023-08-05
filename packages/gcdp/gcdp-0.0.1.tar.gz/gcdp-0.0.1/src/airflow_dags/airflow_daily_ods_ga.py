from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta, date
# from slack_operators import task_fail_slack_alert
from airflow.models.variable import Variable
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.operators.python_operator import PythonOperator
import pandas as pd
import os

from ..gcwb_sql.generate_query import check_duprows, execute_rownum_query
from ..commonlibs.utils import project_path

import pendulum
from datetime import datetime

local_tz = pendulum.timezone('Asia/Seoul')

yesterday = date.today() - timedelta(days=0)
start_day = yesterday.strftime("%Y%m%d")
end_day = yesterday.strftime("%Y%m%d")

default_args = {
    'owner': 'yjjo',
    # 'email': 'gcs.kelly@gmail.com',
    # 'email_on_failure': True,
    # 'email_on_retry': True,
    # 'email_on_success': True,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    # 'on_failure_callback': task_fail_slack_alert,
    'trigger_rule': 'all_success',
}

dag = DAG(
    dag_id='airflow_daily_ods_ga',
    default_args = default_args,
    schedule_interval= '0 1 * * *',
    start_date= datetime(2022,6,18,1,tzinfo=local_tz),
    catchup= False
)

delq_DPN_AFFINITY = f"DELETE FROM GCWB_WDB.ODS.O_GA_DPN_AFFINITY WHERE DATE BETWEEN {start_day} AND {end_day};",
del_DPN_AFFINITY = SnowflakeOperator(
    task_id= 'del_DPN_AFFINITY',
    sql=delq_DPN_AFFINITY,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
DPN_AFFINITY = BashOperator(
    task_id= 'DPN_AFFINITY',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_AFFINITY.py {start_day} {end_day}',
    dag= dag
)


delq_DPN_AGE = f"DELETE FROM GCWB_WDB.ODS.O_GA_DPN_AGE WHERE DATE BETWEEN {start_day} AND {end_day};",
del_DPN_AGE = SnowflakeOperator(
    task_id= 'del_DPN_AGE',
    sql=delq_DPN_AGE,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
DPN_AGE = BashOperator(
    task_id= 'DPN_AGE',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_AGE.py {start_day} {end_day}',
    dag= dag
)


delq_DPN_BEHAVIOR = f"DELETE FROM GCWB_WDB.ODS.O_GA_DPN_BEHAVIOR WHERE DATE BETWEEN {start_day} AND {end_day};",
del_DPN_BEHAVIOR = SnowflakeOperator(
    task_id= 'del_DPN_BEHAVIOR',
    sql=delq_DPN_BEHAVIOR,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
DPN_BEHAVIOR = BashOperator(
    task_id= 'DPN_BEHAVIOR',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_BEHAVIOR.py {start_day} {end_day}',
    dag= dag
)

delq_DPN_CLIENT = f"DELETE FROM GCWB_WDB.ODS.O_GA_DPN_CLIENT WHERE DATE BETWEEN {start_day} AND {end_day};",
del_DPN_CLIENT = SnowflakeOperator(
    task_id= 'del_DPN_CLIENT',
    sql=delq_DPN_CLIENT,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
DPN_CLIENT = BashOperator(
    task_id= 'DPN_CLIENT',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_CLIENT.py {start_day} {end_day}',
    dag= dag
)

delq_DPN_CLIENT_CITY = f"DELETE FROM GCWB_WDB.ODS.O_GA_DPN_CLIENT_CITY WHERE DATE BETWEEN {start_day} AND {end_day};",
del_DPN_CLIENT_CITY = SnowflakeOperator(
    task_id= 'del_DPN_CLIENT_CITY',
    sql=delq_DPN_CLIENT_CITY,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
DPN_CLIENT_CITY = BashOperator(
    task_id= 'DPN_CLIENT_CITY',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_CLIENT_CITY.py {start_day} {end_day}',
    dag= dag
)

delq_DPN_GENDER = f"DELETE FROM GCWB_WDB.ODS.O_GA_DPN_GENDER WHERE DATE BETWEEN {start_day} AND {end_day};",
del_DPN_GENDER = SnowflakeOperator(
    task_id= 'del_DPN_GENDER',
    sql=delq_DPN_GENDER,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
DPN_GENDER = BashOperator(
    task_id= 'DPN_GENDER',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_GENDER.py {start_day} {end_day}',
    dag= dag
)

delq_DPN_GOAL = f"DELETE FROM GCWB_WDB.ODS.O_GA_DPN_GOAL WHERE DATE BETWEEN {start_day} AND {end_day};",
del_DPN_GOAL = SnowflakeOperator(
    task_id= 'del_DPN_GOAL',
    sql=delq_DPN_GOAL,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
DPN_GOAL = BashOperator(
    task_id= 'DPN_GOAL',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_GOAL.py {start_day} {end_day}',
    dag= dag
)

delq_DPN_ORDER = f"DELETE FROM GCWB_WDB.ODS.O_GA_DPN_ORDER WHERE DATE BETWEEN {start_day} AND {end_day};",
del_DPN_ORDER = SnowflakeOperator(
    task_id= 'del_DPN_ORDER',
    sql=delq_DPN_ORDER,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
DPN_ORDER = BashOperator(
    task_id= 'DPN_ORDER',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_ORDER.py {start_day} {end_day}',
    dag= dag
)

delq_DPN_ORDER_PRODUCT = f"DELETE FROM GCWB_WDB.ODS.O_GA_DPN_ORDER_PRODUCT WHERE DATE BETWEEN {start_day} AND {end_day};",
del_DPN_ORDER_PRODUCT = SnowflakeOperator(
    task_id= 'del_DPN_ORDER_PRODUCT',
    sql=delq_DPN_ORDER_PRODUCT,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
DPN_ORDER_PRODUCT = BashOperator(
    task_id= 'DPN_ORDER_PRODUCT',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_ORDER_PRODUCT.py {start_day} {end_day}',
    dag= dag
)

delq_DPN_PAGE = f"DELETE FROM GCWB_WDB.ODS.O_GA_DPN_PAGE WHERE DATE BETWEEN {start_day} AND {end_day};",
del_DPN_PAGE = SnowflakeOperator(
    task_id= 'del_DPN_PAGE',
    sql=delq_DPN_PAGE,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
DPN_PAGE = BashOperator(
    task_id= 'DPN_PAGE',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_PAGE.py {start_day} {end_day}',
    dag= dag
)

delq_DPN_PRODUCT = f"DELETE FROM GCWB_WDB.ODS.O_GA_DPN_PRODUCT WHERE DATE BETWEEN {start_day} AND {end_day};",
del_DPN_PRODUCT = SnowflakeOperator(
    task_id= 'del_DPN_PRODUCT',
    sql=delq_DPN_PRODUCT,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
DPN_PRODUCT = BashOperator(
    task_id= 'DPN_PRODUCT',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_PRODUCT.py {start_day} {end_day}',
    dag= dag
)

delq_DPN_SEARCH = f"DELETE FROM GCWB_WDB.ODS.O_GA_DPN_SEARCH WHERE DATE BETWEEN {start_day} AND {end_day};",
del_DPN_SEARCH = SnowflakeOperator(
    task_id= 'del_DPN_SEARCH',
    sql=delq_DPN_SEARCH,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
DPN_SEARCH = BashOperator(
    task_id= 'DPN_SEARCH',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_SEARCH.py {start_day} {end_day}',
    dag= dag
)

delq_DPN_SOCIAL_MEDIUM = f"DELETE FROM GCWB_WDB.ODS.O_GA_DPN_SOCIAL_MEDIUM WHERE DATE BETWEEN {start_day} AND {end_day};",
del_DPN_SOCIAL_MEDIUM = SnowflakeOperator(
    task_id= 'del_DPN_SOCIAL_MEDIUM',
    sql=delq_DPN_SOCIAL_MEDIUM,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
DPN_SOCIAL_MEDIUM = BashOperator(
    task_id= 'DPN_SOCIAL_MEDIUM',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_SOCIAL_MEDIUM.py {start_day} {end_day}',
    dag= dag
)
delq_PNT_AFFINITY = f"DELETE FROM GCWB_WDB.ODS.O_GA_PNT_AFFINITY WHERE DATE BETWEEN {start_day} AND {end_day};",
del_PNT_AFFINITY = SnowflakeOperator(
    task_id= 'del_PNT_AFFINITY',
    sql=delq_PNT_AFFINITY,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
PNT_AFFINITY = BashOperator(
    task_id= 'PNT_AFFINITY',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_AFFINITY.py {start_day} {end_day}',
    dag= dag
)
delq_PNT_AGE = f"DELETE FROM GCWB_WDB.ODS.O_GA_PNT_AGE WHERE DATE BETWEEN {start_day} AND {end_day};",
del_PNT_AGE = SnowflakeOperator(
    task_id= 'del_PNT_AGE',
    sql=delq_PNT_AGE,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
PNT_AGE = BashOperator(
    task_id= 'PNT_AGE',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_AGE.py {start_day} {end_day}',
    dag= dag
)
delq_PNT_BEHAVIOR = f"DELETE FROM GCWB_WDB.ODS.O_GA_PNT_BEHAVIOR WHERE DATE BETWEEN {start_day} AND {end_day};",
del_PNT_BEHAVIOR = SnowflakeOperator(
    task_id= 'del_PNT_BEHAVIOR',
    sql=delq_PNT_BEHAVIOR,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
PNT_BEHAVIOR = BashOperator(
    task_id= 'PNT_BEHAVIOR',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_BEHAVIOR.py {start_day} {end_day}',
    dag= dag
)
delq_PNT_CLIENT = f"DELETE FROM GCWB_WDB.ODS.O_GA_PNT_CLIENT WHERE DATE BETWEEN {start_day} AND {end_day};",
del_PNT_CLIENT = SnowflakeOperator(
    task_id= 'del_PNT_CLIENT',
    sql=delq_PNT_CLIENT,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
PNT_CLIENT = BashOperator(
    task_id= 'PNT_CLIENT',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_CLIENT.py {start_day} {end_day}',
    dag= dag
)
delq_PNT_CLIENT_CITY = f"DELETE FROM GCWB_WDB.ODS.O_GA_PNT_CLIENT_CITY WHERE DATE BETWEEN {start_day} AND {end_day};",
del_PNT_CLIENT_CITY = SnowflakeOperator(
    task_id= 'del_PNT_CLIENT_CITY',
    sql=delq_PNT_CLIENT_CITY,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
PNT_CLIENT_CITY = BashOperator(
    task_id= 'PNT_CLIENT_CITY',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_CLIENT_CITY.py {start_day} {end_day}',
    dag= dag
)
delq_PNT_GENDER = f"DELETE FROM GCWB_WDB.ODS.O_GA_PNT_GENDER WHERE DATE BETWEEN {start_day} AND {end_day};",
del_PNT_GENDER = SnowflakeOperator(
    task_id= 'del_PNT_GENDER',
    sql=delq_PNT_GENDER,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
PNT_GENDER = BashOperator(
    task_id= 'PNT_GENDER',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_GENDER.py {start_day} {end_day}',
    dag= dag
)

delq_PNT_GOAL = f"DELETE FROM GCWB_WDB.ODS.O_GA_PNT_GOAL WHERE DATE BETWEEN {start_day} AND {end_day};",
del_PNT_GOAL = SnowflakeOperator(
    task_id= 'del_PNT_GOAL',
    sql=delq_PNT_GOAL,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
PNT_GOAL = BashOperator(
    task_id= 'PNT_GOAL',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_GOAL.py {start_day} {end_day}',
    dag= dag
)

delq_PNT_ORDER = f"DELETE FROM GCWB_WDB.ODS.O_GA_PNT_ORDER WHERE DATE BETWEEN {start_day} AND {end_day};",
del_PNT_ORDER = SnowflakeOperator(
    task_id= 'del_PNT_ORDER',
    sql=delq_PNT_ORDER,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
PNT_ORDER = BashOperator(
    task_id= 'PNT_ORDER',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_ORDER.py {start_day} {end_day}',
    dag= dag
)

delq_PNT_ORDER_PRODUCT = f"DELETE FROM GCWB_WDB.ODS.O_GA_PNT_ORDER_PRODUCT WHERE DATE BETWEEN {start_day} AND {end_day};",
del_PNT_ORDER_PRODUCT = SnowflakeOperator(
    task_id= 'del_PNT_ORDER_PRODUCT',
    sql=delq_PNT_ORDER_PRODUCT,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
PNT_ORDER_PRODUCT = BashOperator(
    task_id= 'PNT_ORDER_PRODUCT',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_ORDER_PRODUCT.py {start_day} {end_day}',
    dag= dag
)

delq_PNT_PAGE = f"DELETE FROM GCWB_WDB.ODS.O_GA_PNT_PAGE WHERE DATE BETWEEN {start_day} AND {end_day};",
del_PNT_PAGE = SnowflakeOperator(
    task_id= 'del_PNT_PAGE',
    sql=delq_PNT_PAGE,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
PNT_PAGE = BashOperator(
    task_id= 'PNT_PAGE',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_PAGE.py {start_day} {end_day}',
    dag= dag
)

delq_PNT_PRODUCT = f"DELETE FROM GCWB_WDB.ODS.O_GA_PNT_PRODUCT WHERE DATE BETWEEN {start_day} AND {end_day};",
del_PNT_PRODUCT = SnowflakeOperator(
    task_id= 'del_PNT_PRODUCT',
    sql=delq_PNT_PRODUCT,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
PNT_PRODUCT = BashOperator(
    task_id= 'PNT_PRODUCT',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_PRODUCT.py {start_day} {end_day}',
    dag= dag
)

delq_PNT_SEARCH = f"DELETE FROM GCWB_WDB.ODS.O_GA_PNT_SEARCH WHERE DATE BETWEEN {start_day} AND {end_day};",
del_PNT_SEARCH = SnowflakeOperator(
    task_id= 'del_PNT_SEARCH',
    sql=delq_PNT_SEARCH,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
PNT_SEARCH = BashOperator(
    task_id= 'PNT_SEARCH',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_SEARCH.py {start_day} {end_day}',
    dag= dag
)
delq_PNT_SOCIAL_MEDIUM = f"DELETE FROM GCWB_WDB.ODS.O_GA_PNT_SOCIAL_MEDIUM WHERE DATE BETWEEN {start_day} AND {end_day};",
del_PNT_SOCIAL_MEDIUM = SnowflakeOperator(
    task_id= 'del_PNT_SOCIAL_MEDIUM',
    sql=delq_PNT_SOCIAL_MEDIUM,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
PNT_SOCIAL_MEDIUM = BashOperator(
    task_id= 'PNT_SOCIAL_MEDIUM',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_SOCIAL_MEDIUM.py {start_day} {end_day}',
    dag= dag
)

def check(**kwargs):
    system_name = kwargs['system_name']
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

check_ga_daily = PythonOperator(task_id="check_ga_daily", python_callable=check, op_kwargs={'system_name':'ga'})


del_DPN_AFFINITY >> DPN_AFFINITY >> \
del_DPN_AGE >> DPN_AGE >> \
del_DPN_BEHAVIOR >> DPN_BEHAVIOR >> \
del_DPN_CLIENT >> DPN_CLIENT >> \
del_DPN_CLIENT_CITY >> DPN_CLIENT_CITY >> \
del_DPN_GENDER >> DPN_GENDER >> \
del_DPN_GOAL >> DPN_GOAL >> \
del_DPN_ORDER >> DPN_ORDER >> \
del_DPN_ORDER_PRODUCT >> DPN_ORDER_PRODUCT >> \
del_DPN_PAGE >> DPN_PAGE >> \
del_DPN_PRODUCT >> DPN_PRODUCT >> \
del_DPN_SEARCH >> DPN_SEARCH >> \
del_DPN_SOCIAL_MEDIUM >> DPN_SOCIAL_MEDIUM >> \
del_PNT_AFFINITY >> PNT_AFFINITY >> \
del_PNT_AGE >> PNT_AGE >> \
del_PNT_BEHAVIOR >> PNT_BEHAVIOR >> \
del_PNT_CLIENT >> PNT_CLIENT >> \
del_PNT_CLIENT_CITY >> PNT_CLIENT_CITY >> \
del_PNT_GENDER >> PNT_GENDER >> \
del_PNT_GOAL >> PNT_GOAL >> \
del_PNT_ORDER >> PNT_ORDER >> \
del_PNT_ORDER_PRODUCT >> PNT_ORDER_PRODUCT >> \
del_PNT_PAGE >> PNT_PAGE >> \
del_PNT_PRODUCT >> PNT_PRODUCT >> \
del_PNT_SEARCH >> PNT_SEARCH >> \
del_PNT_SOCIAL_MEDIUM >> PNT_SOCIAL_MEDIUM >> check_ga_daily