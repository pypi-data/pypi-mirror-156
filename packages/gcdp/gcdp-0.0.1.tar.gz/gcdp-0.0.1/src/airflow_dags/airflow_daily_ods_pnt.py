from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta
# from slack_operators import task_fail_slack_alert
from airflow.models.variable import Variable
from datetime import date

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
    dag_id='airflow_daily_ods_pnt',
    default_args = default_args,
    schedule_interval= '0 1 * * *',
    start_date= datetime(2022,6,18,1,tzinfo=local_tz),
    catchup= False
)



t1 = BashOperator(
    task_id= 'pntshop_crawler',
    bash_command = 'python3 /home/ubuntu/gcdp/gcwb_dataload/pntshop_crawler.py',
    dag= dag
)

t2 = BashOperator(
    task_id= 'pntshop_dataload',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/pntshop_monthly.py',
    dag= dag
)


t1 >> t2
