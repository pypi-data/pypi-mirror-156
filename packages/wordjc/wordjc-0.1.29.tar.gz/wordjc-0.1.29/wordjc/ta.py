# ta.py
#    By Johnny Cheng
#    Updated: 28 June 2022


import numpy as np
from importlib_resources import files
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize, sent_tokenize

from wordjc import util


# Tokenize text into sentences
def get_sentences(df, lang):
    text = util.get_text(df)
    if lang == 'chi':
        sentences = text.split('。')
        if sentences[-1] == '':
            sentences = np.delete(sentences, -1)
    else:
        sentences = sent_tokenize(text)

    return sentences


# Score a sentence by its words
def get_sentence_scores(sentences, frequency_table, sent_len) -> dict:   
    sentence_weight = dict()

    for sentence in sentences:
        sentence_wordcount = (len(util.get_sent_terms(sentence)))
        sentence_wordcount_without_stop_words = 0
        for word_weight in frequency_table:
            if word_weight in sentence.lower():
                sentence_wordcount_without_stop_words += 1
                if sentence[:sent_len] in sentence_weight:
                    sentence_weight[sentence[:sent_len]] += frequency_table[word_weight]
                else:
                    sentence_weight[sentence[:sent_len]] = frequency_table[word_weight]

        sentence_weight[sentence[:sent_len]] = sentence_weight[sentence[:sent_len]] / \
                                                sentence_wordcount_without_stop_words

    return sentence_weight


# Extract summary from sentences
def get_summary(sentences, sentence_weight, threshold, sent_len):
    sentence_counter = 0
    summary = ''
    sep ='~'

    for sentence in sentences:
        if sentence[:sent_len] in sentence_weight and \
           sentence_weight[sentence[:sent_len]] >= (threshold):
            summary += sentence + sep
            sentence_counter += 1

    return summary


def summary(df, lang='en', weight=1.5, sent_len=10):
    if type(df) == str: return

    util.set_lang(lang)
    diction = util.get_diction(df)
    sentences = get_sentences(df, lang)

    sentence_scores = get_sentence_scores(sentences, diction, sent_len)
    threshold = np.mean(list(sentence_scores.values()))
    return get_summary(sentences, sentence_scores, weight * threshold, sent_len)
