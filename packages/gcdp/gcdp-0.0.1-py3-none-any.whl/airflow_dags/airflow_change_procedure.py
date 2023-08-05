from airflow import DAG
# from airflow_dags.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.contrib.hooks.snowflake_hook import SnowflakeHook
# from slack_operators import task_fail_slack_alert
import logging
from datetime import date
from airflow.operators.bash_operator import BashOperator


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
    dag_id='airflow_change_procedure',
    default_args = default_args,
    schedule_interval= '0 8 * * *',
    start_date= datetime(2022, 5, 15),
    catchup= False
)

yesterday = date.today() - timedelta(days=1)
q_MOBD_SCK = f"CALL GCWB_WDB.DM.P_MOBD_SCK_C();",
q_MOBD_SRCH_CTGR = f"CALL GCWB_WDB.DM.P_MOBD_SRCH_CTGR_C();",

q_MOBD_CNC_AREA = f"CALL GCWB_WDB.DM.P_MOBD_CNC_AREA_C();",
q_MOBD_CNC_CITY = f"CALL GCWB_WDB.DM.P_MOBD_CNC_CITY_C();"
q_MOBD_CNC_NAT = f"CALL GCWB_WDB.DM.P_MOBD_CNC_NAT_C();"

q_MMKD_CPN = f"CALL GCWB_WDB.DM.P_MMKD_CPN_C({yesterday.strftime('%Y%m%d')});",

q_MMKD_EXH = f"CALL GCWB_WDB.DM.P_MMKD_EXH_C();",

q_MSTD_BASE_DD = f"CALL GCWB_WDB.DM.P_MSTD_BASE_DD_C({yesterday.strftime('%Y%d%m')});",
q_MSTD_BASE_MM = f"CALL GCWB_WDB.DM.P_MSTD_BASE_MM_C({yesterday.strftime('%Y%d%m')});",
q_MSTD_BASE_WK = f"CALL GCWB_WDB.DM.P_MSTD_BASE_WK_C({yesterday.strftime('%Y%d%m')});",
q_MSTD_BASE_YY = f"CALL GCWB_WDB.DM.P_MSTD_BASE_YY_C({yesterday.strftime('%Y%d%m')});",

q_MCSD_CNSL_HDQT_CLS = f"CALL GCWB_WDB.DM.P_MCSD_CNSL_HDQT_CLS_C();",
q_MCSD_CNSL_INQ_LCLS = f"CALL GCWB_WDB.DM.P_MCSD_CNSL_INQ_LCLS_C();",
q_MSTD_SIDO = f"CALL GCWB_WDB.DM.P_MSTD_SIDO_C();",
q_MSTD_SIGUNGU = f"CALL GCWB_WDB.DM.P_MSTD_SIGUNGU_C();",
q_MTDD_MALL_CLS = f"CALL GCWB_WDB.DM.P_MTDD_MALL_CLS_C();",
q_MTDD_MALL_CLSF = f"CALL GCWB_WDB.DM.P_MTDD_MALL_CLSF_C();",

q_MMBD_INTRST_SUBJ = "CALL GCWB_WDB.DM.P_MMBD_INTRST_SUBJ_C();",

q_MOBD_PAGE = f"CALL GCWB_WDB.DM.P_MOBD_PAGE_C();",
q_MOBD_PGR_FO_STEP = f"CALL GCWB_WDB.DM.P_MOBD_PGR_FO_STEP_C();",
q_MOBD_PGR_FT_STEP = f"CALL GCWB_WDB.DM.P_MOBD_PGR_FT_STEP_C();",
q_MOBD_PGR_SE_STEP = f"CALL GCWB_WDB.DM.P_MOBD_PGR_SE_STEP_C();",
q_MOBD_PGR_TH_STEP = f"CALL GCWB_WDB.DM.P_MOBD_PGR_TH_STEP_C();",

q_MMKD_PNT_PAY_DED_RSN = f"CALL GCWB_WDB.DM.P_MMKD_PNT_PAY_DED_RSN_C();",

q_MOBD_EXH_CTGR_LCLS = f"CALL GCWB_WDB.DM.P_MOBD_EXH_CTGR_LCLS_C();",
q_MOBD_EXH_CTGR_MCLS = f"CALL GCWB_WDB.DM.P_MOBD_EXH_CTGR_MCLS_C();"

q_MMBD_AGE = f"CALL GCWB_WDB.DM.P_MMBD_AGE_C();",
q_MMBD_EEMC = f"CALL GCWB_WDB.DM.P_MMBD_EEMC_C();",
q_MMBD_PUR_CY = f"CALL GCWB_WDB.DM.P_MMBD_PUR_CY_C();",
q_MMBD_VST_CY = f"CALL GCWB_WDB.DM.P_MMBD_VST_CY_C();"

q_MOBD_IFL_CHNL = f"CALL GCWB_WDB.DM.P_MOBD_IFL_CHNL_C();",
q_MOBD_IFL_MED = f"CALL GCWB_WDB.DM.P_MOBD_IFL_MED_C();",
q_MOBD_IFL_SRC = f"CALL GCWB_WDB.DM.P_MOBD_IFL_SRC_C();",
q_MOBD_SCN = f"CALL GCWB_WDB.DM.P_MOBD_SCN_C();",

def select_query(**kwargs):
    table_name = kwargs['table_name']
    dwh_hook = SnowflakeHook(snowflake_conn_id="SNOWFLAKE_CONN_ID")
    result = dwh_hook.get_first(f"SELECT COUNT(*) FROM {table_name}")
    logging.info(f"Number of rows in `GCWB_WDB.DM.{table_name}`  - %s", result[0])



# 1. search
MOBD_SCK = SnowflakeOperator(
    task_id= 'P_MOBD_SCK_C',
    sql=q_MOBD_SCK,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_MOBD_SCK = PythonOperator(task_id="check_MOBD_SCK", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MOBD_SCK'})

MOBD_SRCH_CTGR = SnowflakeOperator(
    task_id= 'P_MOBD_SRCH_CTGR_C',
    sql=q_MOBD_SRCH_CTGR,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_MOBD_SRCH_CTGR = PythonOperator(task_id="check_MOBD_SRCH_CTGR", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MOBD_SRCH_CTGR'})

# 2. current_city
MOBD_CNC_AREA = SnowflakeOperator(
    task_id= 'P_MOBD_CNC_AREA_C',
    sql=q_MOBD_CNC_AREA,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_MOBD_CNC_AREA = PythonOperator(task_id="check_MOBD_CNC_AREA", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MOBD_CNC_AREA'})

MOBD_CNC_CITY = SnowflakeOperator(
    task_id= 'P_MOBD_CNC_CITY_C',
    sql=q_MOBD_CNC_CITY,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_MOBD_CNC_CITY = PythonOperator(task_id="check_MOBD_CNC_CITY", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MOBD_CNC_CITY'})

MOBD_CNC_NAT = SnowflakeOperator(
    task_id= 'P_MOBD_CNC_NAT_C',
    sql=q_MOBD_CNC_NAT,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_MOBD_CNC_NAT = PythonOperator(task_id="check_MOBD_CNC_NAT", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MOBD_CNC_NAT'})

# 3. coupon
MMKD_CPN = SnowflakeOperator(
    task_id= 'P_MMKD_CPN_C',
    sql=q_MMKD_CPN,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_MMKD_CPN = PythonOperator(task_id="check_MMKD_CPN", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MMKD_CPN'})

# 4. product
MMKD_EXH = SnowflakeOperator(
    task_id= 'P_MMKD_EXH_C',
    sql=q_MMKD_EXH,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_MMKD_EXH = PythonOperator(task_id="check_MMKD_EXH", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MMKD_EXH'})

# 5. days
call_holiday_api = BashOperator(
    task_id= 'airflow_holidays',
    bash_command = 'python3 /home/ubuntu/gcdp/commonlibs/pdutils.py',
    dag= dag
)
check_holiday = PythonOperator(task_id="check_holiday", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DW.WSTC_HOL'})


MSTD_BASE_DD = SnowflakeOperator(
    task_id= 'MSTD_BASE_DD',
    sql=q_MSTD_BASE_DD,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_MSTD_BASE_DD = PythonOperator(task_id="check_base_dd", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MSTD_BASE_DD'})

MSTD_BASE_MM = SnowflakeOperator(
    task_id= 'MSTD_BASE_MM',
    sql=q_MSTD_BASE_MM,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)

check_MSTD_BASE_MM = PythonOperator(task_id="check_base_mm", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MSTD_BASE_MM'})

MSTD_BASE_WK = SnowflakeOperator(
    task_id= 'MSTD_BASE_WK',
    sql=q_MSTD_BASE_WK,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)

check_MSTD_BASE_WK = PythonOperator(task_id="check_base_wk", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MSTD_BASE_WK'})

MSTD_BASE_YY = SnowflakeOperator(
    task_id= 'MSTD_BASE_YY',
    sql=q_MSTD_BASE_YY,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_MSTD_BASE_YY = PythonOperator(task_id="check_base_yy", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MSTD_BASE_YY'})

# 6. common
MCSD_CNSL_HDQT_CLS = SnowflakeOperator(
    task_id= 'MCSD_CNSL_HDQT_CLS',
    sql=q_MCSD_CNSL_HDQT_CLS,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_MCSD_CNSL_HDQT_CLS = PythonOperator(task_id="check_MCSD_CNSL_HDQT_CLS", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MCSD_CNSL_HDQT_CLS'})

MCSD_CNSL_INQ_LCLS = SnowflakeOperator(
    task_id= 'MCSD_CNSL_INQ_LCLS',
    sql=q_MCSD_CNSL_INQ_LCLS,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_MCSD_CNSL_INQ_LCLS = PythonOperator(task_id="check_MCSD_CNSL_INQ_LCLS", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MCSD_CNSL_INQ_LCLS'})

MSTD_SIDO = SnowflakeOperator(
    task_id= 'MSTD_SIDO',
    sql=q_MSTD_SIDO,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_MSTD_SIDO = PythonOperator(task_id="check_MSTD_SIDO", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MSTD_SIDO'})

MSTD_SIGUNGU = SnowflakeOperator(
    task_id= 'MSTD_SIGUNGU',
    sql=q_MSTD_SIGUNGU,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_MSTD_SIGUNGU = PythonOperator(task_id="check_MSTD_SIGUNGU", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MSTD_SIGUNGU'})

MTDD_MALL_CLS = SnowflakeOperator(
    task_id= 'MTDD_MALL_CLS',
    sql=q_MTDD_MALL_CLS,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_MTDD_MALL_CLS = PythonOperator(task_id="check_MTDD_MALL_CLS", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MTDD_MALL_CLS'})

MTDD_MALL_CLSF = SnowflakeOperator(
    task_id= 'MTDD_MALL_CLSF',
    sql=q_MTDD_MALL_CLSF,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_MTDD_MALL_CLSF = PythonOperator(task_id="check_MTDD_MALL_CLSF", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MTDD_MALL_CLSF'})

# 7. health_topic
MMBD_INTRST_SUBJ = SnowflakeOperator(
    task_id= 'MMBD_INTRST_SUBJ',
    sql=q_MMBD_INTRST_SUBJ,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_MMBD_INTRST_SUBJ = PythonOperator(task_id="check_MMBD_INTRST_SUBJ", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MMBD_INTRST_SUBJ'})

# 8. page
MOBD_PAGE = SnowflakeOperator(
    task_id= 'MOBD_PAGE',
    sql=q_MOBD_PAGE,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)

check_MOBD_PAGE = PythonOperator(task_id="check_MOBD_PAGE", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MOBD_PAGE'})

MOBD_PGR_FO_STEP = SnowflakeOperator(
    task_id= 'MOBD_PGR_FO_STEP',
    sql=q_MOBD_PGR_FO_STEP,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_MOBD_PGR_FO_STEP = PythonOperator(task_id="check_MOBD_PGR_FO_STEP", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MOBD_PGR_FO_STEP'})

MOBD_PGR_FT_STEP = SnowflakeOperator(
    task_id= 'MOBD_PGR_FT_STEP',
    sql=q_MOBD_PGR_FT_STEP,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_MOBD_PGR_FT_STEP = PythonOperator(task_id="check_MOBD_PGR_FT_STEP", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MOBD_PGR_FT_STEP'})

MOBD_PGR_SE_STEP = SnowflakeOperator(
    task_id= 'MOBD_PGR_SE_STEP',
    sql=q_MOBD_PGR_SE_STEP,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_MOBD_PGR_SE_STEP = PythonOperator(task_id="check_MOBD_PGR_SE_STEP", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MOBD_PGR_SE_STEP'})

MOBD_PGR_TH_STEP = SnowflakeOperator(
    task_id= 'MOBD_PGR_TH_STEP',
    sql=q_MOBD_PGR_TH_STEP,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_MOBD_PGR_TH_STEP = PythonOperator(task_id="check_MOBD_PGR_TH_STEP", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MOBD_PGR_TH_STEP'})

# 9. code
MMKD_PNT_PAY_DED_RSN = SnowflakeOperator(
    task_id= 'MMKD_PNT_PAY_DED_RSN',
    sql=q_MMKD_PNT_PAY_DED_RSN,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_MMKD_PNT_PAY_DED_RSN = PythonOperator(task_id="check_MMKD_PNT_PAY_DED_RSN", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MMKD_PNT_PAY_DED_RSN'})

# 10. social_medium
MOBD_EXH_CTGR_LCLS = SnowflakeOperator(
    task_id= 'MOBD_EXH_CTGR_LCLS',
    sql=q_MOBD_EXH_CTGR_LCLS,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_MOBD_EXH_CTGR_LCLS = PythonOperator(task_id="check_MOBD_EXH_CTGR_LCLS", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MOBD_EXH_CTGR_LCLS'})

MOBD_EXH_CTGR_MCLS = SnowflakeOperator(
    task_id= 'MOBD_EXH_CTGR_MCLS',
    sql=q_MOBD_EXH_CTGR_MCLS,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_MOBD_EXH_CTGR_MCLS = PythonOperator(task_id="check_MOBD_EXH_CTGR_MCLS", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MOBD_EXH_CTGR_MCLS'})


MOBD_IFL_CHNL = SnowflakeOperator(
    task_id= 'MOBD_IFL_CHNL',
    sql=q_MOBD_IFL_CHNL,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_MOBD_IFL_CHNL = PythonOperator(task_id="check_MOBD_IFL_CHNL", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MOBD_IFL_CHNL'})

MOBD_IFL_MED = SnowflakeOperator(
    task_id= 'MOBD_IFL_MED',
    sql=q_MOBD_IFL_MED,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_MOBD_IFL_MED = PythonOperator(task_id="check_MOBD_IFL_MED", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MOBD_IFL_MED'})


MOBD_IFL_SRC = SnowflakeOperator(
    task_id= 'MOBD_IFL_SRC',
    sql=q_MOBD_IFL_SRC,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_MOBD_IFL_SRC = PythonOperator(task_id="check_MOBD_IFL_SRC", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MOBD_IFL_SRC'})

MOBD_SCN = SnowflakeOperator(
    task_id= 'MOBD_SCN',
    sql=q_MOBD_SCN,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_MOBD_SCN = PythonOperator(task_id="check_MOBD_SCN", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MOBD_SCN'})

# 11. etc
MMBD_AGE = SnowflakeOperator(
    task_id= 'MMBD_AGE',
    sql=q_MMBD_AGE,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_MMBD_AGE = PythonOperator(task_id="check_MMBD_AGE", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MMBD_AGE'})

MMBD_EEMC = SnowflakeOperator(
    task_id= 'MMBD_EEMC',
    sql=q_MMBD_EEMC,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_MMBD_EEMC = PythonOperator(task_id="check_MMBD_EEMC", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MMBD_EEMC'})

MMBD_PUR_CY = SnowflakeOperator(
    task_id= 'MMBD_PUR_CY',
    sql=q_MMBD_PUR_CY,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_MMBD_PUR_CY = PythonOperator(task_id="check_MMBD_PUR_CY", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MMBD_PUR_CY'})

MMBD_VST_CY = SnowflakeOperator(
    task_id= 'MMBD_VST_CY',
    sql=q_MMBD_VST_CY,
    snowflake_conn_id="SNOWFLAKE_CONN_ID",
    dag=dag
)
check_MMBD_VST_CY = PythonOperator(task_id="check_MMBD_VST_CY", python_callable=select_query, op_kwargs={'table_name':'GCWB_WDB.DM.MMBD_VST_CY'})

[MOBD_SCK, MOBD_SRCH_CTGR] >> check_MOBD_SCK >> check_MOBD_SRCH_CTGR >>\
[MOBD_CNC_AREA, MOBD_CNC_CITY, MOBD_CNC_NAT] >> check_MOBD_CNC_AREA >> check_MOBD_CNC_CITY >> check_MOBD_CNC_NAT >> \
MMKD_CPN>> check_MMKD_CPN >> \
MMKD_EXH >> check_MMKD_EXH >> \
call_holiday_api >> check_holiday >> MSTD_BASE_DD >> check_MSTD_BASE_DD >> [MSTD_BASE_MM, MSTD_BASE_WK, MSTD_BASE_YY] >> check_MSTD_BASE_MM >> check_MSTD_BASE_WK >> check_MSTD_BASE_YY >> \
[MCSD_CNSL_HDQT_CLS, MCSD_CNSL_INQ_LCLS, MSTD_SIDO, MSTD_SIGUNGU, MTDD_MALL_CLS, MTDD_MALL_CLSF] >> check_MCSD_CNSL_HDQT_CLS >> check_MCSD_CNSL_INQ_LCLS >> check_MSTD_SIDO >> check_MSTD_SIGUNGU >> check_MTDD_MALL_CLS >> check_MTDD_MALL_CLSF >> \
MMBD_INTRST_SUBJ >> check_MMBD_INTRST_SUBJ >>\
[MOBD_PAGE, MOBD_PGR_FO_STEP, MOBD_PGR_FT_STEP, MOBD_PGR_SE_STEP, MOBD_PGR_TH_STEP] >> check_MOBD_PAGE >> check_MOBD_PGR_FO_STEP >> check_MOBD_PGR_FT_STEP >> check_MOBD_PGR_SE_STEP >> check_MOBD_PGR_TH_STEP >> \
MMKD_PNT_PAY_DED_RSN >> check_MMKD_PNT_PAY_DED_RSN >> \
[MOBD_EXH_CTGR_LCLS, MOBD_EXH_CTGR_MCLS] >> check_MOBD_EXH_CTGR_LCLS >> check_MOBD_EXH_CTGR_MCLS >> \
[MOBD_IFL_CHNL, MOBD_IFL_MED, MOBD_IFL_SRC, MOBD_SCN]  >> check_MOBD_IFL_CHNL >> check_MOBD_IFL_MED >> check_MOBD_IFL_SRC >> check_MOBD_SCN >>\
MMBD_AGE >> check_MMBD_AGE >> MMBD_EEMC >> check_MMBD_EEMC >> MMBD_PUR_CY >> check_MMBD_PUR_CY >> MMBD_VST_CY >> check_MMBD_VST_CY