import http.client
import json
import re
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials


def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


def get_data():
    conn = http.client.HTTPSConnection("boxofficevietnam.com")
    payload = "draw=1&columns%5B0%5D%5Bdata%5D=0&columns%5B0%5D%5Bname%5D=name&columns%5B0%5D%5Bsearchable%5D=true&columns%5B0%5D%5Borderable%5D=true&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B0%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B1%5D%5Bdata%5D=1&columns%5B1%5D%5Bname%5D=SUM(earning)&columns%5B1%5D%5Bsearchable%5D=true&columns%5B1%5D%5Borderable%5D=true&columns%5B1%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B1%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B2%5D%5Bdata%5D=2&columns%5B2%5D%5Bname%5D=SUM(tickets)&columns%5B2%5D%5Bsearchable%5D=true&columns%5B2%5D%5Borderable%5D=true&columns%5B2%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B2%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B3%5D%5Bdata%5D=3&columns%5B3%5D%5Bname%5D=SUM(ss)&columns%5B3%5D%5Bsearchable%5D=true&columns%5B3%5D%5Borderable%5D=true&columns%5B3%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B3%5D%5Bsearch%5D%5Bregex%5D=false&order%5B0%5D%5Bcolumn%5D=1&order%5B0%5D%5Bdir%5D=desc&start=0&length=25&search%5Bvalue%5D=&search%5Bregex%5D=false&wdtNonce="
    payload = payload + get_secret_string()
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
    data_obj = json.loads(data)
    return data_obj.get('data')


def get_secret_string():
    from bs4 import BeautifulSoup
    from selenium import webdriver
    url = "https://boxofficevietnam.com/"
    browser = webdriver.Chrome()
    browser.get(url)
    html = browser.page_source
    soup = BeautifulSoup(html, 'lxml')
    input_tag = soup.find('input', attrs={"id": "wdtNonceFrontendEdit"})
    secret_string = input_tag.attrs.get("value")
    print("secret string is", secret_string)
    return secret_string


def get_sheet():
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        '/Users/long.le0503/divine-surface-277316-a41c6aa8f0a5.json')
    client = gspread.authorize(creds)
    sheet = client.open("Ticket box statistics").sheet1
    return sheet


if __name__ == '__main__':
    sheet = get_sheet()

    row_index = len(sheet.get_all_values()) + 2
    sheet.insert_row(['Ngày', datetime.now().strftime("%Y-%m-%d %H:%M:%S")], row_index)

    row_index += 1
    sheet.insert_row(['Tên', 'Doanh thu', 'Số vé bán được', 'Số xuất chiếu'], row_index)

    data = get_data()
    row_index += 1
    for data_item in data:
        data_item[0] = clean_html(data_item[0])
        sheet.insert_row(data_item, row_index)
        row_index += 1

    row_index += 1
    sheet.insert_row(["-----------------------"], row_index)




