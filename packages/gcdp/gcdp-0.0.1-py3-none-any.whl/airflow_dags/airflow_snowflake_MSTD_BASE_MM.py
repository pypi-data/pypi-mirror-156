from airflow import DAG
# from airflow_dags.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.contrib.hooks.snowflake_hook import SnowflakeHook
# from slack_operators import task_fail_slack_alert
import logging



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
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
    dag_id='airflow_snowflake_MSTD_BASE_MM',
    default_args = default_args,
    schedule_interval= '0 8 * * *',
    start_date= datetime(2022, 5, 15),
    catchup= False
)


query1 = "TRUNCATE TABLE GCWB_WDB.DM.MSTD_BASE_DD;",
query2 = "CALL GCWB_WDB.DM.P_MSTD_BASE_DD_I('20220531');",

query3 = "TRUNCATE TABLE GCWB_WDB.DM.MSTD_BASE_MM;",
query4 = "CALL GCWB_WDB.DM.P_MSTD_BASE_MM_I('20220531');",

def select_query_DD(**context):
    dwh_hook = SnowflakeHook(snowflake_conn_id="SNOWFLAKE_CONN_ID")
    result = dwh_hook.get_first("SELECT COUNT(*) FROM GCWB_WDB.DM.MSTD_BASE_DD;")
    logging.info("Number of rows in `GCWB_WDB.DM.MSTD_BASE_DD`  - %s", result[0])

def select_query_MM(**context):
    dwh_hook = SnowflakeHook(snowflake_conn_id="SNOWFLAKE_CONN_ID")
    result = dwh_hook.get_first("SELECT COUNT(*) FROM GCWB_WDB.DM.MSTD_BASE_MM;")
    logging.info("Number of rows in `GCWB_WDB.DM.MSTD_BASE_MM`  - %s", result[0])



t1 = SnowflakeOperator(
    task_id= 'truncate_DD_task',
    sql=query1,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)

t2 = PythonOperator(task_id="count_query_DD_tr", python_callable=select_query_DD)

t3 = SnowflakeOperator(
    task_id= 'call_procedure_DD_task',
    sql=query2,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)

t4 = PythonOperator(task_id="count_query_DD_call", python_callable=select_query_DD)


t5 = SnowflakeOperator(
    task_id= 'truncate_MM_task',
    sql=query3,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)

t6 = PythonOperator(task_id="count_query_MM_tr", python_callable=select_query_MM)

t7 = SnowflakeOperator(
    task_id= 'call_procedure_MM_task',
    sql=query4,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)

t8 = PythonOperator(task_id="count_query_MM_call", python_callable=select_query_MM)


t1  >> t2 >> t3 >> t4 >> t5  >> t6 >> t7 >> t8


