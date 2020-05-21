import http.client
import json
import re
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium import webdriver
import time


def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


def get_data(secret_string):
    data = b''
    run_count = 0
    while len(data) == 0 and run_count < 2:
        run_count += 1
        print("run count: ", run_count)
        conn = http.client.HTTPSConnection("boxofficevietnam.com")
        payload = "draw=1&columns[0][data]=0&columns[0][name]=name&columns[0][searchable]=true&columns[0][orderable]=true&columns[0][search][value]=&columns[0][search][regex]=false&columns[1][data]=1&columns[1][name]=SUM(earning)&columns[1][searchable]=true&columns[1][orderable]=true&columns[1][search][value]=&columns[1][search][regex]=false&columns[2][data]=2&columns[2][name]=SUM(tickets)&columns[2][searchable]=true&columns[2][orderable]=true&columns[2][search][value]=&columns[2][search][regex]=false&columns[3][data]=3&columns[3][name]=SUM(ss)&columns[3][searchable]=true&columns[3][orderable]=true&columns[3][search][value]=&columns[3][search][regex]=false&order[0][column]=1&order[0][dir]=desc&start=0&length=25&search[value]=&search[regex]=false&wdtNonce="
        payload = payload + secret_string
        headers = {
            'authority': 'boxofficevietnam.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'x-requested-with': 'XMLHttpRequest',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://boxofficevietnam.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://boxofficevietnam.com/',
            'accept-language': 'en-US,en;q=0.9,vi;q=0.8,fr-FR;q=0.7,fr;q=0.6',
            'cookie': '__cfduid=d96611f1dbf18a3235dbb01c4ea4216361589539794; _ga=GA1.2.924895533.1589539805; _gid=GA1.2.1878356066.1589539805; tk_ai=woo%3AbtidCjymcwK0EBSLICZGcpBw; wordpress_test_cookie=WP+Cookie+check',
            'Content-Type': 'text/plain',
            'Cookie': '__cfduid=d1ea26c318c69da97488634f52d7824bf1589645344; tk_ai=woo%3A4f3tCt2yqcg0gDZT7qmsovvX'
        }
        conn.request("POST", "/wp-admin/admin-ajax.php?action=get_wdtable&table_id=17", payload, headers)
        res = conn.getresponse()
        data = res.read()
        print(data)
        if len(data) == 0:
            time.sleep(2)

    if len(data) == 0:
        return None

    print(data.decode("utf-8"))
    data_obj = json.loads(data.decode("utf-8"))
    return data_obj.get('data')


def get_secret_string():
    url = "https://boxofficevietnam.com/"
    # Mac testing
    # browser = webdriver.Chrome()

    # Ubuntu setup
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    browser = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver', options=chrome_options)

    # Getting data from url
    browser.get(url)

    html = browser.page_source
    soup = BeautifulSoup(html, 'lxml')
    input_tag = soup.find('input', attrs={"id": "wdtNonceFrontendEdit"})
    secret_string = input_tag.attrs.get("value")
    print("secret string is", secret_string)
    return secret_string


def get_sheet():
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        'divine-surface-277316-a41c6aa8f0a5.json')
    client = gspread.authorize(creds)
    sheet = client.open("Ticket box statistics").sheet1
    return sheet


if __name__ == '__main__':
    data = None
    run_count = 0
    while data is None and run_count < 5:
        run_count += 1
        secret_string = get_secret_string()
        data = get_data(secret_string)
        if data is None:
            time.sleep(5)
            print("retrying: ", run_count)

    if data is not None:
        sheet = get_sheet()

        row_index = len(sheet.get_all_values()) + 2
        sheet.insert_row(['Ngày', datetime.now().strftime("%Y-%m-%d %H:%M:%S")], row_index)

        row_index += 1
        sheet.insert_row(['Tên', 'Doanh thu', 'Số vé bán được', 'Số xuất chiếu'], row_index)

        row_index += 1
        for data_item in data:
            data_item[0] = clean_html(data_item[0])
            sheet.insert_row(data_item, row_index)
            row_index += 1

        row_index += 1
        sheet.insert_row(["-----------------------"], row_index)