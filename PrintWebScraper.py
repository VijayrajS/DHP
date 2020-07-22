import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

import datetime
import sys

article_link_list = []
n_pages = int(sys.argv[1])

for i in tqdm(range(1, n_pages + 1)):
    r_website = requests.get('https://theprint.in/page/'+ str(i) +'/?s=coronavirus+india')
    content = r_website.content

    soup_ = BeautifulSoup(content, 'html5lib')

    class_theprint = "td_module_16 td_module_wrap td-animation-stack"
    article_list = soup_.find_all('div', class_=class_theprint)

    for article in article_list:
        dt_of_article = article.find_all('time')[0]['datetime'].split('T')[0]
        
        date_of_article = str(datetime.datetime.strptime(dt_of_article, "%Y-%m-%d")).split(' ')[0]
        article_link = article.find_all('a', class_="td-image-wrap")[0]['href']
        
        article_link_list.append(article_link + ', ' + date_of_article)


for article_link in tqdm(article_link_list[::-1]):
    print(article_link)
