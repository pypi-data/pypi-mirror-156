from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta
# from slack_operators import task_fail_slack_alert
from airflow.models.variable import Variable
from airflow.operators.python_operator import PythonOperator
import os
import pandas as pd
from datetime import date
from ..gcwb_sql.generate_query import check_duprows,execute_rownum_query
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
    dag_id='airflow_daily_ods_dpn',
    default_args = default_args,
    schedule_interval= '0 1 * * *',
    start_date= datetime(2022,6,18,1,tzinfo=local_tz),
    catchup= False
)


t1 = BashOperator(
    task_id= 'check_row_first',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_sql/generate_query.py dpn',
    dag= dag
)

t2 = BashOperator(
    task_id= 'drpnt_daily',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/drpnt_daily.py',
    dag= dag
)

t3 = BashOperator(
    task_id= 'check_row_last',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_sql/generate_query.py dpn',
    dag= dag
)
t1 >> t2 >> t3
