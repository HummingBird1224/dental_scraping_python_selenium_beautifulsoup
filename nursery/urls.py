# from bs4 import BeautifulSoup
import requests
from bs4 import BeautifulSoup
import re

base_url = 'https://job-medley.com/cw/childcare/?employment_type%5B%5D=3&page='

f = open("urls.txt", "a")


def get_page_data(url):
    response = requests.get(url)
    return response


def get_html(html):
    soup = BeautifulSoup(html, 'lxml')
    return soup


def url_write(url):
    f.write(url+",\n")


def main():
    top_page_data = get_page_data(base_url)
    if top_page_data.status_code == 200:
        soup = get_html(top_page_data.text)
        top_page = soup.find("a", string="次へ").find_previous_sibling(
            'ul').findAll('li')[-1].text
        top_page = int(top_page)
        print(top_page)

    name_pattern = re.compile(r'\s*保育士の求人\s*')
    content_pattern = r'^\s*パート・バイト'
    if top_page is not None:
        for page in range(1, top_page+1):
            print(page)
            page_data = get_page_data(base_url+str(page))
            if page_data.status_code == 200:
                soup = get_html(page_data.text)
                cw_names = soup.findAll('p', string=name_pattern)
                for cw_name in cw_names:
                    cw_content = cw_name.find_parent(
                        'dt').find_next_sibling('dd').text
                    if re.match(content_pattern, cw_content):
                        cw_url = cw_name.find_parent(
                            'a', {'class': 'c-facility-card__list-link'}).get('href')
                        print(cw_url)
                        url_write(cw_url)
    f.close()
    print('done')


if __name__ == '__main__':
    main()
