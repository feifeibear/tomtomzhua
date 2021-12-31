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


def ranking_log_to_cities(file_name):
    r"""
    ranking log to city code
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
            # UAE is not support by the search_fuzzy function
            try:
                ctry_code = pycountry.countries.lookup(elem[1]).alpha_3
            except:
                # for UAE
                if elem[1] == 'RUSSIA':
                    ctry_code = 'RUS'
                elif elem[1] == 'UAE':
                    ctry_code = elem[1].upper()
                print(f'wraning {ctry_code}')
            city_code_list.append((f'{ctry_code}', f'{elem[0]}'))
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
    city_array = df.to_numpy()
    res_list = []
    for line in city_array:
        ccode = line[1]
        city = line[2]
        res_list.append((ccode, city))
    return res_list

def url_to_dataframe(ccode, city):
    base_url = f"https://api.midway.tomtom.com/ranking/dailyStats/{ccode}_{city}"
    html_text = requests.get(base_url).text
    soup = BeautifulSoup(html_text, 'html.parser')
    content = soup.get_text()
    info = json.loads(content)
    df = json_normalize(info)
    if len(df) < 5:
        print(f"{ccode} {city} failed")
        raise RuntimeError
    return df

if __name__ == "__main__":
    try:
        os.stat(RES_DIR)
    except:
        os.mkdir(RES_DIR)
    # yet another way to get the city code.
    # It can hand UAE
    # cities = ranking_log_to_cities('./config/log')

    cities = get_city_code("./config/TOMTOM-Country_city_list_rev.csv")

    for ccode, city in cities:
        res_file_name = f'{ccode}_{city}.csv'
        if res_file_name in os.listdir(f'./{RES_DIR}'):
            print(f'{res_file_name} has been processed')
            continue
        try:
            res_df = url_to_dataframe(ccode, city)
            res_df.to_csv(f'./{RES_DIR}/{res_file_name}', index=False)
        except RuntimeError:
            print(f"processing {res_file_name} Failed!")