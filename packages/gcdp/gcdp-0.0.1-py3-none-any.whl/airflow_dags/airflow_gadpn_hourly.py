from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta
# from slack_operators import task_fail_slack_alert
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator

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
    schedule_interval= '0 * * * *',
    start_date= datetime(2022, 5, 15),
    catchup= False
)

table_name
query1=f"DELETE FROM {table_name} WHERE DATE={}"
t1 = SnowflakeOperator(
    task_id='delete today rows',
    sql = query1,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)


t2 = BashOperator(
    task_id= 'airflow_gadrpnt',
    bash_command = 'python3 /opt/prj/gcdp/api/clibs.py',
    dag= dag
)

t1

