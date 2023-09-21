from zenrows import ZenRowsClient
import requests
import time
import schedule

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium_recaptcha_solver import RecaptchaSolver
# from hcaptcha_solver import hCaptchaSolver

client = ZenRowsClient("fce7f0945bc72a9cac7f6914c82c6e1b712fa11c")
base_url = "http://validate.perfdrive.com/9cef9f4323c7ce9d8ffa8c6cfb36fd68/?ssa=257d2aa7-59b3-4e5c-9396-623ba0830977&ssb=21254240681&ssc=https%3A%2F%2Fwww.biccamera.com%2Fbc%2Fcategory%2F001%2F170%2F026%2F%3Fentr_nm%3D%2588%25AE%2589%25BB%2590%25AC%2583%257A%2581%255B%2583%2580%2583%2576%2583%258D%2583%255F%2583%254E%2583%2563%2581%2562Asahi%2520KASEI%257c%2593%258C%2597%256D%2583%2541%2583%258B%2583%257E%2583%2547%2583%2552%2581%255B%2583%2576%2583%258D%2583%255F%2583%254E%2583%2563%2581%2562TOYO%2520ALUMINIUM%2520EKCO%2520PRODUCTS%26rowPerPage%3D100&ssi=e95befc5-bmvn-4314-9815-6a54055cd6c5&ssk=support@shieldsquare.com&ssm=7950893325815988721703343427303638&ssn=3a8931c946483dec714bd9366649861d2929e17e24e3-b150-4343-8cb6b2&sso=198837a8-a26244d80c7876c30fbd544770f53e48268b4e9ccea4cc77&ssp=12772990821690470388169409303079744&ssq=14297270657051181043928893894379302513159&ssr=MTg4LjQzLjE0LjEz&sst=Mozilla/5.0%20(Windows%20NT%2010.0;%20Win64;%20x64)%20AppleWebKit/537.36%20(KHTML,%20like%20Gecko)%20Chrome/116.0.0.0%20Safari/537.36&ssu=&ssv=&ssw=&ssx=W10="
server_url = "https://zzkk28.com/api/v1"
WAIT_SEC = 20
f = open("test.txt", "ab")


def start_driver():
    # Selenium用のウェブドライバーを初期化し、さまざまなオプションで安定した最適なパフォーマンスを得る。
    # Selenium用のChromeドライバーオプションを設定。
    options = webdriver.ChromeOptions()
    # クリーンなブラウジングセッションのためにブラウザ拡張を無効にする。
    # options.add_argument("--headless")
    options.add_argument('--disable-extensions')
    # ブラウザを最大化したウィンドウで開始。参考: https://stackoverflow.com/a/26283818/1689770
    options.add_argument('--start-maximized')
    # 互換性向上のためにサンドボックスを無効にする。参考: https://stackoverflow.com/a/50725918/1689770
    options.add_argument('--no-sandbox')
    # より安定した動作のためにこのオプションを追加。参考: https://stackoverflow.com/a/50725918/1689770
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--ignore-certificate-errors")

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


def postcode(jancode, bc_id):
    data = {
        'jan_code': jancode,
        'bc_id': bc_id
    }
    print(data)
    response = requests.post(server_url+'/jan_code', json=data)
    print(response.status_code)


def get_jancode(driver, solver, bc_id):
    # driver.find_element(By.TAG_NAME, 'body')
    # wait = WebDriverWait(driver, 10)
    # wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'bcs_single')))
    print(len(driver.find_elements(By.CLASS_NAME, 'h-captcha')))
    if len(driver.find_elements(By.CLASS_NAME, 'h-captcha')) > 0:
        print(driver.page_source)
        hcaptcha_iframe = driver.find_element(
            By.XPATH, '//iframe[@title="Widget containing checkbox for hCaptcha security challenge"]')
        solver.click_recaptcha_v2(iframe=hcaptcha_iframe)
    content = driver.page_source
    print(len(content.split('bcs_single')))
    if len(content.split('bcs_single')) > 1:
        jancode = content.split("serGoodsStkNo : '")[1].split("'}")[0]
        postcode(jancode, bc_id)


def main():
    driver = start_driver()
    driver.maximize_window()
    solver = RecaptchaSolver(driver=driver)
    driver.get(base_url)
    if len(driver.find_elements(By.CLASS_NAME, 'h-captcha')) > 0:
        wait = WebDriverWait(driver, 40)
        # wait.until(EC.presence_of_element_located((By.ID, 'checkbox')))
        # checkbox = driver.find_element(By.ID, 'checkbox')
        # checkbox.click()
        # iframe = wait.until(
        #     EC.presence_of_element_located((By.TAG_NAME, 'iframe')))
        # driver.switch_to.frame(iframe)
        # checkbox = driver.find_element(By.ID, 'checkbox')
        # checkbox.click()
        # f.write(iframe.page_source.encode('utf-8'))
        # hcaptcha_iframe = wait.until(EC.presence_of_element_located(
        #     (By.XPATH, '//iframe[@title="Main content of the hCaptcha challenge"]')))
        hcaptcha_iframe = driver.find_element(
            By.XPATH, '//iframe[@title="Main content of the hCaptcha challenge"]')
        # driver.switch_to.frame(hcaptcha_iframe)
        solver.click_recaptcha_v2(iframe=hcaptcha_iframe)
        # response = client.get(url)
        # if response.status_code == 200:
        #     jancode = get_jancode(response.text, json_data[i]['bc_id'])
    # driver.close()
    time.sleep(100)


def test_sleep():
    print('sleep')
    time.sleep(3)


def test_main():
    print('loop')
    time.sleep(3)


if __name__ == '__main__':
    # main()
    # response = client.get(base_url)
    # f.write(response.text.encode('utf-8'))
    schedule.every().day.at("00:00").do(main)
    while True:
        schedule.run_pending()
        time.sleep(1)
