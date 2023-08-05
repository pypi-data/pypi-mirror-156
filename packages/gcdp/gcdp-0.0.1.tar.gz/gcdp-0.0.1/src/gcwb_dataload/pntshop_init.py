import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys

import time
import os


from commonlibs.utils import get_downloads_folder, set_downloads_folder, json_contents, project_path
from ..gcwb_s3.upload_objects import upload_files_to_s3


from datetime import date
from ..gcwb_sql.generate_query import execute_truncate_query, execute_insert_query
import shutil

system_name = "pnt"
# https://stackoverflow.com/questions/42403907/how-to-round-remove-trailing-0-zeros-in-pandas-column
def godomall_crawler(tables_list):
    url = 'https://www.nhn-commerce.com/'

    download_folder_fullpath = set_downloads_folder(system_name="pnt")
    chrome_options = webdriver.ChromeOptions()

    prefs = {'download.default_directory': download_folder_fullpath}
    chrome_options.add_experimental_option('prefs', prefs)

    chrome_options.headless = True
    # chrome_options.headless = False
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(url)

    login_click = driver.find_element(By.XPATH, '//*[@id="btn-gnb-login"]')
    login_click.click()

    id_input_box = driver.find_element(By.XPATH, '//*[@id="godoID"]')
    # /html/body/div[2]/div/div/div[1]/div/form/div[1]/div[1]/div/input
    pwd_input_box = driver.find_element(By.XPATH, '//*[@id="godoPwd"]')
    # /html/body/div[2]/div/div/div[1]/div/form/div[1]/div[2]/div/input
    submit_button = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[1]/div/div[4]/a')
    # /html/body/div[2]/div/div/div[1]/div/div[4]/a
    # 통합로그인 버튼이 새로 생겨서 xpath값 변경됩

    id_input_box.clear()
    pwd_input_box.clear()

    time.sleep(2)
    id_input_box.send_keys(json_contents["godomall_id"])
    time.sleep(3)
    pwd_input_box.send_keys(json_contents["godomall_pwd"])
    time.sleep(3)

    submit_button.click()

    time.sleep(3)

    manage_bt = driver.find_element(By.XPATH, '/html/body/div[3]/div[1]/div/div[2]/div/div[2]/ul/li[3]/a')
    manage_bt.click()
    time.sleep(3)

    mall_manage_bt = driver.find_element(By.XPATH, '//*[@id="container_right"]/table/tbody/tr[4]/td[7]/img')
    mall_manage_bt.click()
    time.sleep(3)

    db_manage_bt = driver.find_element(By.XPATH, '//*[@id="phpmyadminPop"]')
    db_manage_bt.click()
    time.sleep(3)

    php_pwd_input_box = driver.find_element(By.XPATH, '//*[@id="ip_passwd"]')
    php_pwd_input_box.clear()
    php_pwd_input_box.send_keys(json_contents["godomall_pwd"])
    time.sleep(3)

    php_submit_bt = driver.find_element(By.XPATH, '//*[@id="openConnect"]')
    php_submit_bt.click()
    time.sleep(10)

    #php
    popup = driver.window_handles
    driver.switch_to.window(popup.pop())
    php_address = driver.current_url

    driver.get(php_address)
    # LOGIN
    id_input_box = driver.find_element(By.XPATH, '//*[@id="input_username"]')
    pwd_input_box = driver.find_element(By.XPATH, '//*[@id="input_password"]')
    submit_button = driver.find_element(By.XPATH, '//*[@id="input_go"]')

    id_input_box.clear()
    pwd_input_box.clear()

    time.sleep(2)
    id_input_box.send_keys(json_contents["pntshop_id"])
    time.sleep(3)
    pwd_input_box.send_keys(json_contents["pntshop_pwd"])
    time.sleep(3)

    submit_button.click()
    time.sleep(3)
    # for xpath in table_xpath:
    for link_text in tables_list:
        # gcwbhb0314_godomall_com DB클릭
        db = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/div[3]/ul/li[2]/a')
        db.send_keys(Keys.ENTER)
        time.sleep(3)

        # # export table검색
        # table_name = driver.find_element(By.XPATH, '/html/body/div[4]/div[2]/fieldset/div/input')
        # table_name.send_keys(tbl)
        # time.sleep(5)

        # export table인 검색 1번째 항목 es_member클릭
        # table_click = driver.find_element(By.XPATH, f'{xpath}')
        # driver.execute_script("arguments[0].click();", table_click)
        # time.sleep(3)

        print(link_text)
        table_click = driver.find_element(By.LINK_TEXT, f"{link_text}")
        driver.execute_script("arguments[0].click();", table_click)
        time.sleep(3)

        # 내보내기 클릭
        export_menu = driver.find_element(By.XPATH, '//*[@id="topmenu"]/li[6]/a')
        export_menu.click()
        time.sleep(3)

        # 내보내기 옵션1. 내보내기 방법 커스텀 클릭
        wait = WebDriverWait(driver, 20)
        # combo_box = driver.find_element(By.XPATH, '/html/body/div[4]/form/div[1]/ul/li[2]/input')
        combo_box = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[4]/form/div[1]/ul/li[2]/input')))
        # driver.execute_script("arguments[0].click();", combo_box)
        combo_box.click()
        time.sleep(3)

        # 내보내기 옵션2. 형식 CSV 클릭
        ### 파일 형식 클릭 메뉴가 나타날때까지 로드하는 것을 기다렸다가(EC) 클릭
        export_type = wait.until(
            EC.visibility_of_element_located((By.XPATH, '/html/body/div[4]/form/div[2]/select/option[2]')))
        export_type.click()
        time.sleep(5)

        # 내보내기 옵션2. 파일 문자셋 utf16클릭
        file_type = driver.find_element(By.XPATH, '/html/body/div[4]/form/div[6]/ul/li[3]/ul/li[2]/select/option[24]')
        file_type.click()
        time.sleep(5)

        # 실행클릭
        execute_button = driver.find_element(By.XPATH, '//*[@id="buttonGo"]')
        driver.execute_script("arguments[0].click();", execute_button)
        # execute_button.click()
        time.sleep(5)

        downloads_done()

    driver.close()

    return php_address

def downloads_done():
    print(os.listdir(get_downloads_folder(system_name)))
    wait = True
    while wait:
        print("Wait..")
        for file in os.listdir(get_downloads_folder(system_name)):
            if ".crdownload" in file:
                time.sleep(5)
                print("Wait..")
                wait = True
            else:
                # print("Done..")
                wait = False
    print("Done..")


def modify_csv(filefullpath):
    for filename in os.listdir(filefullpath):
        print(filename)
        df = pd.read_csv(os.path.join(filefullpath, filename), encoding='utf-16', header=None, dtype=object)
        df.iloc[:,0] = df.iloc[:,0].apply(lambda x : x.replace("\ufeff","").replace("\"", ""))
        df.fillna('NULL')
        # DF.to_csv(os.path.join(set_downloads_folder("pnt"), filename), index=False, encoding='utf-8')
        df.to_csv(os.path.join(set_downloads_folder("pnt"), filename), index=False)

if __name__ == "__main__":
    # if (os.path.isdir(get_downloads_folder("pnt"))):
    #     shutil.rmtree(get_downloads_folder("pnt"))
    # pnt샵의 myadmin이 로그인이 되지 않아 우선 크롤링을 성공했던 19일 기준의 데이터로 작업을 하였다. 크롤링이 가능하면 modify_csv파일의 날짜를 변경 필요
    # print(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
    df = pd.read_excel(f"{project_path}/gcwb_dataload/code/pnt_table_list.xlsx", index_col=False)
    table_list = df['table_list']
    print(table_list)
    godomall_crawler(tables_list = table_list)
    modify_csv(get_downloads_folder("pnt"))

    for table_name in table_list:
        upload_files_to_s3(upload_date=date.today().strftime('%y%m%d'), system_name=system_name, file=table_name+".csv")
        execute_truncate_query(system_name=system_name, table_name=table_name)
        try:
            execute_insert_query(system_name=system_name, table_name=table_name, data_date=date.today().strftime('%y%m%d'))
            print("success")
        except Exception as e:
            print(f"ERROR: {e}")

    # 특정테이블만 초기적재 하고 싶을때 이코드 실행
    # table_name = "es_logOrder"
    # upload_files_to_s3(upload_date=date.today().strftime('%y%m%d'), system_name=system_name, file=table_name + ".csv")
    # execute_truncate_query(system_name=system_name, table_name=table_name)
    # try:
    #     execute_insert_query(system_name=system_name, table_name=table_name, data_date=date.today().strftime('%y%m%d'))
    #     print("success")
    # except Exception as e:
    #     print(f"ERROR: {e}")