import os
import re
import dedupe
from unidecode import unidecode
from nltk.tokenize import WhitespaceTokenizer
w_tokenizer = WhitespaceTokenizer()


def preprocess(text):
    """Preprocess text"""
    text = text.lower()
    text = re.sub('\.', ' ', text)
    text = re.sub('/', ' ', text)
    text = re.sub(',', ' ', text)
    text = re.sub('-', ' ', text)
    text = ' '.join(w_tokenizer.tokenize(text))
    text = text.strip()
    if text == '':
        text_out = None
    else:
        text_out = unidecode(text)
    return text_out


def format_text(text):
    """Fill empty string with none"""
    if text.strip() == '':
        text_output = None
    else:
        text_output = unidecode(text)
    return text_output


def read_setting_file(filename='settings'):
    """Read dedupe settings file"""
    settings_file = filename
    print('reading from', settings_file)
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
