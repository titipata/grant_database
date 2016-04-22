import os
import dedupe
import numpy as np
import pandas as pd
import argparse
from unidecode import unidecode
from utils import *


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--threshold', default=0.0, type=float, help='Threshold for merging two elements')
    parser.add_argument('-c', '--cores', help='Number of cores to run the dedupe', default=1, type=int)
    parser.add_argument('-n', help='Number of samples', default=15000, type=int)
    parser.add_argument('-t', '--training', help='Training file', default='nsf_investigator_training.json')
    parser.add_argument('-l', '--skiplabel', help='Skip console labeling', action='store_true')
    parser.add_argument('-p', '--nopredicates',
                        help="Makes deduping significantly faster",
                        action='store_true')
    parser.add_argument('--results', default='nsf_investigator_unique.csv')
    parser.add_argument('-v', '--verbose', action='store_true')

    args = parser.parse_args()

    print('read NSF investigators file...')
    investigators_nsf = pd.read_csv('../data/nsf/nsf_grant_investigators.csv').fillna('')
    investigators_nsf['full_name'] = (investigators_nsf.first_name + ' ' +
                                      investigators_nsf.last_name).map(lambda x: x.lower())
    investigators_nsf = investigators_nsf\
        .applymap(lambda x: preprocess(x))\
        .applymap(lambda x: None if x == '' else x)

    dedupe_dict = dataframe_to_dict(investigators_nsf[['full_name', 'email']])

    # use "full name" and "email" for deduplication
    fields = [{'field' : 'name', 'type' : 'String', 'has missing' : True},
              {'field' : 'email', 'type' : 'String', 'has missing' : True}]
    deduper = dedupe.Dedupe(fields, num_cores=args.cores)
    deduper.sample(dedupe_dict, args.n)

    print('loading labeled data...(you can skip active labeling)')
    if os.path.exists(args.training):
        deduper = read_training_file(deduper, args.training)

    if not args.skiplabel:
        dedupe.consoleLabel(deduper)

    if args.verbose:
        print('training deduper...')
    deduper.train(ppc=None, recall=0.95, index_predicates=not args.nopredicates)

    # write_setting_file(deduper, params.settings_file)
    write_training_file(deduper, args.training) # write

    print('finding threshold...')
    if args.threshold == 0:
        args.threshold = deduper.threshold(dedupe_dict, recall_weight=2.0)

    print('performing dedupe...')
    clustered = deduper.match(dedupe_dict, args.threshold)
    print('# duplicate sets', len(clustered))
