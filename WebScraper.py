import requests
from bs4 import BeautifulSoup

import datetime

article_html_data = [[] for i in range(7)]

for i in range(1, 244):
    r_website = requests.get('https://theprint.in/page/'+ str(i) +'/?s=coronavirus+india')
    content = r_website.content

    soup_ = BeautifulSoup(content, 'html5lib')

    class_theprint = "td_module_16 td_module_wrap td-animation-stack"
    article_list = soup_.find_all('div', class_=class_theprint)
    
    for article in article_list:
        dt_of_article = article.find_all('time')[0]['datetime'].split('T')[0]
        month_of_article = datetime.datetime.strptime(dt_of_article, "%Y-%m-%d").month
        print(month_of_article); exit()
        
        
        
    # article_html_data.extend(article_list)
    

