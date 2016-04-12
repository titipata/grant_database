import os
import dedupe
import numpy as np
import pandas as pd
from unidecode import unidecode


# set up file path and parameters
class Parameters():
    num_cores = 4
    n_sample = 15000
    input_file = '../nsf/nsf_grant_investigators.csv'
    output_file = ''
    settings_file = 'nsf_settings'
    training_file = 'nsf_training.json'


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


if __name__ == '__main__':
    params = Parameters()
    print('read NSF investigators file...')
    investigators_nsf = pd.read_csv(params.input_file).fillna('')
    investigators_nsf['full_name'] = (investigators_nsf.first_name + ' ' +
                                      investigators_nsf.last_name).map(lambda x: x.lower())
    name_email = pd.unique(zip(investigators_nsf.full_name, investigators_nsf.email)) # unique
    dedupe_dict = dict((i, {'name': format_text(n), 'email': format_text(e)})
                        for (i, (n, e)) in enumerate(name_email))

    # use "full name" and "email" for deduplication
    fields = [{'field':'name', 'type': 'String', 'has missing' : True},
              {'field' : 'email', 'type': 'String', 'has missing' : True}]
    deduper = dedupe.Dedupe(fields, num_cores=params.num_cores)
    deduper.sample(dedupe_dict, params.n_sample)

    print('load labeled data...(you can skip active labeling)')
    if os.path.exists(params.training_file):
        deduper = read_training_file(deduper, params.training_file)

    print('starting active labeling...')
    dedupe.consoleLabel(deduper)
    deduper.train(ppc=None, recall=0.95)

    # write_setting_file(deduper, params.settings_file)
    write_training_file(deduper, params.training_file) # write

    print('clustering...')
    threshold = deduper.threshold(dedupe_dict, recall_weight=2.0)
    clustered = deduper.match(dedupe_dict, threshold)
    print('# duplicate sets', len(clustered))
