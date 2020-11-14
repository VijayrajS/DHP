import os, sys
from datetime import datetime
import tqdm

article_path = './dataset/TOI'

files = sorted(os.listdir(article_path))

data = {}
data['news_body']  = []
data['time_obj'] = []

if __name__ == '__main__':
    start_date = datetime.fromisoformat(sys.argv[1]).toordinal()
    end_date = datetime.fromisoformat(sys.argv[2]).toordinal()
    
    for filename in tqdm.tqdm(files):
        body_text = ''
        
        i = 0
        with open(os.path.join(article_path, filename), 'r') as fp:
            while line := fp.readline():
                if i == 1:
                    date = datetime.strptime(line.split('_')[0], '%Y-%M-%d')
                    if date.toordinal() >= start_date and date.toordinal() <= end_date:
                        data['time_obj'].append(date)
                else:
                    body_text += line.strip() + ' '
                i += 1
            
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

    print("Creating dictionary...")
    id2word = corpora.Dictionary(data_lemmatized)

    # Create Corpus
    texts = data_lemmatized

    # Term Document Frequency
    print("Creating tdf...")
    corpus = [id2word.doc2bow(text) for text in texts]

    lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                            id2word=id2word,
                                            num_topics=10, 
                                            random_state=100,
                                            update_every=1,
                                            chunksize=100,
                                            passes=10,
                                            alpha='auto',
                                            per_word_topics=True)

    print('\nPerplexity: ', lda_model.log_perplexity(corpus))  # a measure of how good the model is. lower the better.

    # Compute Coherence Score
    coherence_model_lda = CoherenceModel(model=lda_model, texts=data_lemmatized, dictionary=id2word, coherence='c_v')
    coherence_lda = coherence_model_lda.get_coherence()
    print('\nCoherence Score: ', coherence_lda)

    vis = pyLDAvis.gensim.prepare(lda_model, corpus, id2word, mds='tsne')
    pyLDAvis.save_html(vis, 'lda_TOI.html')
    
    DHP_path = '/Users/vijayrajs/Desktop/Academics/Acad-Semesters/Year_4/4-1/DHP/'
    mallet_path = DHP_path + 'mallet-2.0.6/bin/mallet'
    ldamallet = gensim.models.wrappers.LdaMallet(mallet_path, corpus=corpus, num_topics=20, id2word=id2word)
    
    # Compute Coherence Score
    coherence_model_ldamallet = CoherenceModel(model=ldamallet, texts=data_lemmatized, dictionary=id2word, coherence='c_v')
    coherence_ldamallet = coherence_model_ldamallet.get_coherence()
    print('\nCoherence Score: ', coherence_ldamallet)
    
    
    vis = pyLDAvis.gensim.prepare(lda_model, corpus, id2word, mds='tsne')
    pyLDAvis.save_html(vis, 'lda_print.html')
    
    DHP_path = '/home/vijayraj/Desktop/Academics/4-1/DHP/'
    mallet_path = DHP_path + 'mallet-2.0.6/bin/mallet'
    ldamallet = gensim.models.wrappers.LdaMallet(mallet_path, corpus=corpus, num_topics=20, id2word=id2word)
    
    # Compute Coherence Score
    coherence_model_ldamallet = CoherenceModel(model=ldamallet, texts=data_lemmatized, dictionary=id2word, coherence='c_v')
    coherence_ldamallet = coherence_model_ldamallet.get_coherence()
    print('\nCoherence Score: ', coherence_ldamallet)
    
    def compute_coherence_values(dictionary, corpus, texts, limit, start=2, step=3):
        """
        Compute c_v coherence for various number of topics

        Parameters:
        ----------
        dictionary : Gensim dictionary
        corpus : Gensim corpus
        texts : List of input texts
        limit : Max num of topics

        Returns:
        -------
        model_list : List of LDA topic models
        coherence_values : Coherence values corresponding to the LDA model with respective number of topics
        """
        coherence_values = []
        model_list = []
        for num_topics in range(start, limit, step):
            model = gensim.models.wrappers.LdaMallet(mallet_path, corpus=corpus, num_topics=num_topics, id2word=id2word)
            model_list.append(model)
            coherencemodel = CoherenceModel(model=model, texts=texts, dictionary=dictionary, coherence='c_v')
            coherence_values.append(coherencemodel.get_coherence())

        return model_list, coherence_values
    
    model_list, coherence_values = compute_coherence_values(dictionary=id2word, corpus=corpus, texts=data_lemmatized, start=2, limit=40, step=6)
    limit=40; start=2; step=6;
    x = range(start, limit, step)
    plt.plot(x, coherence_values)
    plt.xlabel("Num Topics")
    plt.ylabel("Coherence score")
    plt.legend(("coherence_values"), loc='best')
    plt.show()

    for m, cv in zip(x, coherence_values):
        print("Num Topics =", m, " has Coherence Value of", round(cv, 4))
    
    optimal_model = model_list[3]
    model_topics = optimal_model.show_topics(formatted=False)
    print("Topics")
    print(optimal_model.print_topics(num_words=10))

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

    def format_topics_sentences(ldamodel=lda_model, corpus=corpus, texts=data):
        # Init output
        sent_topics_df = pd.DataFrame()

        # Get main topic in each document
        for i, row in enumerate(ldamodel[corpus]):
            row = sorted(row, key=lambda x: (x[1]), reverse=True)
            # Get the Dominant topic, Perc Contribution and Keywords for each document
            for j, (topic_num, prop_topic) in enumerate(row):
                if j == 0:  # => dominant topic
                    wp = ldamodel.show_topic(topic_num)
                    topic_keywords = ", ".join([word for word, prop in wp])
                    sent_topics_df = sent_topics_df.append(pd.Series([int(topic_num), round(prop_topic,4), topic_keywords]), ignore_index=True)
                else:
                    break
        sent_topics_df.columns = ['Dominant_Topic', 'Perc_Contribution', 'Topic_Keywords']

        # Add original text to the end of the output
        contents = pd.Series(texts)
        sent_topics_df = pd.concat([sent_topics_df, contents], axis=1)
        return(sent_topics_df)


    df_topic_sents_keywords = format_topics_sentences(ldamodel=optimal_model, corpus=corpus, texts=data)

    # Format
    df_dominant_topic = df_topic_sents_keywords.reset_index()
    df_dominant_topic.columns = ['Document_No', 'Dominant_Topic', 'Topic_Perc_Contrib', 'Keywords', 'Text']

    # Show
    df_dominant_topic.head(10)

    topic_counts = df_topic_sents_keywords['Dominant_Topic'].value_counts()

    # Percentage of Documents for Each Topic
    topic_contribution = round(topic_counts/topic_counts.sum(), 4)

    # Topic Number and Keywords
    topic_num_keywords = df_topic_sents_keywords[['Dominant_Topic', 'Topic_Keywords']]

    # Concatenate Column wise
    df_dominant_topics = pd.concat([topic_num_keywords, topic_counts, topic_contribution], axis=1)

    # Change Column names
    df_dominant_topics.columns = ['Dominant_Topic', 'Topic_Keywords', 'Num_Documents', 'Perc_Documents']

    # Show
    print(df_dominant_topics.to_markdown())

    nlp = spacy.load('en')
    ents = []
    from tqdm import tqdm
    for index, row in df.iterrows():
        doc = nlp(row['article'])
        ents.append(doc.ents)
        
    df['Named Entities'] = ents
    print(df.to_markdown())
