import os
import re
import dedupe
import pandas as pd
import argparse
from utils import *
from nltk.tokenize import WhitespaceTokenizer
import pickle


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
    parser = argparse.ArgumentParser()
    parser.add_argument('--threshold', default=0.0, type=float, help='Threshold for merging two elements')
    parser.add_argument('-c', '--cores', help='Number of cores to run the dedupe', default=1, type=int)
    parser.add_argument('-n', help='Number of samples', default=15000, type=int)
    parser.add_argument('-t', '--training', help='Training file', default='link_affiliation_training.json')
    parser.add_argument('-l', '--skiplabel', help='Skip console labeling', action='store_true')
    parser.add_argument('-p', '--nopredicates',
                        help="Makes deduping significantly faster",
                        action='store_true')
    parser.add_argument('--results', default='final_gridlinked_affils.csv')
    parser.add_argument('-v', '--verbose', action='store_true')

    args = parser.parse_args()

    if args.verbose:
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

    linker = dedupe.RecordLink(fields, num_cores=args.cores)

    linker.sample(grant_affils_dict, grid_dict, args.n)
    if os.path.exists(args.training):
        linker = read_training_file(linker, args.training)

    if not args.skiplabel:
        dedupe.consoleLabel(linker)

    if args.verbose:
        print('training linker...')
    linker.train(ppc=None, index_predicates=not args.nopredicates)
    write_training_file(linker, args.training) # update training file

    if args.verbose:
        print('finding threshold...')
    if args.threshold == 0:
        args.threshold = linker.threshold(grid_dict, grant_affils_dict,
                                            recall_weight=0.5)


    linked_records = linker.match(grid_dict, grant_affils_dict,
                                  threshold=args.threshold)
    # add grid_id to grant_affils_dict
    id1 = np.array([i1[0] for i1, p in linked_records])
    id2 = np.array([i1[1] for i1, p in linked_records])

    grid_df2 = pd.DataFrame(grid_dict).T
    grant_affils_df2 = pd.DataFrame(grant_affils_dict).T
    # linking grid to grants affiliations
    grant_affils_df2['grid_id'] = None
    grant_affils_df2.grid_id.iloc[id2] = np.array(grid_df2.grid_id.iloc[id1])
    if args.verbose:
        print("Saving results")
    grant_affils_df2.to_csv(args.results, index=False)
    if args.verbose:
        print('# of record linkage = %s' % len(linked_records))
