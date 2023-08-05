from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta, date
# from slack_operators import task_fail_slack_alert
from airflow.models.variable import Variable


start_day = Variable.get("pnt_start_day")
end_day = Variable.get("pnt_end_day")

default_args = {
    'owner': 'yjjo',
    # 'email': 'gcs.kelly@gmail.com',
    # 'email_on_failure': True,
    # 'email_on_retry': True,
    # 'email_on_success': True,
    'retries': 3,
    'retry_delay': timedelta(minutes=1),
    # 'on_failure_callback': task_fail_slack_alert,
    'trigger_rule': 'all_success',
}

dag = DAG(
    dag_id='airflow_change_ods_pnt',
    default_args = default_args,
    schedule_interval= '@once',
    start_date= datetime(2022, 5, 15),
    catchup= False
)



t1 = BashOperator(
    task_id= 'pntshop_crawler',
    bash_command = 'python3 /home/ubuntu/gcdp/gcwb_dataload/pntshop_crawler.py',
    dag= dag
)

t2 = BashOperator(
    task_id= 'pntshop_dataload',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/pntshop_monthly.py {start_day} {end_day}',
    dag= dag
)


t1 >> t2