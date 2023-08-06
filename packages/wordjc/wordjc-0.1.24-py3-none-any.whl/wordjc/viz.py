# viz.py
#    By Johnny Cheng
#    Updated: 24 June 2022

import numpy as np
from importlib_resources import files
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from PIL import Image

from wordjc import util


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
    util.add_chi_vocab()
    stops = util.chi_stops()
    diction = util.get_diction(df, stops)

    if image:
        img_file = files('wordjc.images').joinpath(image)
        mask = np.array(Image.open(img_file))

    font_path = files('wordjc.data').joinpath('msyh.ttc')
    wordcloud = WordCloud(background_color='black', colormap='Set2', \
	                                mask=mask, font_path=font) \
                            .generate_from_frequencies(frequencies=diction)

    plot_cloud(wordcloud)
