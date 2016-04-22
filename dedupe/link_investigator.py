import os
import re
import dedupe
import pandas as pd
import argparse
from utils import *


def prepare_linkage_dict():
    """
    Read data from NIH and NSF folder and
    return dedupe format dictionary
    """

    cname = ['full_name', 'insti_name', 'insti_city']
    nih_investigators = pd.read_csv('../data/nih/nih_grant_investigators.csv').fillna('')
    nih_investigators['full_name'] = nih_investigators.first_name + ' ' + \
                                     nih_investigators.last_name
    nih_info = pd.read_csv('../data/nih/nih_grant_info.csv').fillna('')
    nsf_investigators = pd.read_csv('../data/nsf/nsf_grant_investigators.csv').fillna('')
    nsf_info = pd.read_csv('../data/nsf/nsf_grant_info.csv')\
        .fillna('')\
        .rename(columns={'org_city': 'insti_city',
                         'org_name': 'insti_name'})
    nsf_investigators['full_name'] = nsf_investigators.first_name + ' ' + \
                                     nsf_investigators.last_name

    nih_investigators = nih_investigators.merge(nih_info[['application_id', 'insti_name', 'insti_city']])
    nsf_investigators = nsf_investigators.merge(nsf_info[['award_id', 'insti_name','insti_city']])

    nih_investigators[cname] = nih_investigators[cname].\
        applymap(lambda x: preprocess(x)).\
        applymap(lambda x: None if x == '' else x)
    nsf_investigators[cname] = nsf_investigators[cname].\
        applymap(lambda x: preprocess(x)).\
        applymap(lambda x: None if x == '' else x)

    nih_linkage = nih_investigators[['pi_id', 'full_name', 'insti_name', 'insti_city']]\
                    .drop_duplicates(subset='pi_id', keep='first').fillna('')
    nsf_linkage = nsf_investigators[['full_name', 'insti_name', 'insti_city']]\
                    .drop_duplicates() # we'll replace with dedupe nsf later on

    nih_linkage_dict = dataframe_to_dict(nih_linkage[cname])
    nsf_linkage_dict = dataframe_to_dict(nsf_linkage[cname])

    return nih_linkage_dict, nsf_linkage_dict


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--threshold', default=0.0, type=float, help='Threshold for merging two elements')
    parser.add_argument('-c', '--cores', help='Number of cores to run the dedupe', default=1, type=int)
    parser.add_argument('-n', help='Number of samples', default=15000, type=int)
    parser.add_argument('-t', '--training', help='Training file', default='link_investogator_training.json')
    parser.add_argument('-l', '--skiplabel', help='Skip console labeling', action='store_true')
    parser.add_argument('-p', '--nopredicates',
                        help="Makes deduping significantly faster",
                        action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')

    args = parser.parse_args()

    print('prepare dataset for dedupe...')
    nih_linkage_dict, nsf_linkage_dict = prepare_linkage_dict()

    fields = [{'field' : 'full_name', 'type': 'String', 'has missing' : True},
              {'field' : 'insti_city', 'type': 'String', 'has missing' : True},
              {'field' : 'insti_name', 'type': 'String', 'has missing' : True}]
    linker = dedupe.RecordLink(fields)
    linker.sample(nih_linkage_dict, nsf_linkage_dict, args.n)
    if os.path.exists(args.training):
        linker = read_training_file(linker, args.training)

    if not args.skiplabel:
        dedupe.consoleLabel(linker)

    if args.verbose:
        print('training linker...')
    linker.train(ppc=None, index_predicates=not args.nopredicates)
    write_training_file(linker, args.training) # update training file

    print('finding threshold...')
    if args.threshold == 0:
        args.threshold = linker.threshold(nih_linkage_dict, nsf_linkage_dict,
                                          recall_weight=2.0)

    linked_records = linker.match(nih_linkage_dict, nsf_linkage_dict,
                                  threshold=args.threshold)
    print('# of record linkage = %s' % len(linked_records))
