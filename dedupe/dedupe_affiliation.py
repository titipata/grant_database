import pandas as pd
import argparse
from itertools import chain
from utils import *


def create_unique_id(nih_grant_info, nsf_grant_info, affil_index):
    """
    Give dataframe from NIH/NSF grant and list of duplicated index
    create table with unique id of same affiliation string
    """
    nih_grant_info['grant'] = 'nih'
    nsf_grant_info['grant'] = 'nsf'
    nih_grant_concat = nih_grant_info[['application_id', 'grant']]
    nsf_grant_concat = nsf_grant_info[['award_id', 'grant']]\
        .rename(columns={'award_id': 'application_id'})
    grant_df = pd.concat((nih_grant_concat, nsf_grant_concat), axis=0)\
        .reset_index(drop=True)
    grant_df['index'] = grant_df.index
    affil_merge = [list(zip(a, [i]*len(a))) for (i, a) in enumerate(affil_index)]
    affil_merge = list(chain(*affil_merge)) # flatten list
    affil_merge = pd.DataFrame(affil_merge, columns=['index', 'affiliation_id'])
    affil_merge_df = grant_df.merge(affil_merge, on='index').drop(['index'], axis=1)
    return affil_merge_df


def merge_nsf_nih_df():
    """
    Read data from NIH and NSF grant and return
    dedupe affiliation dictionary
    """
    nih_grant_info = pd.read_csv('../data/nih/nih_grant_info.csv')
    nsf_grant_info = pd.read_csv('../data/nsf/nsf_grant_info.csv')

    nih_affil_dedupe = nih_grant_info[['org_name', 'org_city', 'org_state']]
    nih_affil_dedupe = nih_affil_dedupe\
        .rename(columns={'org_name': 'insti_name',
                         'org_city': 'insti_city',
                         'org_state': 'insti_code'})

    nsf_affil_dedupe = nsf_grant_info[['insti_name', 'insti_city', 'insti_code']]

    affil_dedupe = pd.concat((nih_affil_dedupe, nsf_affil_dedupe)).fillna('')
    affil_dedupe = affil_dedupe.fillna('').\
        applymap(lambda x: preprocess(x.lower().strip())).\
        reset_index(drop=True) # preprocess all

    # group index of affiliation with same (name, city, code)
    group_affil = affil_dedupe.fillna('').groupby(('insti_name', 'insti_city', 'insti_code'))
    group_affil_index = pd.DataFrame(group_affil\
        .apply(lambda x: np.array(x.index)))\
        .reset_index() # dataframe of grouped same row

    # return table of (grant, application id, affiliation id)
    group_index = list(group_affil_index[0])
    affil_merge_df = create_unique_id(nih_grant_info, nsf_grant_info, group_index)

    all_affil_df = group_affil_index[['insti_name', 'insti_city', 'insti_code']]
    all_affil_df = all_affil_df.applymap(lambda x: None if x is '' else x)

    return all_affil_df, affil_merge_df


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--threshold', default=0.0, type=float, help='Threshold for merging two elements')
    parser.add_argument('-c', '--cores', help='Number of cores to run the dedupe', default=1, type=int)
    parser.add_argument('-n', help='Number of samples', default=15000, type=int)
    parser.add_argument('-s', '--settings', help='Settings file', default='affiliation_settings')
    parser.add_argument('-t', '--training', help='Training file', default='affiliation_training.json')
    parser.add_argument('-l', '--skiplabel', help='Skip console labeling', action='store_true')
    parser.add_argument('--results', default='institutions_disambiguated.csv')
    parser.add_argument('-v', '--verbose', action='store_true')

    args = parser.parse_args()

    all_affil_df, affil_merge_df = merge_nsf_nih_df()
    all_affil_dict = dataframe_to_dict(all_affil_df)

    fields = [{'field': 'insti_name', 'type': 'String', 'has missing': True},
              {'field': 'insti_city', 'type': 'String', 'has missing': True},
              {'field': 'insti_code', 'type': 'String', 'has missing': True}]
    deduper = dedupe.Dedupe(fields, num_cores=args.cores)
    deduper.sample(all_affil_dict, args.n)

    if args.verbose:
        print('loading labeled data')

    if os.path.exists(args.training):
        deduper = read_training_file(deduper, args.training)

    print('starting active labeling...')

    if not args.skiplabel:
        dedupe.consoleLabel(deduper)

    deduper.train(ppc=None, recall=0.95)

    write_training_file(deduper, args.training)

    if args.threshold == 0:
        print('finding threshold')
        threshold = deduper.threshold(all_affil_dict, recall_weight=1.0)
    else:
        threshold = args.threshold

    print('clustering...')
    all_affil_df_deduped = add_dedupe_col(all_affil_df, all_affil_dict, deduper, threshold)
    print('saving results')
    all_affil_df_deduped.to_csv(args.results, index=False)

    print('saving table between application id and unique affiliation')
    affil_merge_df.to_csv('application_vs_affiliation.csv', index=False)
