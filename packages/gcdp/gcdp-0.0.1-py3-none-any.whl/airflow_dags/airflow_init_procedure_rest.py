from airflow import DAG
# from airflow_dags.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
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
    dag_id='airflow_init_procedure_rest',
    default_args = default_args,
    schedule_interval= '0 8 * * *',
    start_date= datetime(2022, 5, 15),
    catchup= False
)

yesterday = date.today() - timedelta(days=1)

base_dd = f"CALL GCWB_WDB.DM.P_MSTD_BASE_DD_I({yesterday.strftime('%Y%d%m')});",

base_mm = f"CALL GCWB_WDB.DM.P_MSTD_BASE_MM_I({yesterday.strftime('%Y%d%m')});",
base_wk = f"CALL GCWB_WDB.DM.P_MSTD_BASE_WK_I({yesterday.strftime('%Y%d%m')});",
base_yy = f"CALL GCWB_WDB.DM.P_MSTD_BASE_YY_I({yesterday.strftime('%Y%d%m')});",



def select_query(**kwargs):
    table_name = kwargs['table_name']
    dwh_hook = SnowflakeHook(snowflake_conn_id="SNOWFLAKE_CONN_ID")
    result = dwh_hook.get_first(f"SELECT COUNT(*) FROM {table_name}")
    logging.info(f"Number of rows in `GCWB_WDB.DM.{table_name}`  - %s", result[0])



call_restday_api = BashOperator(
    task_id= 'airflow_restdays',
    bash_command = 'python3 /home/ubuntu/gcdp/commonlibs/pdutils.py',
    dag= dag
)
check_holiday = PythonOperator(task_id="check_holiday", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DW.WSTC_HOL'})


call_base_dd = SnowflakeOperator(
    task_id= 'MSTD_BASE_DD',
    sql=base_dd,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)

check_base_dd = PythonOperator(task_id="check_base_dd", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MSTD_BASE_DD'})

call_base_mm = SnowflakeOperator(
    task_id= 'MSTD_BASE_MM',
    sql=base_mm,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)

check_base_mm = PythonOperator(task_id="check_base_mm", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MSTD_BASE_MM'})

call_base_wk = SnowflakeOperator(
    task_id= 'MSTD_BASE_WK',
    sql=base_wk,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)

check_base_wk = PythonOperator(task_id="check_base_wk", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MSTD_BASE_WK'})

call_base_yy = SnowflakeOperator(
    task_id= 'MSTD_BASE_YY',
    sql=base_yy,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)

check_base_yy = PythonOperator(task_id="check_base_yy", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MSTD_BASE_YY'})




MOBD_PAGE = f"CALL GCWB_WDB.DM.P_MOBD_PAGE_I();",
call_page1 = SnowflakeOperator(
    task_id= 'MOBD_PAGE',
    sql=MOBD_PAGE,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)

check_page1 = PythonOperator(task_id="check_page1", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MOBD_PAGE'})

MOBD_PGR_FO_STEP = f"CALL GCWB_WDB.DM.P_MOBD_PGR_FO_STEP_I();",
call_page2 = SnowflakeOperator(
    task_id= 'MOBD_PGR_FO_STEP',
    sql=MOBD_PGR_FO_STEP,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_page2 = PythonOperator(task_id="check_page2", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MOBD_PGR_FO_STEP'})


MOBS_PAGE_EFF = f"CALL GCWB_WDB.DM.P_MOBS_PAGE_EFF_I({yesterday.strftime('%Y%m%d')});",
call_page3 = SnowflakeOperator(
    task_id= 'MOBS_PAGE_EFF',
    sql=MOBS_PAGE_EFF,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_page3 = PythonOperator(task_id="check_page3", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MOBS_PAGE_EFF'})


MOBD_PGR_FT_STEP = f"CALL GCWB_WDB.DM.P_MOBD_PGR_FT_STEP_I();",
call_page4 = SnowflakeOperator(
    task_id= 'MOBD_PGR_FT_STEP',
    sql=MOBD_PGR_FT_STEP,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_page4 = PythonOperator(task_id="check_page4", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MOBD_PGR_FT_STEP'})

MOBD_PGR_SE_STEP = f"CALL GCWB_WDB.DM.P_MOBD_PGR_SE_STEP_I();",
call_page5 = SnowflakeOperator(
    task_id= 'MOBD_PGR_SE_STEP',
    sql=MOBD_PGR_SE_STEP,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_page5 = PythonOperator(task_id="check_page5", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MOBD_PGR_SE_STEP'})

MOBD_PGR_TH_STEP = f"CALL GCWB_WDB.DM.P_MOBD_PGR_TH_STEP_I();",
call_page6 = SnowflakeOperator(
    task_id= 'MOBD_PGR_TH_STEP',
    sql=MOBD_PGR_TH_STEP,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_page6 = PythonOperator(task_id="check_page6", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MOBD_PGR_TH_STEP'})

MOBS_VSTR_BHV = f"CALL GCWB_WDB.DM.P_MOBS_VSTR_BHV_I();",
call_MOBS_VSTR_BHV = SnowflakeOperator(
    task_id= 'MOBS_VSTR_BHV',
    sql=MOBS_VSTR_BHV,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_MOBS_VSTR_BHV = PythonOperator(task_id="check_MOBS_VSTR_BHV", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MOBS_VSTR_BHV'})


MOBD_IFL_CHNL = f"CALL GCWB_WDB.DM.P_MOBD_IFL_CHNL_I();",
call_MOBD_IFL_CHNL = SnowflakeOperator(
    task_id= 'MOBD_IFL_CHNL',
    sql=MOBD_IFL_CHNL,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_MOBD_IFL_CHNL = PythonOperator(task_id="check_MOBD_IFL_CHNL", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MOBD_IFL_CHNL'})



MOBD_IFL_MED = f"CALL GCWB_WDB.DM.P_MOBD_IFL_MED_I();",
call_MOBD_IFL_MED = SnowflakeOperator(
    task_id= 'MOBD_IFL_MED',
    sql=MOBD_IFL_MED,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_MOBD_IFL_MED = PythonOperator(task_id="check_MOBD_IFL_MED", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MOBD_IFL_MED'})


MOBD_IFL_SRC = f"CALL GCWB_WDB.DM.P_MOBD_IFL_SRC_I();",
call_MOBD_IFL_SRC = SnowflakeOperator(
    task_id= 'MOBD_IFL_SRC',
    sql=MOBD_IFL_SRC,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_MOBD_IFL_SRC = PythonOperator(task_id="check_MOBD_IFL_SRC", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MOBD_IFL_SRC'})


MOBD_SCN = f"CALL GCWB_WDB.DM.P_MOBD_SCN_I();",
call_MOBD_SCN = SnowflakeOperator(
    task_id= 'MOBD_SCN',
    sql=MOBD_SCN,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_MOBD_SCN = PythonOperator(task_id="check_MOBD_SCN", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MOBD_SCN'})


call_restday_api >> check_holiday >> call_base_dd >> check_base_dd >> call_base_mm >> check_base_mm >> call_base_wk >> check_base_wk >> call_base_yy >> check_base_yy >> call_page1 >> check_page1 >> call_page2 >> check_page2 >> call_page3 >> check_page3 >> call_page4 >> check_page4 >> call_page5 >> check_page5 >> call_page6 >> check_page6 >> call_MOBS_VSTR_BHV >> check_MOBS_VSTR_BHV >> call_MOBD_IFL_CHNL >> check_MOBD_IFL_CHNL >> call_MOBD_IFL_MED >> check_MOBD_IFL_MED >> call_MOBD_IFL_SRC >> check_MOBD_IFL_SRC >> call_MOBD_SCN >> check_MOBD_SCN
