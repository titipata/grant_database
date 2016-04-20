import os
import dedupe
import numpy as np
import pandas as pd
from unidecode import unidecode
from utils import *

# set up file path and parameters
class Parameters():
    num_cores = 4
    n_sample = 15000
    input_file = '../data/nsf/nsf_grant_investigators.csv'
    output_file = ''
    settings_file = 'nsf_settings'
    training_file = 'nsf_training.json'


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
    fields = [{'field' : 'name', 'type' : 'String', 'has missing' : True},
              {'field' : 'email', 'type' : 'String', 'has missing' : True}]
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
