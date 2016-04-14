import re
import dedupe
import pandas as pd
from unidecode import unidecode
from nltk.tokenize import WhitespaceTokenizer
from utils import *
w_tokenizer = WhitespaceTokenizer()


class Parameters():
    threshold = 0.1 # if None, we will find threshold
    num_cores = 8
    n_sample = 15000
    settings_file = 'affiliation_settings'
    training_file = 'affiliation_training.json'


def prepare_affiliation_dict():
    """
    Read data from NIH and NSF grant and return
    dedupe affiliation dictionary
    """
    print('load dataset...')
    nih_grant_info = pd.read_csv('../nih/nih_grant_info.csv')
    nsf_grant_info = pd.read_csv('../nsf/nsf_grant_info.csv')
    print('prepare dedupe affiliation dataset...')
    nih_affil_dedupe = nih_grant_info[['org_name', 'org_city', 'org_state']]
    nih_affil_dedupe = nih_affil_dedupe.drop_duplicates(keep='first')\
                            .rename(columns={'org_name': 'insti_name',
                                             'org_city': 'insti_city',
                                             'org_state': 'insti_code'})
    nsf_affil_dedupe = nsf_grant_info[['insti_name', 'insti_city', 'insti_code']].drop_duplicates(keep='first')
    affil_dedupe = pd.concat((nih_affil_dedupe, nsf_affil_dedupe)).fillna('')
    affil_dedupe = affil_dedupe.applymap(lambda x: preprocess(x.lower().strip())).drop_duplicates(keep='first')
    affil_dedupe_dict = dict((i, a) for (i, a) in enumerate(affil_dedupe.to_dict('records')))
    return affil_dedupe_dict


if __name__ == '__main__':
    params = Parameters()
    affil_dedupe_dict = prepare_affiliation_dict()
    fields = [{'field': 'insti_name', 'type': 'String', 'has missing': True},
              {'field': 'insti_city', 'type': 'String', 'has missing': True},
              {'field': 'insti_code', 'type': 'String', 'has missing': True}]
    deduper = dedupe.Dedupe(fields, num_cores=params.num_cores)
    deduper.sample(affil_dedupe_dict, params.n_sample)

    print('load labeled data...(you can skip active labeling)')
    if os.path.exists(params.training_file):
        deduper = read_training_file(deduper, params.training_file)

    print('starting active labeling...')
    dedupe.consoleLabel(deduper)
    deduper.train(ppc=None, recall=0.95)

    write_training_file(deduper, params.training_file) # write

    print('clustering...')
    threshold = deduper.threshold(affil_dedupe_dict, recall_weight=1.0)
    clustered = deduper.match(affil_dedupe_dict, threshold)
    print('# duplicate sets', len(clustered))
