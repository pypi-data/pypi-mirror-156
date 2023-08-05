from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta
# from slack_operators import task_fail_slack_alert

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
    dag_id='airflow_gadrpnt',
    default_args = default_args,
    schedule_interval= '0 1 * * *',
    start_date= datetime(2022, 5, 15),
    catchup= False
)



t1 = BashOperator(
    task_id= 'airflow_gadrpnt',
    bash_command = 'python3 /home/ubuntu/gcdp/gcwb_dataload/clibs.py',
    dag= dag
)

t1

