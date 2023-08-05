from airflow import DAG
from datetime import datetime, timedelta, date
# from slack_operators import task_fail_slack_alert
from airflow.operators.python_operator import PythonOperator
import pandas as pd
import os

from ..gcwb_sql.generate_query import check_duprows, execute_rownum_query
from commonlibs.utils import project_path

import pendulum
from datetime import datetime

local_tz = pendulum.timezone('Asia/Seoul')


default_args = {
    'owner': 'yjjo',
    # 'email': 'gcs.kelly@gmail.com',
    # 'email_on_failure': True,
    # 'email_on_retry': True,
    # 'email_on_success': True,
    'retries': 3,
    'retry_delay': timedelta(minutes=3),
    # 'on_failure_callback': task_fail_slack_alert,
    'trigger_rule': 'all_success',
}

dag = DAG(
    dag_id='airflow_checkrows',
    default_args = default_args,
    schedule_interval= '@once',
    start_date= datetime(2022,6,18,1,tzinfo=local_tz),
    catchup= False
)

def check(**kwargs):
    system_name = kwargs['system_name']
    code_folder = os.path.join(os.path.join(os.path.join(project_path, "gcwb_dataload"), "code"),
                               f"{system_name}_table_list.xlsx")
    df = pd.read_excel(f"{code_folder}", index_col=False)
    table_list = list(df["table_list"])
    if (system_name == "dpn"):
        table_list.remove("t_product_tag")
        table_list.remove("t_order_status_log")
        table_list.remove("t_point_use")
    total_rows = 0
    for table_name in table_list:
        # print(table_name)
        check_duprows(f"{system_name}", table_name)
        total_rows = total_rows + execute_rownum_query(system_name=system_name, table_name=table_name)
    print(f"system_name: {system_name}  total_rows: {total_rows} rows")
    print(" ================================================================================================== ")

check_ga_daily = PythonOperator(task_id="check_ga_daily", python_callable=check, op_kwargs={'system_name':'ga'}, dag=dag)
check_dpn_daily = PythonOperator(task_id="check_dpn_daily", python_callable=check, op_kwargs={'system_name':'dpn'}, dag=dag)
check_pnt_daily = PythonOperator(task_id="check_pnt_daily", python_callable=check, op_kwargs={'system_name':'pnt'}, dag=dag)

check_ga_daily >> check_dpn_daily >> check_pnt_daily