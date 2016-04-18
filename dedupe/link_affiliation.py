import os
import re
import dedupe
import pandas as pd
from utils import *
from nltk.tokenize import WhitespaceTokenizer
import pickle
wtk = WhitespaceTokenizer()


class Parameters():
    threshold = None # if None, we will find threshold
    num_cores = 8
    n_sample = 15000
    settings_file = 'link_affiliation_settings'
    training_file = 'link_affiliation_training.json'


def write_training_file(deduper, filename='link_affiliation_training.json'):
    """Give a deduper, write a training file"""
    with open(filename, 'w') as tf:
        deduper.writeTraining(tf)
    print("Training file saved")


def prepare_df():
    deduped_affils_df = pd.read_csv('institutions_disambigutated.csv')
    # merge grants affils
    def select_longest_names(df):
        longest_insti_name = np.argmax(np.array(df.insti_name.map(len)))
        longest_insti_city = np.argmax(np.array(df.insti_city.map(len)))
        new_df = df.iloc[[0]]
        new_df['insti_name'] = df.insti_name.iloc[longest_insti_name]
        new_df['insti_city'] = df.insti_city.iloc[longest_insti_city]
        return new_df

    deduped_affils_merged_df = deduped_affils_df.fillna('') \
        .groupby('dedupe_id') \
        .apply(select_longest_names) \
        .reset_index(drop=True) \
        .applymap(lambda x: None if x == '' else x)

    grid_df = pd.read_csv('../data/grid/grid_merged_affil.csv')
    grid_df['insti_name'] = grid_df.NameMerged.apply(preprocess).apply(lambda x: None if x == '' else x)
    grid_df['insti_city'] = grid_df.City.apply(preprocess).apply(lambda x: None if x == '' else x)

    return deduped_affils_merged_df, grid_df


if __name__ == '__main__':
    params = Parameters()
    n_sample = params.n_sample

    print('prepare dataset...')
    if not os.path.isfile('grid_dict.pickle') or not os.path.isfile('grant_affils_dict.pickle'):
        grant_affils_df, grid_df = prepare_df()
        grant_affils_dict = dataframe_to_dict(grant_affils_df)
        grid_dict = dataframe_to_dict(grid_df)
        pickle.dump(grant_affils_dict, open('grant_affils_dict.pickle', 'w'), protocol=2)
        pickle.dump(grid_dict, open('grid_dict.pickle', 'w'), protocol=2)
    else:
        grant_affils_dict = pickle.load(open('grant_affils_dict.pickle', 'r'))
        grid_dict = pickle.load(open('grid_dict.pickle', 'r'))

    fields = [{'field' : 'insti_city', 'type': 'String', 'has missing' : True},
              {'field' : 'insti_name', 'type': 'String', 'has missing' : True}]

    linker = dedupe.RecordLink(fields)

    linker.sample(grant_affils_dict, grid_dict, params.n_sample)
    if os.path.exists(params.training_file):
        linker = read_training_file(linker, params.training_file)

    # dedupe.consoleLabel(linker)
    print('training linker...')
    linker.train(ppc=None)
    write_training_file(linker, params.training_file) # update training file

    print('finding threshold...')
    if params.threshold is None:
        params.threshold = linker.threshold(grid_dict, grant_affils_dict,
                                            recall_weight=0.5)

    linked_records = linker.match(grid_dict, grant_affils_dict,
                                  threshold=params.threshold)
    # add grid_id to grant_affils_dict
    id1 = np.array([i1[0] for i1, p in linked_records])
    id2 = np.array([i1[1] for i1, p in linked_records])

    grid_df2 = pd.DataFrame(grid_dict).T
    grid_affils_df2 = pd.DataFrame(grant_affils_dict).T
    # linking grid to grants affiliations
    grid_affils_df2['grid_id'] = None
    grid_affils_df2.grid_id.iloc[id2] = grid_df2.grid_id.iloc[id1]
    print("Saving results")
    grid_affils_df2.to_csv('final_grid_affils.csv', index=False)
    print('# of record linkage = %s' % len(linked_records))
