import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

import datetime
import sys

article_link_list = []
n_pages = int(sys.argv[1])
months = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
            'September', 'October', 'November', 'December']

for i in tqdm(range(1, n_pages + 1)):
    r_website = requests.get('https://indianexpress.com/section/india/page/'+ str(i) +'/?s=coronavirus+india')
    content = r_website.content

    soup_ = BeautifulSoup(content, 'html5lib')

    class_IE = "details"
    article_list = soup_.find_all('div', class_=class_IE)

    for article in article_list:
        article_link = article.find('h3').find('a')['href']
        article_date = article.find('time').text.split('\n')[-1].strip().split()
        month_str = str(months.index(article_date[1]))
        month_str = '0'*(len(month_str) == 1) + month_str
        
        day_str = article_date[2].strip(',')
        day_str = '0'*(len(day_str) == 1) + day_str
        
        final_date = article_date[3]+'-'+month_str+'-'+day_str
        
        article_link_list.append(article_link + ', ' + final_date)


for article_link in tqdm(article_link_list[::-1]):
    print(article_link)
