import os
from datetime import datetime
import tqdm

article_path = './dataset/print'

files = sorted(os.listdir(article_path))

data = {}
data['news_body']  = []
data['time_obj'] = []

bad_lines = [
'We are deeply grateful to our readers & viewers for their time, trust and subscriptions.',
'Quality journalism is expensive and needs readers to pay for it. Your support will define our work and ThePrint’s future.',
'SUBSCRIBE NOW'
]


for filename in tqdm.tqdm(files):
    body_text = ''
    date = datetime.strptime(filename.split('_')[0], '%Y-%M-%d')
    data['time_obj'].append(date)
    
    with open(os.path.join(article_path, filename), 'r') as fp:
        while line := fp.readline():
            flag = 0
            for bad_line in bad_lines:
                if bad_line in line:
                    flag = 1; break
            if flag:
                continue
            
            body_text += line.strip() + ' '

    data['news_body'].append(body_text)

#LDA
import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel

# spacy for lemmatization
import spacy

# Plotting tools
import pyLDAvis
import pyLDAvis.gensim
import matplotlib.pyplot as plt

# Enable logging for gensim - optional
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.ERROR)

import warnings
warnings.filterwarnings("ignore",category=DeprecationWarning)

import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords

stop_words = stopwords.words('english')
stop_words.extend(['from', 'subject', 're', 'edu', 'use'])
stop_words = set(stop_words)

import re
import pandas as pd

start_date = None
end_date = None

df = pd.DataFrame.from_records(data)
data_p = df.news_body.values.tolist()
# Remove new line characters
print('Removing newlines...')
data_p = [re.sub('\s+', ' ', sent) for sent in data_p]

# Remove distracting single quotes
print('Removing single quotes...')
data_p = [re.sub("\'", "", sent) for sent in data_p]

# Removing unicode spaces
print('Removing unicode spaces...')
data_p = [str(s.replace(u'\xa0', ' ').encode('utf-8').decode('utf-8','ignore')) for s in data_p]

# Removing links
print('Removing links...')
link_regex = r'(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$'
data_p = [re.sub(link_regex, "", sent) for sent in data_p]

# Removing hashtags
print('Removing #tags...')
data_p = [re.sub(r'\#\w+', "", sent) for sent in data_p]
# Removing emojis
print('Removing emojis...')
emoji_regex = r'[(\U0001F600-\U0001F92F|\U0001F300-\U0001F5FF|\U0001F680-\U0001F6FF|\U0001F190-\U0001F1FF|\U00002702-\U000027B0|\U0001F926-\U0001FA9F|\u200d|\u2640-\u2642|\u2600-\u2B55|\u23cf|\u23e9|\u231a|\ufe0f)]+'
result = [re.sub(emoji_regex, '', sent) for sent in data_p]

def sent_to_words(sentences):
    for sentence in sentences:
        yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))  # deacc=True removes punctuations

data_words = list(sent_to_words(data_p))

# Bigram and trigram models
bigram = gensim.models.Phrases(data_words, min_count=5, threshold=100) # higher threshold fewer phrases.
trigram = gensim.models.Phrases(bigram[data_words], threshold=100)  

# Faster way to get a sentence clubbed as a trigram/bigram
bigram_mod = gensim.models.phrases.Phraser(bigram)
trigram_mod = gensim.models.phrases.Phraser(trigram)

def remove_stopwords(texts):
    return [[word for word in simple_preprocess(str(doc)) if word not in stop_words] for doc in texts]

def make_bigrams(texts):
    return [bigram_mod[doc] for doc in texts]

def make_trigrams(texts):
    return [trigram_mod[bigram_mod[doc]] for doc in texts]

# Remove Stop Words
data_words_nostops = remove_stopwords(data_words)

# Form Bigrams
data_words_bigrams = make_bigrams(data_words_nostops)

# Initialize spacy 'en' model, keeping only tagger component (for efficiency)
# python3 -m spacy download en
nlp = spacy.load('en', disable=['parser', 'ner'])

def lemmatization(texts, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
    """https://spacy.io/api/annotation"""
    texts_out = []
    for sent in texts:
        doc = nlp(" ".join(sent)) 
        texts_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])
    return texts_out

# Do lemmatization keeping only noun, adj, vb, adv
print("Lemmatizing words...")
data_lemmatized = lemmatization(data_words_bigrams, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV'])


