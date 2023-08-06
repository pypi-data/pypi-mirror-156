# viz.py

import numpy as np
import pandas as pd
from importlib_resources import files
import re
import nltk
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from PIL import Image
import jieba
from collections import Counter

def load_word(ver='web.csv'):
    scfile = files('wordjc.data').joinpath(ver)
    return pd.read_csv(scfile)

def get_text(df):
    return ' '.join(list(df.text.values))

def clean_text(df):
    df.text = [re.sub(r'\d+', '', str(v).replace('\n', ' ')) for v in df.text]
    for sw in stopwords.words('english'):
        df.text = [v.replace(' ' + sw + ' ', ' ') for v in df.text]

    df.text = df.text.apply(lambda v: " ".join(w.lower() for w in v.split()))
    df.text = df.text.str.replace('[^\w\s]', '', regex=True)
    return df

def add_chi_vocab():
    vocab_file = files('wordjc.data').joinpath('bible_vocab.txt')
    with open(vocab_file, 'r', encoding='utf8') as f:
        vocab_list = f.readlines()
        for vocab in vocab_list:
            jieba.add_word(vocab.replace('\n', ''))

def chi_stops():
    dict_file = files('wordjc.dictionary').joinpath('dict.txt.big.txt')
    cloud_file = files('wordjc.dictionary').joinpath('stopWord_cloudmod.txt')
    jieba.set_dictionary(dict_file)
    with open(cloud_file, 'r', encoding='utf-8-sig') as f:
        return f.read().split('\n')

def get_diction(df, stops):
    text = ''.join(list(df.text)).replace('\u3000', '')
    text = re.sub("[、．。，！？『』「」〔〕]", "", text)
    terms = []
    for t in jieba.cut(text, cut_all=False):
        if t not in stops:
            terms.append(t)
    diction = Counter(terms)
    return diction

def plot_cloud(wordcloud):
    plt.figure(figsize=(15, 10))
    plt.imshow(wordcloud) 
    plt.axis("off");

def show_wordcloud(text, image='heart.jpg', mask=None):
    if image:
        img_file = files('wordjc.images').joinpath(image)
        mask = np.array(Image.open(img_file))

    wordcloud = WordCloud(background_color='black', colormap='Set2', mask=mask) \
                    .generate(text)

    plot_cloud(wordcloud)

def chi_wordcloud(df, image='heart.jpg', mask=None):
    add_chi_vocab()
    stops = chi_stops()
    diction = get_diction(df, stops)

    if image:
        img_file = files('wordjc.images').joinpath(image)
        mask = np.array(Image.open(img_file))

    wordcloud = WordCloud(background_color='black', colormap='Set2', mask=mask) \
                    .generate_from_frequencies(frequencies=diction)

    plot_cloud(wordcloud)
