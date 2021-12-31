from requests_html import HTMLSession
from urllib.parse import urlparse
import requests
session = HTMLSession()
from bs4 import BeautifulSoup
import pandas as pd
import json
from pandas import json_normalize
import pycountry
import os

def ranking_log_to_cities(file_name):
    r"""
    ranking log to city and city code
    """
    with open(file_name, 'r+') as file:
        is_enter = False
        cnt = 0;
        city_name_list = []
        country_name_list = []
        for line in file.readlines():
            if "Change from 2019" in line:
                is_enter = True
                continue
            if "Change the way you move with TomTom technology" in line:
                is_enter = False
                continue
            if is_enter:
                if cnt == 1:
                    city_name_list.append(line.strip().lower().replace(' ', '-'))
                elif cnt == 2:
                    country_name_list.append(line.strip().upper())
                elif cnt == 6:
                    cnt = -1
                cnt += 1
        
        city_code_list = []
        for elem in zip(city_name_list, country_name_list):
            ctry_code = pycountry.countries.search_fuzzy(elem[1])
            city_code_list.append(f'{ctry_code}_{elem[0]}')
        print(len(city_code_list))
        print(city_code_list)

def get_city_code(file):
    df = pd.read_csv(file)
    print(df)
    return df

def url_to_dataframe(ccode, city):
    base_url = f"https://api.midway.tomtom.com/ranking/dailyStats/{ccode}_{city}"
    html_text = requests.get(base_url).text
    soup = BeautifulSoup(html_text, 'html.parser')
    content = soup.get_text()
    info = json.loads(content)
    df = json_normalize(info)
    if len(df) < 5:
        print(f"{ccode} {city} failed")
    return df

if __name__ == "__main__":
    os.mkdir('res')
    city_df = get_city_code("./config/TOMTOM-Country_city_list_rev.csv")
    cities = city_df.to_numpy()
    print(cities)
    for line in cities:
        ccode = line[1]
        city = line[2]
        print(f"processing {ccode} {city}")
        res_df = url_to_dataframe(ccode, city)
        res_df.to_csv(f'./res/{ccode}_{city}.csv', index=False)