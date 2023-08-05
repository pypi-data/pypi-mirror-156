from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta, date
# from slack_operators import task_fail_slack_alert
from airflow.models.variable import Variable

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
    dag_id='airflow_individual_ga',
    default_args = default_args,
    schedule_interval= '@once',
    start_date= datetime(2022, 5, 15),
    catchup= False
)


yesterday = date.today() - timedelta(days=1)

dpn_start_day = '2021-01-18'
dpn_end_day = '2022-05-31'

DPN_CLIENT = BashOperator(
    task_id= 'DPN_CLIENT',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_CLIENT.py {dpn_start_day} {dpn_end_day}',
    dag= dag
)

DPN_CLIENT_CITY = BashOperator(
    task_id= 'DPN_CLIENT_CITY',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_CLIENT_CITY.py {dpn_start_day} {dpn_end_day}',
    dag= dag
)

DPN_SOCIAL_MEDIUM = BashOperator(
    task_id= 'DPN_SOCIAL_MEDIUM',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/DPN_SOCIAL_MEDIUM.py {dpn_start_day} {dpn_end_day}',
    dag= dag
)

pnt_start_day = '2021-10-19'
pnt_end_day = '2022-05-31'

PNT_CLIENT = BashOperator(
    task_id= 'PNT_CLIENT',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_CLIENT.py {pnt_start_day} {pnt_end_day}',
    dag= dag
)

PNT_CLIENT_CITY = BashOperator(
    task_id= 'PNT_CLIENT_CITY',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_CLIENT_CITY.py {pnt_start_day} {pnt_end_day}',
    dag= dag
)

PNT_SOCIAL_MEDIUM = BashOperator(
    task_id= 'PNT_SOCIAL_MEDIUM',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/ga/PNT_SOCIAL_MEDIUM.py {pnt_start_day} {pnt_end_day}',
    dag= dag
)

DPN_CLIENT >> DPN_CLIENT_CITY >>  DPN_SOCIAL_MEDIUM >>  PNT_CLIENT >> PNT_CLIENT_CITY >>  PNT_SOCIAL_MEDIUM