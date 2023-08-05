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
    dag_id='airflow_init_pntshop',
    default_args = default_args,
    schedule_interval= '@once',
    start_date= datetime(2022, 5, 15),
    catchup= False
)



pntshop = BashOperator(
    task_id= 'airflow_pntshop',
    bash_command = 'python3 /home/ubuntu/gcdp/gcwb_dataload/pntshop_init.py',
    dag= dag
)

pntshop