import requests
import time
import csv
from normalize_japanese_addresses import normalize

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

WAIT_SEC = 20

f = open("urls_test.txt", "r")

data = ['storename', 'address_original', 'address_normalize[0]', 'address_normalize[1]', '最終更新日', 'url',
        '開設者種別', '開設者名', '管理者名', '歯科一般領域一覧', '歯科口腔外科領域一覧', '小児歯科領域一覧', '矯正歯科領域一覧',
        '施設状況一覧', '対応可能ﾅ麻酔治療一覧', '在宅医療', '連携ﾉ有無', '歯科医師(総数|常勤|非常勤)', '歯科技工士(総数|常勤|非常勤)',
        '歯科助手(総数|常勤|非常勤)', '歯科衛生士(総数|常勤|非常勤)', '前年度1日平均外来患者数', '緯度', '経度', 'page']

fc = open('yamanashi.csv', 'a', newline='', encoding='utf-8')
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
                f'C:\\Users\\{USERNAME}\\.wdm\\drivers\\chromedriver\\win64\\116.0.5845.141\\chromedriver.exe'), options=options)
        except:
            driver = webdriver.Chrome(service=Service(
                f'C:\\Users\\{USERNAME}\\.wdm\\drivers\\chromedriver\\win64\\116.0.5845.140\\chromedriver.exe'), options=options)

    # ブラウザウィンドウを最大化。
    driver.maximize_window()
    # ウェブドライバの待機時間を設定。
    wait = WebDriverWait(driver, WAIT_SEC)
    return driver


def get_base_data(html):
    baseData = {}
    baseData['storename'] = html.find_element(By.ID, 'lblKikanName').text if len(
        html.find_elements(By.ID, 'lblKikanName')) > 0 else '-'
    baseData['updated_at'] = html.find_element(By.ID, 'lblLastUpdate').text.split(
        ' ')[0] if len(html.find_elements(By.ID, 'lblLastUpdate')) > 0 else '-'
    baseData['address'] = html.find_element(By.ID, 'lblLocationName').text if len(
        html.find_elements(By.ID, 'lblLocationName')) > 0 else '-'
    try:
        storeAddressNormalize = "".join(
            list(normalize(baseData['address']).values())[0:4])
        baseData['address_normalize_1'] = _split_buildingName(storeAddressNormalize)[
            0]
        baseData['address_normalize_2'] = _split_buildingName(storeAddressNormalize)[
            1]
    except:
        baseData['address_normalize_1'] = baseData['address_normalize_2'] = "na"
    baseData['founder_name'] = html.find_element(By.ID, 'lblKaisetsuName').text.replace(
        '\u3000', ' ') if len(html.find_elements(By.ID, 'lblKaisetsuName')) > 0 else '-'
    baseData['admin_name'] = html.find_element(By.ID, 'lblKanriName').text.replace(
        '\u3000', ' ') if len(html.find_elements(By.ID, 'lblKanriName')) > 0 else '-'
    return baseData


def get_amenity_data(html):
    true_elements = html.find_elements(By.XPATH, "//td[text()='有り']")
    span_elements = html.find_elements(By.XPATH, "//span[text()='有り']")
    if len(span_elements) > 0:
        for s_el in span_elements:
            true_elements.append(s_el.find_element(By.XPATH, '..'))

    if len(true_elements) > 0:
        amenityData = []
        for t_el in true_elements:
            service = t_el.find_element(
                By.XPATH, "./preceding-sibling::td[1]").find_element(By.TAG_NAME, 'span').text
            amenityData.append(service)
    else:
        amenityData = 'na'

    return amenityData


def get_contents_data(html):
    contentsData = {}
    general_elements = []
    if len(html.find_elements(By.XPATH, "//span[contains(text(), '歯科領域')]")) > 0:
        general_ancestor = html.find_element(
            By.XPATH, "//span[contains(text(), '歯科領域')]").find_element(By.XPATH, './ancestor::table[1]')
        general_elements = general_ancestor.find_element(
            By.XPATH, "following-sibling::table").find_elements(By.ID, 'lblIryokinoName')
    if len(general_elements) > 0:
        general_dentistry = []
        for g_el in general_elements:
            general_dentistry.append(g_el.text)
    else:
        general_dentistry = 'na'
    contentsData['general_dentistry'] = general_dentistry

    oral_elements = []
    if len(html.find_elements(By.XPATH, "//span[contains(text(), '口腔外科領域')]")) > 0:
        oral_ancestor = html.find_element(
            By.XPATH, "//span[contains(text(), '口腔外科領域')]").find_element(By.XPATH, './ancestor::table[1]')
        oral_elements = oral_ancestor.find_element(
            By.XPATH, "following-sibling::table").find_elements(By.ID, 'lblIryokinoName')
    if len(oral_elements) > 0:
        oral_surgery = []
        for o_el in oral_elements:
            oral_surgery.append(o_el.text)
    else:
        oral_surgery = 'na'
    contentsData['oral_surgery'] = oral_surgery

    homecare_elements = []
    if len(html.find_elements(By.XPATH, "//span[contains(text(), '在宅医療') and @id='lblZaitakuiryo']")) > 0:
        homecare_elements = html.find_element(By.XPATH, "//span[contains(text(), '在宅医療') and @id='lblZaitakuiryo']").find_element(
            By.XPATH, "following-sibling::table").find_elements(By.ID, "lblZaitakuiryoName")
    if len(homecare_elements) > 0:
        homecare = []
        for h_el in homecare_elements:
            homecare.append(h_el.text)
    else:
        homecare = 'na'
    contentsData['homecare'] = homecare

    collaboration_elements = []
    if len(html.find_elements(By.XPATH, "//span[contains(text(), '連携の有無') and @id='lblZaitakuiryo']")) > 0:
        collaboration_elements = html.find_element(By.XPATH, "//span[contains(text(), '連携の有無') and @id='lblZaitakuiryo']").find_element(
            By.XPATH, "following-sibling::table").find_elements(By.ID, "lblZaitakuiryoName")
    if len(collaboration_elements) > 0:
        collaboration = []
        for c_el in collaboration_elements:
            collaboration.append(c_el.text)
    else:
        collaboration = 'na'
    contentsData['collaboration'] = collaboration

    return contentsData


def get_actual_data(html):
    actualData = {}
    if len(html.find_elements(By.XPATH, "//span[text()='歯科医師']")) > 0:
        dentist_ancestor = html.find_element(
            By.XPATH, "//span[text()='歯科医師']").find_element(By.XPATH, './ancestor::tr[@id="trJininhaichi"]')
        den_total = dentist_ancestor.find_element(By.ID, 'lblSoSouSu').text
        den_full = dentist_ancestor.find_element(By.ID, 'lblJoSouSu').text
        den_part = dentist_ancestor.find_element(By.ID, 'lblHjSouSu').text
        actualData['dentist'] = den_total+'|' + den_full + '|' + den_part
    else:
        actualData['dentist'] = 'na'

    if len(html.find_elements(By.XPATH, "//span[text()='歯科衛生士']")) > 0:
        hygienist_ancestor = html.find_element(
            By.XPATH, "//span[text()='歯科衛生士']").find_element(By.XPATH, './ancestor::tr[@id="trJininhaichi"]')
        hyg_total = hygienist_ancestor.find_element(By.ID, 'lblSoSouSu').text
        hyg_full = hygienist_ancestor.find_element(By.ID, 'lblJoSouSu').text
        hyg_part = hygienist_ancestor.find_element(By.ID, 'lblHjSouSu').text
        actualData['dental_hygienist'] = hyg_total + \
            '|' + hyg_full + '|' + hyg_part
    else:
        actualData['dental_hygienist'] = 'na'

    if len(html.find_elements(By.ID, "pnlGairaiKanjyasu")) > 0 and len(html.find_elements(By.ID, "tblGairaiKanjyasu")) > 0:
        actualData['day_patients'] = html.find_element(By.ID, "pnlGairaiKanjyasu").find_element(
            By.XPATH, 'table[@id="tblGairaiKanjyasu"]').find_element(By.TAG_NAME, 'tr').find_elements(By.TAG_NAME, 'td')[1].text
    else:
        actualData['day_patients'] = 'na'

    return actualData


def main():
    driver = start_driver()
    driver.maximize_window()
    for line in f:
        page = line.split(',')[0]
        url = line.split(',')[1]
        print(url)
        driver.get(url)
        data = {}

        baseData = get_base_data(driver)
        if baseData:
            btn_tabs = driver.find_elements(
                By.CSS_SELECTOR, 'a[class="DetailHyper"]')
            btn_tabs[1].click()

        amenityData = get_amenity_data(driver)
        if amenityData:
            btn_tabs = driver.find_elements(
                By.CSS_SELECTOR, 'a[class="DetailHyper"]')
            btn_tabs[3].click()

        contentsData = get_contents_data(driver)
        if contentsData:
            btn_tabs = driver.find_elements(
                By.CSS_SELECTOR, 'a[class="DetailHyper"]')
            btn_tabs[4].click()

        actualData = get_actual_data(driver)
        if actualData:
            data = [
                baseData['storename'],
                baseData['address'],
                baseData['address_normalize_1'],
                baseData['address_normalize_2'],
                baseData['updated_at'],
                url,
                'na',
                baseData['founder_name'],
                baseData['admin_name'],
                contentsData['general_dentistry'],
                contentsData['oral_surgery'],
                'na',
                'na',
                amenityData,
                'na',
                contentsData['homecare'],
                contentsData['collaboration'],
                actualData['dentist'],
                'na',
                'na',
                actualData['dental_hygienist'],
                actualData['day_patients'],
                'na',
                'na',
                page
            ]
            writer.writerow(data)

    fc.close()
    driver.close()
    time.sleep(5000)


if __name__ == '__main__':
    main()
