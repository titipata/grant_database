import os
import re
import dedupe
import pandas as pd
from nltk.tokenize import WhitespaceTokenizer
wtk = WhitespaceTokenizer()


class Parameters():
    threshold = 0.1 # if None, we will find threshold
    num_cores = 8
    n_sample = 15000
    settings_file = 'link_grant_settings'
    training_file = 'link_grant_training.json'


def write_training_file(deduper, filename='training.json'):
    """Give a deduper, write a training file"""
    with open(filename, 'w') as tf:
        deduper.writeTraining(tf)
    print("Training file saved")


def preprocess(text, tokenizer=None):
    """Preprocess text"""
    text = re.sub('\.', '', text)
    text = re.sub('/', ' ', text)
    text = re.sub('-', '', text)
    if wtk is not None:
        text = ' '.join(wtk.tokenize(text)).lower()
    text = text.strip()
    if text == '':
        text = None
    return text


def prepare_linkage_dict():
    """
    Read data from NIH and NSF folder
    """
    cname = ['full_name', 'insti_name', 'insti_city']
    print('read file from NIH and NSF folder...')
    nih_investigators = pd.read_csv('nih/nih_grant_investigators.csv').fillna('')
    nih_investigators['full_name'] = nih_investigators.first_name + ' ' + \
                                     nih_investigators.last_name
    nih_info = pd.read_csv('nih/nih_grant_info.csv').fillna('')
    nsf_investigators = pd.read_csv('nsf/nsf_grant_investigators.csv').fillna('')
    nsf_info = pd.read_csv('nsf/nsf_grant_info.csv').fillna('')
    nsf_investigators['full_name'] = nsf_investigators.first_name + ' ' + \
                                     nsf_investigators.last_name
    nih_info.rename(columns={'org_city': 'insti_city',
                             'org_name': 'insti_name'}, inplace=True)

    nih_investigators = nih_investigators.merge(nih_info[['application_id', 'insti_name', 'insti_city']])
    nsf_investigators = nsf_investigators.merge(nsf_info[['award_id', 'insti_name','insti_city']])

    for c in cname:
        nih_investigators[c] = nih_investigators[c].map(lambda x: preprocess(x, wtk))
        nsf_investigators[c] = nsf_investigators[c].map(lambda x: preprocess(x, wtk))

    nih_linkage = nih_investigators[['pi_id', 'full_name', 'insti_name', 'insti_city']]\
                    .drop_duplicates(subset='pi_id', keep='first').fillna('')
    nsf_linkage = nsf_investigators[['full_name', 'insti_name', 'insti_city']]\
                    .drop_duplicates() # we'll replace with dedupe nsf later on

    cname = ['full_name', 'insti_name', 'insti_city']
    nih_linkage_dict = nih_linkage[cname].to_dict('records')
    nih_linkage_dict = dict((i,d) for (i, d) in enumerate(nih_linkage_dict))
    nsf_linkage_dict = nsf_linkage[cname].to_dict('records')
    nsf_linkage_dict = dict((i,d) for (i, d) in enumerate(nsf_linkage_dict))
    return nih_linkage_dict, nsf_linkage_dict


if __name__ == '__main__':
    params = Parameters()
    n_sample = params.n_sample

    print('prepare dataset...')
    nih_linkage_dict, nsf_linkage_dict = prepare_linkage_dict()

    fields = [{'field' : 'full_name', 'type': 'String', 'has missing' : True},
              {'field' : 'insti_city', 'type': 'String', 'has missing' : True},
              {'field' : 'insti_name', 'type': 'String', 'has missing' : True}]
    linker = dedupe.RecordLink(fields)
    linker.sample(nih_linkage_dict, nsf_linkage_dict, params.n_sample)
    if os.path.exists(params.training_file):
        linker = read_training_file(linker, params.training_file)

    dedupe.consoleLabel(linker)
    print('training linker...')  
    linker.train(ppc=None)
    write_training_file(linker, params.training_file) # update training file

    print('finding threshold...')
    if params.threshold is None:
        params.threshold = linker.threshold(nih_linkage_dict, nsf_linkage_dict,
                                            recall_weight=2.0)

    linked_records = linker.match(nih_linkage_dict, nsf_linkage_dict,
                                  threshold=params.threshold)
    print('# of record linkage = %s' % len(linked_records))
