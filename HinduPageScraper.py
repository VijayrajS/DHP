import requests
import os
import sys
from tqdm import tqdm

from bs4 import BeautifulSoup
from datetime import datetime

cutoff_date_str = sys.argv[1]
cutoff_date = datetime.toordinal(datetime.strptime('2019-12-01', '%Y-%M-%d'))
count = 0
misses = 0

def extract_link_article(link, date):
    tags_class = "paywall"
    
    try:
        r_website = requests.get(link)
        content = r_website.content
        soup_ = BeautifulSoup(content, 'html5lib')
    
        article_text = ''
        title = soup_.find_all('h1')[0].text
        article_text += title + '\n'
        p_set = soup_.find_all('div', {'class':"paywall"})[0].find_all('p')

        for j in range(len(p_set)):
            article_text += p_set[j].text + '\n'
        
        with open('dataset/hindu/'+date+'_'+link.split('/')[-1]+'.txt', 'w') as fpw:
            fpw.write(article_text)
    except:
        global misses
        misses += 1
        with open('misses_hindu.csv', 'a') as mp:
            if '-live-updates' not in link:
                mp.write(link + ', '+date + '\n')
        print(misses)
        return

with open('results_hindu1.csv', 'r') as fp:
    # put a tqdm loop here too
    pbar = tqdm(total=10)

    while (line := fp.readline()):
        pbar.update(1)
        try:
            link, date = [u.strip() for u in line.split(',')]
            date_obj = datetime.strptime(date, '%Y-%M-%d')
            
            if datetime.toordinal(date_obj) <= cutoff_date:
                continue
            
            file_name = 'dataset/hindu/' + date+'_'+link.split('/')[-1]+'.txt'
            if os.path.exists(file_name):
                continue
        except:
            misses += 1
            print(misses)
        
        extract_link_article(link, date)

print(misses)
