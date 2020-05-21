import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium import webdriver
import time


def get_data():
    url = "https://boxofficevietnam.com/"
    # Mac setup
    # browser = webdriver.Chrome()

    # Ubuntu setup
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    browser = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver', options=chrome_options)

    # Getting data from url
    browser.get(url)
    time.sleep(9)
    html = browser.page_source
    soup = BeautifulSoup(html, 'lxml')
    table_tag = soup.find('table', attrs={"id": "table_1"})
    table_body_tag = table_tag.find('tbody')
    data = []
    for tr in table_body_tag.findAll('tr'):
        row = []
        for td in tr.findAll('td'):
            row.append(td.text)
        data.append(row)
    print(data)
    return data


def get_sheet():
    creds = ServiceAccountCredentials.from_json_keyfile_name('divine-surface-277316-a41c6aa8f0a5.json')
    client = gspread.authorize(creds)
    sheet = client.open("Ticket box statistics").sheet1
    return sheet


if __name__ == '__main__':
    print("Starting on ", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    data = get_data()
    sheet = get_sheet()

    row_index = len(sheet.get_all_values()) + 2
    sheet.insert_row(['Ngày', datetime.now().strftime("%Y-%m-%d %H:%M:%S")], row_index)

    row_index += 1
    sheet.insert_row(['Tên', 'Doanh thu', 'Số vé bán được', 'Số xuất chiếu'], row_index)

    row_index += 1
    for data_item in data:
        sheet.insert_row(data_item, row_index)
        row_index += 1

    row_index += 1
    sheet.insert_row(["-----------------------"], row_index)
