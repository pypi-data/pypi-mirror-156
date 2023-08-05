import os
from datetime import date, timedelta
from sqlalchemy import create_engine, text
import json
import pandas as pd
import snowflake.connector
import numpy as np


yesterday = date.today() - timedelta(days=1)

project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

with open(f"{project_path}/secret.json", "r") as fp:
    json_contents=json.loads(fp.read())

def set_downloads_folder(system_name):
    """
    set downloads folder
    system_name = "pnt"||"dpn"
    :param system_name: 
    :return: 
    """
    # project폴더의 하위downloads폴더
    downloads_folder = os.path.join(project_path, "downloads")
    system_folder = os.path.join(downloads_folder, system_name)
    today_folder = os.path.join(system_folder, date.today().strftime('%y%m%d'))
    download_folder_fullpath = today_folder
    if not os.path.exists(downloads_folder):
        os.makedirs(downloads_folder)
    if not os.path.exists(system_folder):
        os.makedirs(system_folder)
    if not os.path.exists(today_folder):
        os.makedirs(today_folder)

    print(f"{download_folder_fullpath} download folder fullpath: {download_folder_fullpath}")
    return download_folder_fullpath

def get_downloads_folder(system_name):
    download_folder_fullpath = os.path.join(os.path.join(os.path.join(project_path, "downloads"), system_name), date.today().strftime('%y%m%d'))
    # print(f"{system_name} download folder fullpath: {system_folder}")
    return download_folder_fullpath

def convert_csv(table_name):
    csv_filepath = f"{os.path.join(get_downloads_folder('pnt'),f'{table_name}.csv')}"
    df = pd.read_csv(csv_filepath, encoding='utf-16', header=None)
    df[0] = df[0].str.replace('"', '').encode('ascii', 'ignore')
    print(df)
    df.to_csv(os.path.join(get_downloads_folder('pnt'),f'{table_name}.csv'), index=False, header=None, encoding='utf-8', sep=";")

def remove_index_from_csv():
    filespath = get_downloads_folder("ga")
    print(filespath)
    for file in os.listdir(filespath):
        src_filefullpath = os.path.join(filespath, file)
        print(src_filefullpath)
        df = pd.read_csv(src_filefullpath, index_col=[0])
        print(df)
        target_filefullpath = os.path.join(filespath, "mod_"+file)
        df.to_csv(target_filefullpath, index=False)

def get_max_length(table_name):
    connection_string = f'snowflake://{json_contents["sf_user"]}:{json_contents["sf_password"]}@{json_contents["sf_account"]}/{json_contents["sf_database"]}/{json_contents["sf_schema"]}?warehouse={json_contents["sf_warehouse"]}&role={json_contents["sf_role"]}'
    conn = create_engine(connection_string)

    df = pd.read_sql_query(f"select * from {json_contents['sf_database']}.{json_contents['sf_schema']}.{table_name}", con=conn)
    measurer = np.vectorize(len)
    res = dict(zip(df, measurer(df.values.astype(str)).max(axis=0)))
    print(res)

def get_max_length_huge(table_name="O_GA_DPN_PAGE"):
    connection_string = f'snowflake://{json_contents["sf_user"]}:{json_contents["sf_password"]}@{json_contents["sf_account"]}/{json_contents["sf_database"]}/{json_contents["sf_schema"]}?warehouse={json_contents["sf_warehouse"]}&role={json_contents["sf_role"]}'
    conn = create_engine(connection_string)

    df = pd.read_sql_query(f"select * from {json_contents['sf_database']}.{json_contents['sf_schema']}.{table_name}", con=conn)
    maxColumnLenghts = []
    for col in range(len(df.columns)):
        maxColumnLenghts.append(max(df.iloc[:, col].astype(str).apply(len)))
    print('Max Column Lengths ', maxColumnLenghts)
    return maxColumnLenghts


import glob
def concat_csv():
    service_name = "PNT_SEARCH"
    folderpath = f"D:\\GitHub\\dataeng\\libs\\gcdp\\downloads\\220613\\{service_name}\\"
    # ["PNT_CLIENT", "PNT_CLIENT_CITY", "PNT_GENDER", "PNT_AGE", "PNT_AFFINITY", "PNT_PAGE", "PNT_PRODUCT", "PNT_ORDER_PRODUCT", "PNT_SEARCH", "PNT_GOAL", "PNT_BEHAVIOR", "PNT_SOCIAL_MEDIUM", "PNT_ORDER"]:
    # ["DPN_CLIENT", "DPN_CLIENT_CITY", "DPN_GENDER", "DPN_AGE", "DPN_AFFINITY", "DPN_PAGE", "DPN_PRODUCT", "DPN_ORDER_PRODUCT", "DPN_SEARCH", "DPN_GOAL", "DPN_BEHAVIOR", "DPN_SOCIAL_MEDIUM", "DPN_ORDER"]:

    # with open(f"D:\\GitHub\\dataeng\\libs\\gcdp\\downloads\\Archive\\TEST\\PNT_GENDER\\PNT_GENDER.csv", 'a+', encoding='utf-8') as out_csvfile:
    fout = open(os.path.join(folderpath, f"{service_name}.csv"), "a", encoding='utf-8')
    for line in open(os.path.join(folderpath,f"{service_name}_1.csv"), encoding='utf-8'):
        fout.write(line)

    for num in range(2, 10):
        f = open(os.path.join(folderpath,f"{service_name}_"+str(num)+".csv"), encoding='utf-8')
        f.__next__()
        for line in f:
            fout.write(line)
        f.close()
    fout.close()

if __name__ == "__main__":
#     for table_name in ["O_GA_PNT_CLIENT", "O_GA_PNT_CLIENT_CITY", "O_GA_PNT_GENDER", "O_GA_PNT_AGE", "O_GA_PNT_AFFINITY", "O_GA_PNT_PAGE", "O_GA_PNT_ORDER", "O_GA_PNT_PRODUCT", "O_GA_PNT_ORDER_PRODUCT", "O_GA_PNT_SEARCH", "O_GA_PNT_BEHAVIOR", "O_GA_PNT_SOCIAL_MEDIUM", "O_GA_DPN_CLIENT", "O_GA_DPN_CLIENT_CITY", "O_GA_DPN_GENDER", "O_GA_DPN_AGE", "O_GA_DPN_AFFINITY",  "O_GA_DPN_ORDER", "O_GA_DPN_PRODUCT", "O_GA_DPN_ORDER_PRODUCT", "O_GA_DPN_SEARCH", "O_GA_DPN_GOAL", "O_GA_DPN_BEHAVIOR", "O_GA_DPN_SOCIAL_MEDIUM"]:
#         print(table_name)
#         get_max_length(table_name)
#     get_max_length_huge()
    concat_csv()

    # print(2046+2021+2544+2349+2498+564+2046+1949)
    print(2666+4442+7122+3121+2658+25+1360+1302)
    print(1844+2990+5617+1671+1309+30+1156+696)