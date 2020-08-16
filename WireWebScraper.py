# https://science.thewire.in/category/health/page/8/
# https://thewire.in/wp-json/thewire/v2/posts/search?keyword=coronavirus%20indi&category=&orderby=rel&per_page=5&page=1

# https://thewire.in/politics/telangana-karnataka-opposition-use-aps-measures-to-prove-covid-mishandling-in-own-states

import requests
import json
from tqdm import tqdm

raw_json = requests.get("https://thewire.in/wp-json/thewire/v2/posts/search?keyword=coronavirus%20indi&category=&orderby=rel&per_page=5&page=1")

url_main = "https://thewire.in/wp-json/thewire/v2/posts/search?keyword=coronavirus%20india&category=&orderby=rel&per_page=5&page="
raw_json = raw_json.json()
# print(raw_json.json())

page_number = 1
rejected_pages = 0
pbar = tqdm(total=10)

def tag_checker(tag_list):
    for tag in tag_list:
        if "coronavirus" in tag.lower() or "covid" in tag.lower():
            return 1

    global rejected_pages
    rejected_pages += 1
    return 0

while True:
    pbar.update(1)
    response = requests.get(url_main + str(page_number))
    raw_json = response.json()
    
    if not raw_json['generic']:
        break
    
    for news_json in raw_json['generic']:
        flag_check = tag_checker(news_json['tags'])
        
        if not flag_check:
            continue
        
        prime_categ = news_json["prime_category"][0]["slug"]
        post_name = news_json["post_name"]
        
        post_date = news_json["post_date"].split(' ')[0]
        link = "https://thewire.in/" + prime_categ + '/' + post_name
        print(link + ', ' + post_date)
    page_number += 1

# print(page_number - 1)
# print(rejected_pages)
