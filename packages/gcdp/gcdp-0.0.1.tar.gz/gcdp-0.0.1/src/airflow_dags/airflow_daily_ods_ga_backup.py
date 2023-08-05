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
from commonlibs.utils import project_path

import pendulum
from datetime import datetime

local_tz = pendulum.timezone('Asia/Seoul')
#
# yesterday = date.today() - timedelta(days=0)
# start_day = yesterday.strftime("%Y%m%d")
# end_day = yesterday.strftime("%Y%m%d")

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
    dag_id='airflow_daily_ods_ga_backup',
    default_args = default_args,
    schedule_interval= '0 1 * * *',
    start_date= datetime(2022,6,18,1,tzinfo=local_tz),
    catchup= False
)


DPN_AFFINITY = BashOperator(
    task_id= 'DPN_AFFINITY',
    # bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_AFFINITY.py {start_day} {end_day}',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_AFFINITY.py',
    dag= dag
)

DPN_AGE = BashOperator(
    task_id= 'DPN_AGE',
    # bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_AGE.py {start_day} {end_day}',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_AGE.py',
    dag= dag
)


DPN_BEHAVIOR = BashOperator(
    task_id= 'DPN_BEHAVIOR',
    # bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_BEHAVIOR.py {start_day} {end_day}',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_BEHAVIOR.py',
    dag= dag
)

DPN_CLIENT = BashOperator(
    task_id= 'DPN_CLIENT',
    # bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_CLIENT.py {start_day} {end_day}',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_CLIENT.py',
    dag= dag
)


DPN_CLIENT_CITY = BashOperator(
    task_id= 'DPN_CLIENT_CITY',
    # bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_CLIENT_CITY.py {start_day} {end_day}',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_CLIENT_CITY.py',
    dag= dag
)



DPN_GENDER = BashOperator(
    task_id= 'DPN_GENDER',
    # bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_GENDER.py {start_day} {end_day}',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_GENDER.py',
    dag= dag
)



DPN_GOAL = BashOperator(
    task_id= 'DPN_GOAL',
    # bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_GOAL.py {start_day} {end_day}',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_GOAL.py',
    dag= dag
)


DPN_ORDER = BashOperator(
    task_id= 'DPN_ORDER',
    # bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_ORDER.py {start_day} {end_day}',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_ORDER.py',
    dag= dag
)



DPN_ORDER_PRODUCT = BashOperator(
    task_id= 'DPN_ORDER_PRODUCT',
    # bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_ORDER_PRODUCT.py {start_day} {end_day}',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_ORDER_PRODUCT.py',
    dag= dag
)

DPN_PAGE = BashOperator(
    task_id= 'DPN_PAGE',
    # bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_PAGE.py {start_day} {end_day}',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_PAGE.py',
    dag= dag
)



DPN_PRODUCT = BashOperator(
    task_id= 'DPN_PRODUCT',
    # bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_PRODUCT.py {start_day} {end_day}',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_PRODUCT.py',
    dag= dag
)



DPN_SEARCH = BashOperator(
    task_id= 'DPN_SEARCH',
    # bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_SEARCH.py {start_day} {end_day}',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_SEARCH.py',
    dag= dag
)


DPN_SOCIAL_MEDIUM = BashOperator(
    task_id= 'DPN_SOCIAL_MEDIUM',
    # bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_SOCIAL_MEDIUM.py {start_day} {end_day}',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_SOCIAL_MEDIUM.py',
    dag= dag
)


PNT_AFFINITY = BashOperator(
    task_id= 'PNT_AFFINITY',
    # bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_AFFINITY.py {start_day} {end_day}',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_AFFINITY.py',
    dag= dag
)



PNT_AGE = BashOperator(
    task_id= 'PNT_AGE',
    # bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_AGE.py {start_day} {end_day}',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_AGE.py',
    dag= dag
)



PNT_BEHAVIOR = BashOperator(
    task_id= 'PNT_BEHAVIOR',
    # bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_BEHAVIOR.py {start_day} {end_day}',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_BEHAVIOR.py',
    dag= dag
)


PNT_CLIENT = BashOperator(
    task_id= 'PNT_CLIENT',
    # bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_CLIENT.py {start_day} {end_day}',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_CLIENT.py',
    dag= dag
)


PNT_CLIENT_CITY = BashOperator(
    task_id= 'PNT_CLIENT_CITY',
    # bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_CLIENT_CITY.py {start_day} {end_day}',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_CLIENT_CITY.py',
    dag= dag
)


PNT_GENDER = BashOperator(
    task_id= 'PNT_GENDER',
    # bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_GENDER.py {start_day} {end_day}',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_GENDER.py',
    dag= dag
)



PNT_GOAL = BashOperator(
    task_id= 'PNT_GOAL',
    # bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_GOAL.py {start_day} {end_day}',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_GOAL.py',
    dag= dag
)



PNT_ORDER = BashOperator(
    task_id= 'PNT_ORDER',
    # bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_ORDER.py {start_day} {end_day}',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_ORDER.py',
    dag= dag
)



PNT_ORDER_PRODUCT = BashOperator(
    task_id= 'PNT_ORDER_PRODUCT',
    # bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_ORDER_PRODUCT.py {start_day} {end_day}',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_ORDER_PRODUCT.py',
    dag= dag
)



PNT_PAGE = BashOperator(
    task_id= 'PNT_PAGE',
    # bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_PAGE.py {start_day} {end_day}',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_PAGE.py',
    dag= dag
)



PNT_PRODUCT = BashOperator(
    task_id= 'PNT_PRODUCT',
    # bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_PRODUCT.py {start_day} {end_day}',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_PRODUCT.py',
    dag= dag
)



PNT_SEARCH = BashOperator(
    task_id= 'PNT_SEARCH',
    # bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_SEARCH.py {start_day} {end_day}',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_SEARCH.py',
    dag= dag
)


PNT_SOCIAL_MEDIUM = BashOperator(
    task_id= 'PNT_SOCIAL_MEDIUM',
    # bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_SOCIAL_MEDIUM.py {start_day} {end_day}',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_SOCIAL_MEDIUM.py',
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

check_ga_daily = PythonOperator(task_id="check_ga_daily", python_callable=check, op_kwargs={'system_name':'ga'}, dag=dag)

DPN_AFFINITY >>\
DPN_AGE >> \
DPN_BEHAVIOR >> \
DPN_CLIENT >> \
DPN_CLIENT_CITY >> \
DPN_GENDER >> \
DPN_GOAL >> \
DPN_ORDER >> \
DPN_ORDER_PRODUCT >> \
DPN_PAGE >> \
DPN_PRODUCT >> \
DPN_SEARCH >> \
DPN_SOCIAL_MEDIUM >> \
PNT_AFFINITY >> \
PNT_AGE >> \
PNT_BEHAVIOR >> \
PNT_CLIENT >> \
PNT_CLIENT_CITY >> \
PNT_GENDER >> \
PNT_GOAL >> \
PNT_ORDER >> \
PNT_ORDER_PRODUCT >> \
PNT_PAGE >> \
PNT_PRODUCT >> \
PNT_SEARCH >> \
PNT_SOCIAL_MEDIUM >> \
check_ga_daily