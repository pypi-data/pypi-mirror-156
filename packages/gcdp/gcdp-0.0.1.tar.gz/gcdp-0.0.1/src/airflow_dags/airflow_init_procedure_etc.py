from airflow import DAG
# from airflow_dags.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.contrib.hooks.snowflake_hook import SnowflakeHook
# from slack_operators import task_fail_slack_alert
import logging
from datetime import date


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
    dag_id='airflow_init_procedure_etc',
    default_args = default_args,
    schedule_interval= '0 8 * * *',
    start_date= datetime(2022, 5, 15),
    catchup= False
)

yesterday = date.today() - timedelta(days=1)
query1 = f"CALL GCWB_WDB.DM.P_MMBD_AGE_I();",
query2 = f"CALL GCWB_WDB.DM.P_MMBD_EEMC_I();",
query3 = f"CALL GCWB_WDB.DM.P_MMBD_PUR_CY_I();",
query4 = f"CALL GCWB_WDB.DM.P_MMBD_VST_CY_I();"






def select_query(**kwargs):
    table_name = kwargs['table_name']
    dwh_hook = SnowflakeHook(snowflake_conn_id="SNOWFLAKE_CONN_ID")
    result = dwh_hook.get_first(f"SELECT COUNT(*) FROM GCWB_WDB.DM.{table_name}")
    logging.info(f"Number of rows in `GCWB_WDB.DM.{table_name}`  - %s", result[0])

t1 = SnowflakeOperator(
    task_id= 'MMBD_AGE',
    sql=query1,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)

t2 = PythonOperator(task_id="count_query1", python_callable=select_query, op_kwargs={'table_name':'MMBD_AGE'})

t3 = SnowflakeOperator(
    task_id= 'MMBD_EEMC',
    sql=query2,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)

t4 = PythonOperator(task_id="count_query2", python_callable=select_query, op_kwargs={'table_name':'MMBD_EEMC'})

t5 = SnowflakeOperator(
    task_id= 'MMBD_PUR_CY',
    sql=query3,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)

t6 = PythonOperator(task_id="count_query3", python_callable=select_query, op_kwargs={'table_name':'MMBD_PUR_CY'})

t7 = SnowflakeOperator(
    task_id= 'MMBD_VST_CY',
    sql=query4,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)

t8 = PythonOperator(task_id="count_query4", python_callable=select_query, op_kwargs={'table_name':'MMBD_VST_CY'})

t1  >> t2 >> t3  >> t4 >> t5  >> t6 >> t7  >> t8