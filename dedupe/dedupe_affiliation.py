import pandas as pd
from utils import *
w_tokenizer = WhitespaceTokenizer()


class Parameters():
    threshold = 0.1 # if None, we will find threshold
    num_cores = 8
    n_sample = 15000
    settings_file = 'affiliation_settings'
    training_file = 'affiliation_training.json'


def merge_nsf_nih_df():
    """
    Read data from NIH and NSF grant and return
    dedupe affiliation dictionary
    """
    nih_grant_info = pd.read_csv('../data/nih/nih_grant_info.csv')
    nsf_grant_info = pd.read_csv('../data/nsf/nsf_grant_info.csv')

    nih_affil_dedupe = nih_grant_info[['org_name', 'org_city', 'org_state']]
    nih_affil_dedupe = nih_affil_dedupe\
        .drop_duplicates(keep='first')\
        .rename(columns={'org_name': 'insti_name',
                         'org_city': 'insti_city',
                         'org_state': 'insti_code'})

    nsf_affil_dedupe = nsf_grant_info[['insti_name', 'insti_city', 'insti_code']].drop_duplicates(keep='first')

    affil_dedupe = pd.concat((nih_affil_dedupe, nsf_affil_dedupe)).fillna('')
    affil_dedupe = affil_dedupe.fillna('').\
        applymap(lambda x: format_text(x.lower().strip())).\
        drop_duplicates(keep='first')

    return affil_dedupe


if __name__ == '__main__':
    params = Parameters()
    all_affil_df = merge_nsf_nih_df()
    all_affil_dict = dh.dataframe_to_dict(all_affil_df)

    fields = [{'field': 'insti_name', 'type': 'String', 'has missing': True},
              {'field': 'insti_city', 'type': 'String', 'has missing': True},
              {'field': 'insti_code', 'type': 'String', 'has missing': True}]
    deduper = dedupe.Dedupe(fields, num_cores=params.num_cores)
    deduper.sample(all_affil_dict, params.n_sample)

    print('load labeled data...(you can skip active labeling)')
    if os.path.exists(params.training_file):
        deduper = read_training_file(deduper, params.training_file)

    print('starting active labeling...')
    dedupe.consoleLabel(deduper)
    deduper.train(ppc=None, recall=0.95)

    write_training_file(deduper, params.training_file)

    print('clustering...')
    threshold = deduper.threshold(all_affil_dict, recall_weight=1.0)
    all_affil_df_deduped = add_dedupe_col(all_affil_df, all_affil_dict, deduper, threshold)
    all_affil_df_deduped.to_csv('institutions_disambigutated.csv', index=False)

