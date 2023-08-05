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
    dag_id='airflow_init_procedure_current_city',
    default_args = default_args,
    schedule_interval= '0 8 * * *',
    start_date= datetime(2022, 5, 15),
    catchup= False
)


yesterday = date.today() - timedelta(days=1)
query1 = f"CALL GCWB_WDB.DM.P_MOBD_CNC_AREA_I();",
query2 = f"CALL GCWB_WDB.DM.P_MOBD_CNC_CITY_I();"
query3 = f"CALL GCWB_WDB.DM.P_MOBD_CNC_NAT_I();"

def select_query(**context):
    dwh_hook = SnowflakeHook(snowflake_conn_id="SNOWFLAKE_CONN_ID")
    result = dwh_hook.get_first("SELECT COUNT(*) FROM GCWB_WDB.DM.MOBD_CNC_AREA;")
    logging.info("Number of rows in `GCWB_WDB.DM.MOBD_SCK`  - %s", result[0])
    result = dwh_hook.get_first("SELECT COUNT(*) FROM GCWB_WDB.DM.MOBD_CNC_CITY;")
    logging.info("Number of rows in `GCWB_WDB.DM.MOBD_IFL_MED`  - %s", result[0])
    result = dwh_hook.get_first("SELECT COUNT(*) FROM GCWB_WDB.DM.MOBD_CNC_NAT;")
    logging.info("Number of rows in `GCWB_WDB.DM.MOBD_IFL_MED`  - %s", result[0])

t1 = SnowflakeOperator(
    task_id= 'P_MOBD_CNC_AREA_I',
    sql=query1,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
t2 = SnowflakeOperator(
    task_id= 'P_MOBD_CNC_CITY_I',
    sql=query2,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
t3 = SnowflakeOperator(
    task_id= 'P_MOBD_CNC_NAT_I',
    sql=query3,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
t4 = PythonOperator(task_id="count_query", python_callable=select_query)

t1  >> t2  >> t3  >> t4