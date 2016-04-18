import pandas as pd
import argparse
from utils import *


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
        applymap(lambda x: preprocess(x.lower().strip())) # preprocess all

    # group index in order to refer back later
    group_affil = affil_dedupe.fillna('').groupby(('insti_name', 'insti_city', 'insti_code'))
    affil_dedupe = pd.DataFrame(group_affil\
        .apply(lambda x: np.array(x.index)))\
        .reset_index()

    return affil_dedupe[['insti_name', 'insti_city', 'insti_code']], list(affil_dedupe[0])


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

    all_affil_df, all_affil_index = merge_nsf_nih_df()
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
