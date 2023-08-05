from airflow.models import Variable
import logging
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def var_test(**context):
    my_val = Variable.get("usa")
    print(my_val)
    logging.info("variable  - %s", my_val)


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
    dag_id='airflow_var_test',
    default_args = default_args,
    schedule_interval= '0 8 * * *',
    start_date= datetime(2022, 5, 15),
    catchup= False
)

t1 = PythonOperator(task_id="var_test1", python_callable=var_test, dag=dag)

t2 = BashOperator(
    task_id= 'airflow_bash_test',
    bash_command = 'ls',
    dag= dag
)

t1 >> t2