import pandas as pd
import os
from commonlibs.utils import get_downloads_folder, set_downloads_folder, json_contents, yesterday
from ..gcwb_s3.upload_objects import upload_files_to_s3
from sqlalchemy import create_engine
from datetime import date, timedelta
from ..gcwb_sql.generate_query import execute_insert_query, execute_truncate_query, execute_rownum_query, execute_delete_query
import snowflake.connector
import sys
import datetime


def dpn_daily(start_day, end_day):
    # conn = create_engine(f'mysql+pymysql://{json_contents["drpnt_user"]}:{json_contents["drpnt_password"]}'
    #                      f'@{json_contents["drpnt_host"]}/{json_contents["drpnt_database"]}?ssl_ca={json_contents["drpnt_ssl_ca"]}',pool_pre_ping=True)
    conn = create_engine(f'mysql+pymysql://{json_contents["drpnt_user"]}:{json_contents["drpnt_password"]}'
                         f'@{json_contents["drpnt_host"]}/{json_contents["drpnt_database"]}?ssl_ca={json_contents["drpnt_ssl_ca"]}')
    snow_conn = snowflake.connector.connect(
        user=json_contents['sf_user'],
        password=json_contents['sf_pwd'],
        account=json_contents['sf_host'],
        warehouse=json_contents['sf_wh'],
        database=json_contents['sf_db'],
        schema=json_contents['sf_schema']
    )

    system_name = "dpn"
    set_downloads_folder(system_name)
    file_path = get_downloads_folder(system_name)
    #######################################################################################################################################################
    # Case1. 전체 데이터를 truncate하고 select * 로 mysql에서 읽어와 다시 적재
    table_list = \
    """
    t_clinic,
    t_coupon_product,
    t_order_status_code,
    t_pbanner_product,
    t_product_category,
    t_product_tag,
    t_routine_order_item,
    t_se_product,
    t_qna,
    T_MEMBER_CLINIC_LOG,
    T_MEMBER_LOG,
    T_MYCLINIC_HIS,
    t_order_status_log,
    t_order_refund,
    T_PAYMENT_LOG,
    t_point,
    t_point_use"""
    tbl_list = table_list.replace("    ", "").replace(" ", "").replace("\n", "").split(",")
    print(tbl_list)
    for table_name in tbl_list:
        df = pd.read_sql_query(f"SELECT * FROM {json_contents['drpnt_database']}.{table_name};",con=conn)
        df.to_csv(f'{os.path.join(file_path, table_name + ".csv")}', index=False, header=True, encoding='utf-8-sig')
        upload_files_to_s3(upload_date=date.today().strftime("%y%m%d"), system_name=system_name,
                           file=f"{table_name}.csv")
        execute_truncate_query(system_name=system_name, table_name=table_name)
        execute_insert_query(system_name=system_name, table_name=table_name, data_date=date.today().strftime("%y%m%d"))
        execute_rownum_query(system_name=system_name, table_name=table_name)
    #######################################################################################################################################################
#     # Case2. cdate만 존재
#     table_list = \
#     """
# """
#     tbl_list = table_list.replace("    ", "").replace("\n", "").split(",")
#     print(tbl_list)
#     for table_name in tbl_list:
#         df = pd.read_sql_query(f"SELECT * FROM {json_contents['drpnt_database']}.{table_name} WHERE DATE_FORMAT(CDATE,'%%Y%%m%%d')  BETWEEN '{start_day}' and '{end_day}';",con=conn)
#         # df에 있는 데이터(mysql)의 key가 snowflake에 있으면 지운다
#         df_key = pd.read_sql_query(
#             sql=f"show columns in table {json_contents['sf_db']}.{json_contents['sf_schema']}.O_{system_name}_{table_name};",
#             con=snow_conn)
#         select_string = ", ".join([df_key['column_name'][i] for _, i in enumerate(df_key.index.values.tolist()) if (df_key['null?'][i] == "NOT_NULL")])
#         key_name = select_string.lower()
#         for key_value in df[key_name]:
#             delete_query = f"DELETE FROM GCWB_WDB.ODS.O_{system_name}_{table_name} WHERE {key_name}={key_value}"
#             execute_delete_query_dpn(delete_query=delete_query)
#         df.to_csv(f'{os.path.join(file_path, table_name + ".csv")}', index=False, header=True, encoding='utf-8-sig')
#         upload_files_to_s3(upload_date=date.today().strftime("%y%m%d"), system_name=system_name,
#                            file=f"{table_name}.csv")
#         execute_insert_query(system_name=system_name, table_name=table_name, data_date=date.today().strftime("%y%m%d"))
#         execute_rownum_query(system_name=system_name, table_name=table_name)
    #######################################################################################################################################################
    # Case3. cdate와 udate모두 존재, KEY 하나
    # t_clinic_product, KEY2개
    # t_code,KEY2개
    table_list = \
    """
    T_CART,
    t_category,
    t_coupon,
    T_HEALTH_TOPIC,
    T_MEM_HEALTH,
    T_MEMBER,
    T_MEMBERSNS,
    T_MY_HEALTH,
    t_notice,
    t_pbanner,
    t_product,
    t_review,
    t_routine_order,
    t_special_exhibition
    """
    tbl_list = table_list.replace("    ", "").replace("\n", "").split(",")
    print(tbl_list)
    for table_name in tbl_list:
        df = pd.read_sql_query(f"SELECT * FROM {json_contents['drpnt_database']}.{table_name} where DATE_FORMAT(CDATE,'%%Y%%m%%d')  BETWEEN '{start_day}' and '{end_day}' or DATE_FORMAT(UDATE,'%%Y%%m%%d') BETWEEN '{start_day}' and '{end_day}';",con=conn)
        # df에 있는 데이터(mysql)의 key가 snowflake에 있으면 지운다
        df_key = pd.read_sql_query(
            sql=f"show columns in table {json_contents['sf_db']}.{json_contents['sf_schema']}.O_{system_name}_{table_name};",
            con=snow_conn)
        select_string = ", ".join([df_key['column_name'][i] for _, i in enumerate(df_key.index.values.tolist()) if (df_key['null?'][i] == "NOT_NULL")])
        key_name = select_string.lower()
        for key_value in df[key_name]:
            delete_query = f"DELETE FROM GCWB_WDB.ODS.O_{system_name}_{table_name} WHERE {key_name}='{key_value}'"
            execute_delete_query(delete_query=delete_query)
        df.to_csv(f'{os.path.join(file_path, table_name + ".csv")}', index=False, header=True, encoding='utf-8-sig')
        upload_files_to_s3(upload_date=date.today().strftime("%y%m%d"), system_name=system_name,
                           file=f"{table_name}.csv")
        execute_insert_query(system_name=system_name, table_name=table_name, data_date=date.today().strftime("%y%m%d"))
        execute_rownum_query(system_name=system_name, table_name=table_name)
    #######################################################################################################################################################
    # Case 2.1 cdate만 존재, key 2개 delete쿼리에 key_name 넣어서 delete
    table_name = "T_CLINIC_PRODUCT"
    df = pd.read_sql_query(f"SELECT * FROM {json_contents['drpnt_database']}.{table_name} where DATE_FORMAT(CDATE,'%%Y%%m%%d')  BETWEEN '{start_day}' and '{end_day}' or DATE_FORMAT(UDATE,'%%Y%%m%%d') BETWEEN '{start_day}' and '{end_day}';",con=conn)
    # df에 있는 데이터(mysql)의 key가 snowflake에 있으면 지운다
    for MEM_NO_val, PNO_val in zip(df['mem_no'], df['pno']):
        delete_query = f"DELETE FROM GCWB_WDB.ODS.O_{system_name}_{table_name} WHERE MEM_NO={MEM_NO_val} and PNO='{PNO_val}'"
        # print(delete_query)
        execute_delete_query(delete_query=delete_query)
    df.to_csv(f'{os.path.join(file_path, table_name + ".csv")}', index=False, header=True, encoding='utf-8-sig')
    upload_files_to_s3(upload_date=date.today().strftime("%y%m%d"), system_name=system_name,
                       file=f"{table_name}.csv")
    execute_insert_query(system_name=system_name, table_name=table_name, data_date=date.today().strftime("%y%m%d"))
    execute_rownum_query(system_name=system_name, table_name=table_name)
    #######################################################################################################################################################
    table_name = "T_CODE"
    df = pd.read_sql_query(
        f"SELECT * FROM {json_contents['drpnt_database']}.{table_name} where DATE_FORMAT(CDATE,'%%Y%%m%%d')  BETWEEN '{start_day}' and '{end_day}' or DATE_FORMAT(UDATE,'%%Y%%m%%d') BETWEEN '{start_day}' and '{end_day}';",
        con=conn)
    for CODE1_val, CODE2_val in zip(df['code1'], df['code2']):
        delete_query = f"DELETE FROM GCWB_WDB.ODS.O_{system_name}_{table_name} WHERE CODE1='{CODE1_val}' and CODE2='{CODE2_val}'"
        execute_delete_query(delete_query=delete_query)
    df.to_csv(f'{os.path.join(file_path, table_name + ".csv")}', index=False, header=True, encoding='utf-8-sig')
    upload_files_to_s3(upload_date=date.today().strftime("%y%m%d"), system_name=system_name,
                       file=f"{table_name}.csv")
    execute_insert_query(system_name=system_name, table_name=table_name, data_date=date.today().strftime("%y%m%d"))
    execute_rownum_query(system_name=system_name, table_name=table_name)
    #######################################################################################################################################################
    # Case3. cdate와 udate모두 존재

    table_name = "T_MCOUPON"
    df = pd.read_sql_query(
        f"SELECT * FROM {json_contents['drpnt_database']}.{table_name} where DATE_FORMAT(CDATE,'%%Y%%m%%d')  BETWEEN '{start_day}' and '{end_day}' or DATE_FORMAT(USE_DATE,'%%Y%%m%%d') BETWEEN '{start_day}' and '{end_day}';",
        con=conn)
    for mcouponid_val, couponid_val in zip(df['mcouponid'], df['couponid']):
        delete_query = f"DELETE FROM GCWB_WDB.ODS.O_{system_name}_{table_name} WHERE MCOUPONID='{mcouponid_val}' and COUPONID='{couponid_val}'"
        # print(delete_query)
        execute_delete_query(delete_query=delete_query)
    df.to_csv(f'{os.path.join(file_path, table_name + ".csv")}', index=False, header=True, encoding='utf-8-sig')
    upload_files_to_s3(upload_date=date.today().strftime("%y%m%d"), system_name=system_name,
                       file=f"{table_name}.csv")
    execute_insert_query(system_name=system_name, table_name=table_name, data_date=date.today().strftime("%y%m%d"))
    execute_rownum_query(system_name=system_name, table_name=table_name)

    #######################################################################################################################################################
    # 변경적재할 데이터 mysql에서 select하고 csv로 저장하여 s3에 저장. 변경적재할 데이터의 해당날짜의 데이터 모두 삭제하고 s3에 업로드 한 데이터 sf에 적재
    # t_order와 t_order_item에 date컬럼이 없어 조인하여 데이터 적재
    table_name = "T_ORDER_ITEM"
    select_query = f"""
    SELECT
        T1.ITEM_NO   -- 상품순번
      , T1.ORDERID   -- 주문아이디
      , T1.SHIP_NO   -- 배송순번
      , T1.PNO           -- 상품번호
      , T1.QTY           -- 수량
      , T1.PNAME   -- 상품명
      , T1.SALE_PRICE   -- 판매가
      , T1.MEM_PRICE   -- 회원가
      , T1.DISCOUNT   -- 상품 할인액
      , T1.APPLY_PRICE   -- 실판매가
      , T1.POINT   -- 지급포인트
      , T1.RETURN_QTY   -- 반품수량
      , T1.EXCHANGE_QTY   -- 교환수량
      , T1.MCOUPONID   -- 상품쿠폰아이디
      , T1.ORG_ITEM_NO   -- 원주문 상품순번
  FROM {json_contents['drpnt_database']}.{table_name} AS T1
 INNER JOIN (SELECT DISTINCT  ORDERID
               FROM PNTMALL.T_ORDER_STATUS_LOG
              WHERE DATE_FORMAT(CDATE,'%%Y%%m%%d') BETWEEN '{start_day}' AND '{end_day}'
            ) AS T2
   ON T1.ORDERID = T2.ORDERID
    """

    df = pd.read_sql_query(f"{select_query}", con=conn)
    print(df)
    df.to_csv(f'{os.path.join(file_path, table_name+".csv")}', index=False, header=True, encoding='utf-8-sig')
    upload_files_to_s3(upload_date=date.today().strftime("%y%m%d"), system_name=system_name, file=f"{table_name}.csv")
    df.to_csv(f'{os.path.join(file_path, table_name + ".csv")}', index=False, header=True, encoding='utf-8-sig')
    upload_files_to_s3(upload_date=date.today().strftime("%y%m%d"), system_name=system_name,
                       file=f"{table_name}.csv")
    for ITEM_NO_val in df['ITEM_NO']:
        delete_query = f"DELETE FROM GCWB_WDB.ODS.O_{system_name}_{table_name} WHERE ITEM_NO= '{ITEM_NO_val}'"
        execute_delete_query(delete_query=delete_query)
    execute_insert_query(system_name=system_name, table_name=table_name, data_date=date.today().strftime("%y%m%d"))
    execute_rownum_query(system_name=system_name, table_name=table_name)

    #######################################################################################################################################################
    table_name = "T_ORDER"
    select_query = f"""
    SELECT
           T1.ORDERID     -- 주문아이디
         , T1.GROUPID     -- 그룹아이디
         , T1.GUBUN             -- 구분 1:주문 2:교환 3:반품 4:재배송
         , T1.ORDER_GUBUN     -- 구분 1:일반배송 2:정기배송 3:병의원픽업 4:소분
         , T1.MEM_NO     -- 회원번호
         , T1.GRADE_NO     -- 등급 번호
         , T1.CLINIC_MEM_NO     -- 병의원 회원번호
         , T1.ONAME             -- 주문자명
         , T1.OMTEL1     -- 휴대폰1
         , T1.OMTEL2     -- 휴대폰2
         , T1.OTEL1             -- 전화1
         , T1.OTEL2             -- 전화2
         , T1.OEMAIL     -- 이메일
         , T1.AMT             -- 상품금액
         , T1.SHIP_AMT     -- 배송비
         , T1.TOT_AMT     -- 합계금액
         , T1.GRADE_DISCOUNT  -- 등급 총할인액
         , T1.COUPON_DISCOUNT -- 쿠폰 할인액
         , T1.SHIP_DISCOUNT     -- 배송비 총할인액
         , T1.TOT_DISCOUNT      -- 총할인액
         , T1.POINT             -- 포인트
         , T1.PAY_AMT     -- 결제금액
         , T1.PAY_TYPE     -- 결제타입
         , T1.DEVICE     -- 디바이스 P:PC, M:MOBILE, A:APP
         , T1.SHIP_MCOUPONID  -- 배송비 쿠폰아이디
         , T1.FIRST_ORDER_YN  -- 첫주문여부
         , T1.STATUS     -- 주문상태
         , T1.PICKUP_CLINIC     -- 픽업 병의원
         , T1.PICKUP_DATE     -- 픽업 방문일자
         , T1.PICKUP_TIME     -- 픽업 방문시간
         , T1.ESCROW     -- 에스크로
         , T1.ESCROW_TRAN     -- 에스크로 전송
         , T1.ODATE             -- 주문일
         , T1.ORG_ORDERID     -- 원주문아이디
      FROM {json_contents['drpnt_database']}.{table_name}  AS T1
     INNER JOIN (SELECT DISTINCT  ORDERID
                   FROM PNTMALL.T_ORDER_STATUS_LOG
                  WHERE DATE_FORMAT(CDATE,'%%Y%%m%%d') BETWEEN '{start_day}' AND '{end_day}'
                ) AS T2
       ON T1.ORDERID = T2.ORDERID
       """

    df = pd.read_sql_query(f"{select_query}", con=conn)
    df.to_csv(f'{os.path.join(file_path, table_name + ".csv")}', index=False, header=True, encoding='utf-8-sig')
    upload_files_to_s3(upload_date=date.today().strftime("%y%m%d"), system_name=system_name, file=f"{table_name}.csv")

    for orderid_val in df['ORDERID']:
        delete_query = f"DELETE FROM GCWB_WDB.ODS.O_{system_name}_{table_name} WHERE ORDERID = '{orderid_val}'"
        execute_delete_query(delete_query=delete_query)
    execute_insert_query(system_name=system_name, table_name=table_name, data_date=date.today().strftime("%y%m%d"))
    execute_rownum_query(system_name=system_name, table_name=table_name)
# sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError) (2006, "MySQL server has gone away (BrokenPipeError(32, 'Broken pipe'))")
def main():
    # 파라미터가 없을때 즉, yesterday만 가져올때, daily배치
    if len(sys.argv) == 1:
        print(len(sys.argv) == 1)
        start_day = yesterday
        end_day = yesterday
        dpn_daily(start_day = start_day.strftime("%Y%m%d"),
             end_day = end_day.strftime("%Y%m%d"))
    # 파라미터가 있을때 즉, date를 range로 넣어서 실행할때
    else:
        print("else")
        start_day = sys.argv[1]
        end_day = sys.argv[2]
        dpn_daily(start_day=datetime.date(int(start_day.split("-")[0]), int(start_day.split("-")[1]),
                                          int(start_day.split("-")[2])).strftime("%Y%m%d"),
                  end_day=datetime.date(int(end_day.split("-")[0]), int(end_day.split("-")[1]),
                                        int(end_day.split("-")[2]) + 1).strftime("%Y%m%d"))

if __name__ == "__main__":
    main()