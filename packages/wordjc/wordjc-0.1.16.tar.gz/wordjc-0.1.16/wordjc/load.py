# load.py

import numpy as np
import pandas as pd
from importlib_resources import files
import re
import nltk
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from PIL import Image

def load_word():
    scfile = files('wordjc.data').joinpath('web4.csv')
    return pd.read_csv(scfile)

def clean_text(df):
    df.text = [re.sub(r'\d+', '', str(v).replace('\n', ' ')) for v in df.text]
    for sw in stopwords.words('english'):
        df.text = [v.replace(' ' + sw + ' ', ' ') for v in df.text]

    df.text = df.text.apply(lambda v: " ".join(w.lower() for w in v.split()))
    df.text = df.text.str.replace('[^\w\s]', '', regex=True)
    return df

def plot_cloud(wordcloud):
    plt.figure(figsize=(15, 10))
    plt.imshow(wordcloud) 
    plt.axis("off");

def show_wordcloud(text, image=None, mask=None):
    if image:
        mask = np.array(Image.open(image))

    wordcloud = WordCloud(background_color='black', colormap='Set2', mask=mask) \
                    .generate(text)

    plot_cloud(wordcloud)
