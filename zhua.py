from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from pandas import json_normalize
import pycountry
import os
import shutil
import tempfile
import urllib
from urllib.request import urlopen
import nltk


RES_DIR = "tomtom_data"


def ranking_log_to_cities():
    r"""
    ranking log to city code
    """
    
    url = 'https://www.tomtom.com/en_gb/traffic-index/ranking/'
    # html = urlopen(url).read()
    
    # print(raw)

    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    print(r.text)

    raw = soup.find('div', class_="RankingTable__td RankingTable__td--city").text
    badges = soup.body.find('div', attrs={'class': 'badges'})
    for span in badges.span.find_all('span', recursive=False):
        print(span.attrs['RankingTable__td RankingTable__td--city'])
    print(raw)
    exit(0)
    # print(soup.find_all('a'))
    for script in soup(["script", "style"]):
        script.extract()
    text = soup.get_text()

    lines = (line for line in text.splitlines())

    # # break multi-headlines into a line each
    chunks = (phrase for line in lines for phrase in line.split("  "))
    # # drop blank lines
    # for chunk in chunks:
    #     if chunk:
    #         print(chunk)
    text = ''.join(chunk or print('chunk ',chunk) for chunk in chunks if chunk)
    # print(text)
    with open("tmpfile.txt", 'w+') as tmp_file:
        tmp_file.write(text)
    
    exit(0)
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
            # UAE is not support by the search_fuzzy function
            try:
                ctry_code = pycountry.countries.search_fuzzy(elem[1]).alpha_3
            except:
                # for UAE
                ctry_code = elem[1].upper()
            city_code_list.append(f'{ctry_code}_{elem[0]}')
        print(len(city_code_list))
        print(city_code_list)
        return city_code_list

def get_city_code(file):
    r"""
    Yet another way to get the city code
    alternative to the ranking_log_to_cities
    """
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
    try:
        os.stat(RES_DIR)
    except:
        os.mkdir(RES_DIR)
    # ranking_log_to_cities('./config/log')
    
    city_df = get_city_code("./config/TOMTOM-Country_city_list_rev.csv")
    cities = city_df.to_numpy()
    for line in cities:
        ccode = line[1]
        city = line[2]
        print(f"processing {ccode} {city}")
        res_df = url_to_dataframe(ccode, city)
        res_df.to_csv(f'./{RES_DIR}/{ccode}_{city}.csv', index=False)