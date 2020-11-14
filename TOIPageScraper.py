import requests
import os
import sys
from tqdm import tqdm
from bs4 import BeautifulSoup
import urllib.request as urllib2

skipped_pages = 0

def extract_link_article(link):
    # print(link)
    
    r_website = urllib2.urlopen(link)
    content = r_website.read()
    
    soup_ = BeautifulSoup(content, 'html5lib')
    for script in soup_(["script", "style"]): 
        script.extract()

    article_text = ''
    title = soup_.find('span', class_="title").text
    date = soup_.find('time')['datetime'].split('T')[0]
    text_ = soup_.find('div', class_="Normal").text
    article_text += title + '\n' + date + '\n' + text_
    
    with open('dataset/TOI/'+link.split('/')[-3]+'.txt', 'w') as fpw:
        fpw.write(article_text)

with open('results_toi.csv', 'r') as fp:
    pbar = tqdm(total=1)

    while (line := fp.readline()):
        pbar.update(1)
        link = line if line[0] != '/' else "https://timesofindia.indiatimes.com/" + line
        if link[:5] != 'https':
            link = link.replace("http", "https", 1)
        file_name = 'dataset/TOI/' + link.split('/')[-3]+'.txt'
        if os.path.exists(file_name):
            continue
        try:
            extract_link_article(link)

        except:
            skipped_pages += 1
            print(skipped_pages)
            continue

print(skipped_pages)