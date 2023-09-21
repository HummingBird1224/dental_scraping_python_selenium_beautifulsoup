# from bs4 import BeautifulSoup
import requests
import time
import csv

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys

login_url = 'https://job-medley.com/members/sign_in/'
base_url = 'https://job-medley.com/members/sign_in/'
WAIT_SEC = 20

f = open("hw_urls.txt", "r")

data = ['法人・施設名', '住所', 'アクセス', '仕事内容', 'サービス形態', '給与',
        '給与の備考', '待遇', '勤務時間', '休日', '長期休暇/特別休暇', 'url']

fc = open('hw_4000.csv', 'a', newline='', encoding='utf-8')
# Create a CSV writer object
writer = csv.writer(fc)
# Write the data to the CSV file
# writer.writerow(data)


def start_driver():
    # Selenium用のウェブドライバーを初期化し、さまざまなオプションで安定した最適なパフォーマンスを得る。
    # Selenium用のChromeドライバーオプションを設定。
    options = webdriver.ChromeOptions()
    # クリーンなブラウジングセッションのためにブラウザ拡張を無効にする。
    options.add_argument('--disable-extensions')
    # ブラウザを最大化したウィンドウで開始。参考: https://stackoverflow.com/a/26283818/1689770
    options.add_argument('--start-maximized')
    # 互換性向上のためにサンドボックスを無効にする。参考: https://stackoverflow.com/a/50725918/1689770
    options.add_argument('--no-sandbox')
    # より安定した動作のためにこのオプションを追加。参考: https://stackoverflow.com/a/50725918/1689770
    options.add_argument('--disable-dev-shm-usage')

    # 主処理
    try:
        driver_path = ChromeDriverManager().install()
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=options)

    except ValueError:
        # 最新バージョンのChromeドライバーを取得してインストール。
        url = r'https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json'
        response = requests.get(url)
        data_dict = response.json()
        latest_version = data_dict["channels"]["Stable"]["version"]

        driver_path = ChromeDriverManager(version=latest_version).install()
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=options)

    except PermissionError:  # 暫定処理 参考: https://note.com/yuu________/n/n14d97c155e5e
        try:
            driver = webdriver.Chrome(service=Service(
                f'C:\\Users\\{USERNAME}\\.wdm\\drivers\\chromedriver\\win64\\116.0.5845.97\\chromedriver.exe'), options=options)
        except:
            driver = webdriver.Chrome(service=Service(
                f'C:\\Users\\{USERNAME}\\.wdm\\drivers\\chromedriver\\win64\\116.0.5845.96\\chromedriver.exe'), options=options)

    # ブラウザウィンドウを最大化。
    driver.maximize_window()
    # ウェブドライバの待機時間を設定。
    wait = WebDriverWait(driver, WAIT_SEC)
    return driver


def auto_login(driver):
    email_field = driver.find_element(By.NAME, 'users2016_member[email]')
    password_field = driver.find_element(By.NAME, 'users2016_member[password]')
    email_field.send_keys('elen12241735@outlook.com')
    password_field.send_keys('admin123')
    password_field.send_keys(Keys.RETURN)


def csv_write(data, url):
    row = [
        data['storename'],
        data['address'],
        data['access'],
        data['work'],
        '',
        data['salary'],
        data['salary_notes'],
        data['priority'].replace('\u3000', ' '),
        data['working_hour'],
        data['holiday'],
        '',
        url
    ]
    writer.writerow(row)


def get_hw_data(driver):
    if len(driver.find_elements(By.XPATH, "//*[contains(text(), '404 not found')]")) == 0 and len(driver.find_elements(By.XPATH, "//*[contains(text(), '500 error')]")) == 0:
        data = {}
        office_info = driver.find_element(
            By.CSS_SELECTOR, "div[class='c-segment__inner c-segment__inner--lid@desktop']")
        data['storename'] = office_info.find_element(By.XPATH, "//th[text()='事業所名']").find_element(
            By.XPATH, 'following-sibling::td[1]').text.strip() if len(office_info.find_elements(By.XPATH, "//th[text()='事業所名']")) > 0 else ''
        data['address'] = office_info.find_element(By.XPATH, "//th[text()='住所']").find_element(
            By.XPATH, 'following-sibling::td[1]').text.strip() if len(office_info.find_elements(By.XPATH, "//th[text()='住所']")) > 0 else ''
        data['access'] = office_info.find_element(By.XPATH, "//th[text()='アクセス']").find_element(
            By.XPATH, 'following-sibling::td[1]').text.strip() if len(office_info.find_elements(By.XPATH, "//th[text()='アクセス']")) > 0 else ''

        job_info = driver.find_element(By.XPATH, "//h2[text()='募集内容']").find_element(By.XPATH, '..').find_element(
            By.XPATH, 'following-sibling::div[1]').find_element(By.CSS_SELECTOR, "table[class='c-table']")
        data['work'] = job_info.find_element(By.XPATH, "//th[text()='仕事内容']").find_element(By.XPATH, 'following-sibling::td[1]').find_element(
            By.TAG_NAME, 'p').text.replace('<br>', ' ') if len(job_info.find_elements(By.XPATH, "//th[text()='仕事内容']")) > 0 else ''
        data['salary'] = job_info.find_element(By.XPATH, "//th[text()='給与']").find_element(By.XPATH, 'following-sibling::td[1]').find_element(
            By.TAG_NAME, 'p').text if len(job_info.find_elements(By.XPATH, "//th[text()='給与']")) > 0 else ''
        data['salary_notes'] = job_info.find_element(By.XPATH, "//th[text()='給与の備考']").find_element(By.XPATH, 'following-sibling::td[1]').find_element(
            By.TAG_NAME, 'p').text.replace('<br>', ' ') if len(job_info.find_elements(By.XPATH, "//th[text()='給与の備考']")) > 0 else ''
        priorities = []
        data['priority'] = ''
        if len(job_info.find_elements(By.XPATH, "//th[text()='待遇']")) > 0:
            priorities = job_info.find_element(By.XPATH, "//th[text()='待遇']").find_element(
                By.XPATH, 'following-sibling::td[1]').find_elements(By.TAG_NAME, 'p')
        for priority in priorities:
            data['priority'] = data['priority'] + priority.text + ' '
        working_hours = []
        data['working_hour'] = ''
        if len(job_info.find_elements(By.XPATH, "//th[text()='勤務時間']")) > 0:
            working_hours = job_info.find_element(By.XPATH, "//th[text()='勤務時間']").find_element(
                By.XPATH, 'following-sibling::td[1]').find_elements(By.TAG_NAME, 'p')
        for working_hour in working_hours:
            data['working_hour'] = data['working_hour'] + \
                working_hour.text + ' '
        data['holiday'] = '年間休日数 ' + job_info.find_element(By.XPATH, "//th[text()='年間休日数']").find_element(By.XPATH, 'following-sibling::td[1]').find_element(
            By.TAG_NAME, 'p').text if len(job_info.find_elements(By.XPATH, "//th[text()='年間休日数']")) > 0 else ''
        return data


def get_page_data(driver, urls):
    # for url in urls:
    for i in range(4000, 5000):
        # print(urls)
        # driver.get(url)
        print(urls[i])
        driver.get(urls[i])
        data = get_hw_data(driver)
        if data is not None:
            # csv_write(data, url)
            csv_write(data, urls[i])
    fc.close()
    driver.close()
    return 'close'


def main():
    driver = start_driver()
    driver.maximize_window()
    driver.get(login_url)
    auto_login(driver)
    urls = f.read().split(',')
    total_num = len(urls)
    print(total_num)
    page_data = get_page_data(driver, urls)
    print(page_data)
    time.sleep(total_num*10)


if __name__ == '__main__':
    main()
