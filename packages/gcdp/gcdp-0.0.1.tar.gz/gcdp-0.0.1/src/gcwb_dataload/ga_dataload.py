from datetime import date, timedelta
import datetime

from ..gcwb_sql.generate_query import execute_insert_query, execute_truncate_query, execute_delete_query
from commonlibs.utils import set_downloads_folder, get_downloads_folder, yesterday
from ..gcwb_s3.upload_objects import upload_files_to_s3
from gcwb_dataload.ga import DPN_AFFINITY, DPN_AGE, DPN_BEHAVIOR, DPN_CLIENT, DPN_CLIENT_CITY, DPN_GENDER, DPN_GOAL, DPN_ORDER, DPN_ORDER_PRODUCT, DPN_PAGE, DPN_PRODUCT, DPN_SEARCH, DPN_SOCIAL_MEDIUM
from gcwb_dataload.ga import PNT_AFFINITY, PNT_AGE, PNT_BEHAVIOR, PNT_CLIENT, PNT_CLIENT_CITY, PNT_GENDER, PNT_GOAL, PNT_ORDER, PNT_ORDER_PRODUCT, PNT_PAGE, PNT_PRODUCT, PNT_SEARCH, PNT_SOCIAL_MEDIUM

def main():
    system_name = "ga"
    set_downloads_folder(system_name)
    file_path = get_downloads_folder(system_name)
    for table_name in ["PNT_CLIENT", "PNT_CLIENT_CITY", "PNT_GENDER", "PNT_AGE", "PNT_AFFINITY", "PNT_PAGE",
                       "PNT_PRODUCT", "PNT_ORDER_PRODUCT", "PNT_SEARCH", "PNT_GOAL", "PNT_BEHAVIOR",
                       "PNT_SOCIAL_MEDIUM", "PNT_ORDER",
                       "DPN_CLIENT", "DPN_CLIENT_CITY", "DPN_GENDER", "DPN_AGE", "DPN_AFFINITY", "DPN_PAGE",
                       "DPN_PRODUCT", "DPN_ORDER_PRODUCT", "DPN_SEARCH", "DPN_GOAL", "DPN_BEHAVIOR",
                       "DPN_SOCIAL_MEDIUM", "DPN_ORDER"]:
        # for table_name in ["PNT_SOCIAL_MEDIUM", "DPN_SOCIAL_MEDIUM"]:
    # for table_name in ["DPN_AFFINITY"]:
        upload_files_to_s3(upload_date=datetime.date.today().strftime("%y%m%d"), system_name=system_name,
                           file=table_name + ".csv")
        execute_truncate_query(system_name=system_name, table_name=table_name)
        execute_insert_query(system_name=system_name, table_name=table_name, data_date=date.today().strftime("%y%m%d"))
        delete_query = f"DELETE FROM GCWB_WDB.ODS.O_{system_name}_{table_name} WHERE DATE LIKE '202206*';"
        execute_delete_query(delete_query)
    DPN_AFFINITY.main(start_day=datetime.date(2022, 6, 1), end_day=yesterday)
    DPN_AGE.main(start_day=datetime.date(2022, 6, 1), end_day=yesterday)
    DPN_BEHAVIOR.main(start_day=datetime.date(2022, 6, 1), end_day=yesterday)
    DPN_CLIENT.main(start_day=datetime.date(2022, 6, 1), end_day=yesterday)
    DPN_CLIENT_CITY.main(start_day=datetime.date(2022, 6, 1), end_day=yesterday)
    DPN_GENDER.main(start_day=datetime.date(2022, 6, 1), end_day=yesterday)
    DPN_GOAL.main(start_day=datetime.date(2022, 6, 1), end_day=yesterday)
    DPN_ORDER.main(start_day=datetime.date(2022, 6, 1), end_day=yesterday)
    DPN_ORDER_PRODUCT.main(start_day=datetime.date(2022, 6, 1), end_day=yesterday)
    DPN_PAGE.main(start_day=datetime.date(2022, 6, 1), end_day=yesterday)
    DPN_PRODUCT.main(start_day=datetime.date(2022, 6, 1), end_day=yesterday)
    DPN_SEARCH.main(start_day=datetime.date(2022, 6, 1), end_day=yesterday)
    DPN_SOCIAL_MEDIUM.main(start_day=datetime.date(2022, 6, 1), end_day=yesterday)

    PNT_AFFINITY.main(start_day=datetime.date(2022, 6, 1), end_day=yesterday)
    PNT_AGE.main(start_day=datetime.date(2022, 6, 1), end_day=yesterday)
    PNT_BEHAVIOR.main(start_day=datetime.date(2022, 6, 1), end_day=yesterday)
    PNT_CLIENT.main(start_day=datetime.date(2022, 6, 1), end_day=yesterday)
    PNT_CLIENT_CITY.main(start_day=datetime.date(2022, 6, 1), end_day=yesterday)
    PNT_GENDER.main(start_day=datetime.date(2022, 6, 1), end_day=yesterday)
    PNT_GOAL.main(start_day=datetime.date(2022, 6, 1), end_day=yesterday)
    PNT_ORDER.main(start_day=datetime.date(2022, 6, 1), end_day=yesterday)
    PNT_ORDER_PRODUCT.main(start_day=datetime.date(2022, 6, 1), end_day=yesterday)
    PNT_PAGE.main(start_day=datetime.date(2022, 6, 1), end_day=yesterday)
    PNT_PRODUCT.main(start_day=datetime.date(2022, 6, 1), end_day=yesterday)
    PNT_SEARCH.main(start_day=datetime.date(2022, 6, 1), end_day=yesterday)
    PNT_SOCIAL_MEDIUM.main(start_day=datetime.date(2022, 6, 1), end_day=yesterday)


if __name__ == "__main__":
    main()