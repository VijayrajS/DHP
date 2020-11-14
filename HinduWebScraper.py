url = "https://www.thehindu.com/search/?q=coronavirus&order=DESC&sort=publishdate&pd=year&page="


import requests
import os
import sys
import re
from tqdm import tqdm

from bs4 import BeautifulSoup


page_number = 1
pbar = tqdm(total=1)

months = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
            'September', 'October', 'November', 'December']
corona_terms = ['coronavirus', 'covid', 'n95', 'quarantine', 'lockdown', 'vaccine', 
                'unlock', 'pandemic', 'wuhan', 'tablighi', 'virus', 'testing', 'travel', 'reopen', 'china']

def date_extract(raw):
    date_list = raw.strip().split()[:3]
    month_num = str(months.index(date_list[0]))
    month_num = month_num if len(month_num) == 2 else '0' + month_num
    final_date = str(date_list[2]) + '-' + month_num + '-' + str(date_list[1])
    return final_date

from time import sleep

while True:
    pbar.update(1)
    response = requests.get(url + str(page_number))
    content = response.content
    soup = BeautifulSoup(content, 'html5lib')
    
    card_list = soup.find_all('div', class_="75_1x_StoryCard mobile-padding")
    if not card_list:
        break
    
    for card in card_list:
        # print(card);exit()
        article_link = card.find('a')['href']
        article_head = card.find_all('a', {'class':'story-card75x1-text'})[0].text


        flag = 0
        for word in article_head.lower().split():
            if word in corona_terms:
                flag = 1
                break
        if flag == 0:
            continue

        date_raw = card.find('span', class_="dateline").text.replace(',' , '')
        date = date_extract(date_raw)
        print(article_link + ', ' + date)
        
    page_number += 1

