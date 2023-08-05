from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta
# from slack_operators import task_fail_slack_alert
from airflow.models.variable import Variable
from datetime import date
import os
import pandas as pd

from commonlibs.utils import project_path
from ..gcwb_sql.generate_query import execute_rownum_query, check_duprows

start_day = Variable.get("dpn_start_day")
end_day = Variable.get("dpn_end_day")

default_args = {
    'owner': 'yjjo',
    # 'email': 'gcs.kelly@gmail.com',
    # 'email_on_failure': True,
    # 'email_on_retry': True,
    # 'email_on_success': True,
    'retries': 3,
    'retry_delay': timedelta(minutes=1),
    # 'on_failure_callback': task_fail_slack_alert,
    'trigger_rule': 'all_success',
}

dag = DAG(
    dag_id='airflow_change_ods_dpn',
    default_args = default_args,
    schedule_interval= '@once',
    start_date= datetime(2022, 5, 15),
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

check_dpn_daily_back = PythonOperator(task_id="check_dpn_daily_back", python_callable=check, op_kwargs={'system_name':'dpn'}, dag=dag)

t1 = BashOperator(
    task_id= 'drpnt_daily',
    bash_command = f'python3 /home/ubuntu/gcdp/gcwb_dataload/drpnt_daily.py {start_day} {end_day}',
    dag= dag
)

check_dpn_daily_forth = PythonOperator(task_id="check_dpn_daily_forth", python_callable=check, op_kwargs={'system_name':'dpn'}, dag=dag)

check_dpn_daily_forth >> t1 >> check_dpn_daily_back