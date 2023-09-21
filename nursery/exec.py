from __future__ import print_function
from bs4 import BeautifulSoup
import requests
import csv

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

f = open("urls.txt", "r")

data = ['法人・施設名', '住所', 'アクセス', '仕事内容', 'サービス形態', '給与',
        '給与の備考', '待遇', '勤務時間', '休日', '長期休暇/特別休暇', 'url']
sheet_id = '1a9KLg9AINknBkaTOc0axFRc7RvVKtsTm-FVh2Yh-mzA'
base_url = 'https://job-medley.com'

fc = open('nursery.csv', 'a', newline='', encoding='utf-8')
# Create a CSV writer object
writer = csv.writer(fc)
# Write the data to the CSV file
writer.writerow(data)


def get_page_data(url):
    print(url)
    response = requests.get(url)
    return response


def get_html(html):
    soup = BeautifulSoup(html, 'lxml')
    return soup


def get_direct_data(soup):
    data = {}
    data['storename'] = soup.find('th', string='法人・施設名').find_next_sibling(
        'td').find('a').text if soup.find('th', string='法人・施設名') else ''
    data['work'] = soup.find('th', string='仕事内容').find_next_sibling('td').find(
        'p').text.replace('br', ' ') if soup.find('th', string='仕事内容') else ''
    data['address'] = soup.find('th', string='アクセス').find_next_sibling(
        'td').find('p').text if soup.find('th', string='アクセス') else ''
    data['access'] = soup.find('th', string='アクセス').find_next_sibling('td').find('div', {
        'class': 'o-gutter-row__item c-map c-map@desktop'}).find_next_sibling('div').find('p').text.replace('<br>', ' ') if soup.find('th', string='アクセス') else ''
    services = []
    data['service'] = ''
    if soup.find('th', string='診療科目・サービス形態'):
        services = soup.find('th', string='診療科目・サービス形態').find_next_sibling(
            'td').find('ul').findAll('li')
    for service in services:
        data['service'] = data['service'] + service.find('a').text + ' '
    data['salary'] = soup.find('th', string='給与').find_next_sibling(
        'td').text.strip().replace('\n', '') if soup.find('th', string='給与') else ''
    data['salary_notes'] = soup.find('th', string='給与の備考').find_next_sibling('td').find(
        'p').text.replace('<br>', ' ') if soup.find('th', string='給与の備考') else ''
    data['priority'] = soup.find('th', string='待遇').find_next_sibling('td').find(
        'p').text.replace('<br>', ' ') if soup.find('th', string='待遇') else ''
    data['working_hour'] = soup.find('th', string='勤務時間').find_next_sibling('td').find(
        'p').text.replace('<br>', ' ') if soup.find('th', string='勤務時間') else ''
    data['holiday'] = soup.find('th', string='休日').find_next_sibling('td').find(
        'p').text.replace('<br>', ' ') if soup.find('th', string='休日') else ''
    data['ls_vacation'] = soup.find('th', string='長期休暇・特別休暇').find_next_sibling('td').find(
        'p').text.replace('<br>', ' ') if soup.find('th', string='長期休暇・特別休暇') else ''
    return data


def get_hw_data(soup):
    data = {}
    office_info = soup.find(
        'div', {'class': 'c-segment__inner c-segment__inner--lid@desktop'})
    data['storename'] = office_info.find('th', string='事業所名').find_next_sibling(
        'td').text.strip() if office_info.find('th', string='事業所名') else ''
    data['address'] = office_info.find('th', string='住所').find_next_sibling(
        'td').text.strip() if office_info.find('th', string='住所') else ''
    data['access'] = office_info.find('th', string='アクセス').find_next_sibling(
        'td').text.strip() if office_info.find('th', string='アクセス') else ''

    job_info = soup.find('h2', string='募集内容').find_parent('div', {'class': 'o-gutter-row__item'}).find_next_sibling(
        'div', {'class': 'o-gutter-row__item'}).find('table', {'class': 'c-table'})
    data['work'] = job_info.find('th', string='仕事内容').find_next_sibling('td').find(
        'p').text.replace('br', ' ') if job_info.find('th', string='仕事内容') else ''
    data['salary'] = job_info.find('th', string='給与').find_next_sibling(
        'td').find('p').text if job_info.find('th', string='給与') else ''
    data['salary_notes'] = job_info.find('th', string='給与の備考').find_next_sibling('td').find(
        'p').text.replace('<br>', ' ') if job_info.find('th', string='給与の備考') else ''
    priorities = []
    data['priority'] = ''
    if job_info.find('th', string='待遇'):
        priorities = job_info.find(
            'th', string='待遇').find_next_sibling('td').findAll('p')
    for priority in priorities:
        data['priority'] = data['priority'] + priority.text + ' '
    working_hours = []
    data['working_hour'] = ''
    if job_info.find('th', string='勤務時間'):
        working_hours = job_info.find(
            'th', string='勤務時間').find_next_sibling('td').findAll('p')
    for working_hour in working_hours:
        data['working_hour'] = data['working_hour'] + working_hour.text + ' '
    data['holiday'] = '年間休日数 ' + job_info.find('th', string='年間休日数').find_next_sibling(
        'td').find('p').text if job_info.find('th', string='年間休日数') else ''

    print(data)


def csv_write(data, url):
    row = [
        data['storename'],
        data['address'],
        data['access'],
        data['work'],
        data['service'],
        data['salary'],
        data['salary_notes'],
        data['priority'],
        data['working_hour'],
        data['holiday'],
        data['ls_vacation'],
        url
    ]
    writer.writerow(row)


def append_values(spreadsheet_id, range_name, value_input_option,
                  _values):
    """
    Creates the batch_update the user has access to.
    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
        """
    creds, _ = google.auth.default()
    # pylint: disable=maybe-no-member
    try:
        service = build('sheets', 'v4', credentials=creds)

        values = [
            [
                # Cell values ...
            ],
            # Additional rows ...
        ]
        body = {
            'values': values
        }
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption=value_input_option, body=body).execute()
        print(f"{(result.get('updates').get('updatedCells'))} cells appended.")
        return result

    except HttpError as error:
        print(f"An error occurred: {error}")
        return error


def main():
    # for line in f:
    #     url = line.split(',')[0]
    #     # if not 'hw' in url :
    #     page_data = get_page_data(base_url+url)
    #     if page_data.status_code == 200:
    #         soup = get_html(page_data.text)
    #         data = get_direct_data(soup)
    #         csv_write(data, url)

    # fc.close()
    append_values(sheet_id, 'A1:L1', 'USER_ENTERED', data)


if __name__ == '__main__':
    main()
