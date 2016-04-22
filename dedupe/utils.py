import os
import re
import string
import numpy as np
import dedupe
from unidecode import unidecode
from nltk.tokenize import WhitespaceTokenizer
w_tokenizer = WhitespaceTokenizer()
regex_punctuation = re.compile('[%s]' % re.escape(string.punctuation))


def preprocess(text):
    """Preprocess text"""
    try:
        text = text.lower()
        text = regex_punctuation.sub(' ', text)
        text = ' '.join(w_tokenizer.tokenize(text))
        if text == '':
            text_out = None
        else:
            text_out = unidecode(text)
    except:
        text_out = ''
    return text_out


def read_setting_file(filename='settings'):
    """Read dedupe settings file"""
    settings_file = filename
    print('reading from ', settings_file)
    with open(settings_file, 'rb') as sf:
        deduper = dedupe.StaticDedupe(sf)
    return deduper


def read_training_file(deduper, filename='training.json'):
    """Read dedupe training file"""
    training_file = filename
    print('reading labeled examples from ', training_file)
    with open(training_file, 'rb') as tf:
        deduper.readTraining(tf)
    return deduper


def write_setting_file(deduper, filename='settings'):
    """Write dedupe setting file"""
    settings_file = filename
    with open(settings_file, 'wb') as sf:
        deduper.writeSettings(sf)
    print("Setting file saved")


def write_training_file(deduper, filename='training.json'):
    """Give a deduper, write a training file"""
    with open(filename, 'w') as tf:
        deduper.writeTraining(tf)
    print("Training file saved")


def format_text(text):
    """Fill empty string with none"""
    try:
        return preprocess(text)
    except:
        pass
    return ''


def dataframe_to_dict(df):
    """
    Transforms a pandas' dataframe to a dict used by dedupe
    """
    return dict((i, a) for (i, a) in enumerate(df.to_dict('records')))


def add_dedupe_col(df, df_dict, deduper, threshold):
    """
    add a deduplication column to the dataframe `df` using the `deduper`
    """
    df_new = df.copy()
    df_new['dedupe_id'] = None
    clustered = deduper.match(df_dict, threshold)
    clustered = list(clustered)
    cluster_assignment_idx = np.array([[row_id, c_id]
                                       for c_id in range(len(clustered))
                                       for row_id in clustered[c_id][0]])

    df_new.dedupe_id.iloc[cluster_assignment_idx[:, 0]] = cluster_assignment_idx[:, 1]
    new_idx = range(df_new.dedupe_id.max() + 1, df_new.dedupe_id.max() + 1 + df_new.dedupe_id.isnull().sum())
    df_new.dedupe_id[df_new.dedupe_id.isnull()] = new_idx
    return df_new
