# from bs4 import BeautifulSoup
import requests
import time
import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

base_url = 'http://medinfo.pref.tottori.lg.jp/'
search_base_url = 'https://medinfo.pref.tottori.lg.jp/ComDisp/search_01_input.php?Kind=3'
WAIT_SEC = 20

f = open("urls.txt", "a")

def start_driver():
    # Selenium用のウェブドライバーを初期化し、さまざまなオプションで安定した最適なパフォーマンスを得る。
    # Selenium用のChromeドライバーオプションを設定。
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-extensions')  # クリーンなブラウジングセッションのためにブラウザ拡張を無効にする。
    options.add_argument('--start-maximized')  # ブラウザを最大化したウィンドウで開始。参考: https://stackoverflow.com/a/26283818/1689770
    options.add_argument('--no-sandbox')  # 互換性向上のためにサンドボックスを無効にする。参考: https://stackoverflow.com/a/50725918/1689770
    options.add_argument('--disable-dev-shm-usage')  # より安定した動作のためにこのオプションを追加。参考: https://stackoverflow.com/a/50725918/1689770

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
            driver = webdriver.Chrome(service=Service(f'C:\\Users\\{USERNAME}\\.wdm\\drivers\\chromedriver\\win64\\116.0.5845.97\\chromedriver.exe'), options=options)
        except:
            driver = webdriver.Chrome(service=Service(f'C:\\Users\\{USERNAME}\\.wdm\\drivers\\chromedriver\\win64\\116.0.5845.96\\chromedriver.exe'), options=options)

    # ブラウザウィンドウを最大化。
    driver.maximize_window()
    # ウェブドライバの待機時間を設定。
    wait = WebDriverWait(driver, WAIT_SEC)
    return driver

def url_write(url):
    f.write(url+",\n")

def get_urls(driver, total_page):
    for page in range(1, total_page + 1):

        table_elements=driver.find_elements(By.CSS_SELECTOR, "table[class='comTblGyoumuCommon']")
        a_elements=table_elements[6].find_elements(By.TAG_NAME, 'a')[0::2]
        for a_el in a_elements:
            url=a_el.get_attribute('href')
            print(url)
            url_write(url, page)
    if len(driver.find_elements(By.XPATH, "//a[text()='次へ>']")) >0:
        btn_next=driver.find_element(By.XPATH, "//a[text()='次へ>']") 
        btn_next.click()
    else :
        driver.close()





def main():
    driver = start_driver()
    driver.maximize_window()
    driver.get(search_base_url)

    driver.find_element(By.XPATH, "//input[@type='submit']").click()
    time.sleep(5)

    element = driver.find_element(By.XPATH, "//select[@name='表示件数']")
    all_options = element.find_elements(By.TAG_NAME, "option")
    all_options[2].click()
    time.sleep(5)

    try:
        total_page_element = driver.find_element(By.XPATH, "//a[text()='>>']")
        href = total_page_element.get_attribute('href')
        match = re.search(r"javascript:on_events\('page',(\d+)\);", href)
        if match:
            total_page = int(match.group(1))
    except:
        print("not selected.")
        total_page = 6

    get_urls(driver, total_page)

    


if __name__ == '__main__':
    main()
