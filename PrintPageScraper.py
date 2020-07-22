import requests
import os
import sys
from tqdm import tqdm

from bs4 import BeautifulSoup
from datetime import datetime

cutoff_date_str = sys.argv[1]
cutoff_date = datetime.toordinal(datetime.strptime('2019-12-01', '%Y-%M-%d'))
count = 0

def extract_link_article(link, date):
    tags_class = "td-tags td-post-small-box clearfix"
    
    r_website = requests.get(link)
    content = r_website.content
    
    soup_ = BeautifulSoup(content, 'html5lib')
    try:
        tag_list = soup_.find_all('ul', class_=tags_class)[0].find_all('a')
    except:
        return
    tag_text = [tag.get_text() for tag in tag_list]
    # COVID-19, Coronavirus, Covid Vaccine
    
    if "Coronavirus" in tag_text or "COVID-19" in tag_list:
        
        article_text = ''
        title = soup_.find_all('h1', class_='entry-title')[0].text
        
        article_text += title + '\n'
        p_set = soup_.find_all('p')
        for j in range(len(p_set)-14):
            article_text += p_set[j].text + '\n'
        
        with open('dataset/print/'+date+'_'+link.split('/')[-2]+'.txt', 'w') as fpw:
            fpw.write(article_text)

with open('results_print.csv', 'r') as fp:
    # put a tqdm loop here too
    n_lines = os.system('wc -l results.csv')
    pbar = tqdm(total=n_lines)

    while (line := fp.readline()):
        pbar.update(1)
        link, date = [u.strip() for u in line.split(',')]
        date_obj = datetime.strptime(date, '%Y-%M-%d')
        
        if datetime.toordinal(date_obj) <= cutoff_date:
            continue
        
        file_name = 'dataset/print/' + date+'_'+link.split('/')[-2]+'.txt'
        if os.path.exists(file_name):
            continue
        
        extract_link_article(link, date)
