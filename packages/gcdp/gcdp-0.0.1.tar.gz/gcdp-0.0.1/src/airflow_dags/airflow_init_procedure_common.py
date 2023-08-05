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
    dag_id='airflow_init_procedure_common',
    default_args = default_args,
    schedule_interval= '0 8 * * *',
    start_date= datetime(2022, 5, 15),
    catchup= False
)

yesterday = date.today() - timedelta(days=1)
query1 = f"CALL GCWB_WDB.DM.P_MCSD_CNSL_HDQT_CLS_I();",
query2 = f"CALL GCWB_WDB.DM.P_MCSD_CNSL_INQ_LCLS_I();",
query3 = f"CALL GCWB_WDB.DM.P_MSTD_SIDO_I();",
query4 = f"CALL GCWB_WDB.DM.P_MSTD_SIGUNGU_I();",
query5 = f"CALL GCWB_WDB.DM.P_MTDD_MALL_CLS_I();",
query6 = f"CALL GCWB_WDB.DM.P_MTDD_MALL_CLSF_I();",


def select_query(**kwargs):
    table_name = kwargs['table_name']
    dwh_hook = SnowflakeHook(snowflake_conn_id="SNOWFLAKE_CONN_ID")
    result = dwh_hook.get_first(f"SELECT COUNT(*) FROM GCWB_WDB.DM.{table_name}")
    logging.info(f"Number of rows in `GCWB_WDB.DM.{table_name}`  - %s", result[0])

t1 = SnowflakeOperator(
    task_id= 'MCSD_CNSL_HDQT_CLS',
    sql=query1,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)

t2 = PythonOperator(task_id="count_query1", python_callable=select_query, op_kwargs={'table_name':'MCSD_CNSL_HDQT_CLS'})

t3 = SnowflakeOperator(
    task_id= 'MCSD_CNSL_INQ_LCLS',
    sql=query2,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)

t4 = PythonOperator(task_id="count_query2", python_callable=select_query, op_kwargs={'table_name':'MCSD_CNSL_INQ_LCLS'})

t5 = SnowflakeOperator(
    task_id= 'MSTD_SIDO',
    sql=query3,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)

t6 = PythonOperator(task_id="count_query3", python_callable=select_query, op_kwargs={'table_name':'MSTD_SIDO'})

t7 = SnowflakeOperator(
    task_id= 'MSTD_SIGUNGU',
    sql=query4,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)

t8 = PythonOperator(task_id="count_query4", python_callable=select_query, op_kwargs={'table_name':'MSTD_SIGUNGU'})

t9 = SnowflakeOperator(
    task_id= 'MTDD_MALL_CLS',
    sql=query5,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)

t10 = PythonOperator(task_id="count_query5", python_callable=select_query, op_kwargs={'table_name':'MTDD_MALL_CLS'})

t11 = SnowflakeOperator(
    task_id= 'MTDD_MALL_CLSF',
    sql=query6,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)

t12 = PythonOperator(task_id="count_query6", python_callable=select_query, op_kwargs={'table_name':'MTDD_MALL_CLSF'})

t1  >> t2 >> t3  >> t4 >> t5  >> t6 >> t7  >> t8 >> t9  >> t10 >> t11  >> t12