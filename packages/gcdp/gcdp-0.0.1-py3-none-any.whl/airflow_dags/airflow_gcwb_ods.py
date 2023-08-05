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
    dag_id='airflow_gcwb_ods',
    default_args = default_args,
    schedule_interval= '0 8 * * *',
    start_date= datetime(2022, 5, 15),
    catchup= False
)



drpnt = BashOperator(
    task_id= 'airflow_drpnt',
    bash_command = 'python3 /home/ubuntu/gcdp/gcwb_dataload/drpnt_init.py',
    dag= dag
)

gadrpnt = BashOperator(
    task_id= 'airflow_gadrpnt',
    bash_command = 'python3 /home/ubuntu/gcdp/gcwb_dataload/GA_API_Data_DPN.py',
    dag= dag
)

gapntshop = BashOperator(
    task_id= 'airflow_gapntshop',
    bash_command = 'python3 /home/ubuntu/gcdp/gcwb_dataload/GA_API_Data_PNT.py',
    dag= dag
)

gadrpnt >> gapntshop >> drpnt