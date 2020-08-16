import requests
import os
import sys
from tqdm import tqdm

from bs4 import BeautifulSoup

def extract_link_article(link):
    r_website = requests.get(link)
    content = r_website.content
    
    soup_ = BeautifulSoup(content, 'html5lib')
    article_text = ''
    title = soup_.find_all('h1')[0].text
    
    article_text += title + '\n'
    p_set = soup_.find_all('p')
    for j in range(len(p_set)-2):
        if "|" not in p_set[j].text:
            article_text += p_set[j].text + '\n'
    
    with open('dataset/IE/'+date+'_'+link.split('/')[-2]+'.txt', 'w') as fpw:
        fpw.write(article_text)


with open('results_IE.csv', 'r') as fp:
    pbar = tqdm(total=1)

    while (line := fp.readline()):
        pbar.update(1)
        link, date = [u.strip() for u in line.split(',')]
        
        file_name = 'dataset/IE/' + date+'_'+link.split('/')[-2]+'.txt'
        if os.path.exists(file_name):
            continue
        
        extract_link_article(link)

