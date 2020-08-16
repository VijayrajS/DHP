base_url = "https://timesofindia.indiatimes.com/2019/12/1/archivelist/starttime-"
import requests
import os
import sys
import re
from tqdm import tqdm

from bs4 import BeautifulSoup

pbar = tqdm(total=10)


page_number = 43800
# <div style="font-family: arial; font-size: 12px; font-weight: bold; color: rgb(0, 102, 153); --darkreader-inline-color:#61caff;" data-darkreader-inline-color="">
corona_terms = ['coronavirus', 'covid', 'n95', 'quarantine', 'lockdown', 'vaccine', 
                'unlock', 'pandemic', 'wuhan', 'tablighi', 'virus', 'testing']

while page_number <= 44058:
    pbar.update(1)
    url = base_url + str(page_number) + ".cms"
    response = requests.get(url)
    content = response.content
    soup = BeautifulSoup(content, 'html5lib')
    
    link_div = soup.find_all('div', style=re.compile("font-family:arial ;font-size:12;font-weight:bold; color: #006699"))
    
    if not link_div:
        break
    
    for link in link_div:
        article_links = link.find_all('a')
        
        for article in article_links:
            text = article.text
            for term in corona_terms:
                if term in text.lower():
                    print(article['href'])
                    break

    page_number += 1
