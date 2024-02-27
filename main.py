import json

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from tabulate import tabulate

BASE_URL = 'https://index.minfin.com.ua/ua/russian-invading/casualties'


def get_urls():
    urls = ["/"]
    html_doc = requests.get(BASE_URL)
    soup = BeautifulSoup(html_doc.text, "html.parser")
    content = soup.select("div[class=ajaxmonth] h4[class=normal] a ")  # тут просто через пробел ищем всё, сейчас в
    # контенте ссылки
    prefix = "/month.php?month="
    for link in content:
        url = prefix + re.search(r"\d{4}-\d{2}", link["id"]).group()
        urls.append(url)
    return urls


def spider(url):
    result = []
    html_doc = requests.get(BASE_URL + url)  # базовий + то що уже знайшли
    soup = BeautifulSoup(html_doc.text, "html.parser")
    content = soup.select("ul[class=see-also] li[class=gold]")
    for li in content:
        parse_element = {}
        date_key = li.find("span", attrs={"class": "black"}).text
        try:
            date_key = datetime.strptime(date_key, "%d.%m.%Y").isoformat()
        except ValueError:
            print(f"Error for :{date_key}")
            continue
        parse_element.update({"date": date_key})
        casualties = li.find("div").find("div").find("ul")
        for casual in casualties:
            name, quantity, *_ = casual.text.split("—")
            name = name.strip()
            quantity = re.search(r"\d+", quantity).group()
            parse_element.update({name: quantity})
        result.append(parse_element)
    return result


def main(urls):
    data = []
    for url in urls:
        data.extend(spider(url))
    return data


if __name__ == "__main__":
    result = main(get_urls())
    headers = list(result[0].keys())
    data_rows = []
    for row in result:
        data_row = []
        for header in headers:
            if header in row:
                data_row.append(row[header])
            else:
                data_row.append(None)
        data_rows.append(data_row)
    #print(result := tabulate(data_rows,  tablefmt="pretty", headers=headers))
    with open("data.json", "w", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=2)
