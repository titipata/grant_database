import os
import argparse
import numpy as np
import pandas as pd
from bokeh.plotting import figure, output_file, show
from utils import scatter_with_hover


def process_date(date):
    """Process grant date to year"""
    try:
        y = int(date.split('/')[-1])
    except:
        y = 0
    return y


def process_amount(amount):
    """convert amount to integer"""
    try:
        amount = int(amount)
    except:
        amount = 0
    return amount


def summarize_grant(df, dedupe_id=0, grant_type=None):
    """
    Put dataframe with columns of
    dedupe_id, year, type, grant, n_grants, amount

    input:
        dedupe_id - integer of interested affiliation
        grant_type - type of grant either 'nih', 'nsf' or None
    """
    query_text = 'dedupe_id == %s' % dedupe_id
    if grant_type:
        query_text += ' and grant == "%s"' % grant_type
    df_sel = df.query(query_text)
    df_group = df_sel.groupby(['year'])
    df_summary = df_group.agg({'amount': lambda x: np.sum(x), 'n_grants': lambda x: np.sum(x)}).reset_index()
    return df_summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', default=2854, type=int, help='Dedupe index')
    parser.add_argument('--type', default=None, type=str,
                        help='either NIH or NSF or None if not specify')
    parser.add_argument('--result', default='group_grant_df.pickle')
    parser.add_argument('--output', default='grant_summary.html',
                        help='Output html path for Bokeh')
    parser.add_argument('--width', type=int, default=800)
    parser.add_argument('--height', type=int, default=300)

    args = parser.parse_args()

    if not os.path.isfile(args.result):
        print('load and group deduped grant...')
        grant_df = pd.read_csv('../data/deduped_grants.csv')
        grant_df['year'] = grant_df.start_date.map(lambda s: process_date(s))
        grant_df['amount'] = grant_df.amount.map(lambda s: process_amount(s))
        grant_df.fillna('', inplace=True)
        group_id = grant_df.groupby(['dedupe_id', 'year', 'type', 'grant'])
        aggregations = {
            'application_id': 'count',
            'amount': lambda x: np.sum(x)
        }
        group_grant_df = group_id.agg(aggregations).reset_index()
        group_grant_df.rename(columns={'application_id':'n_grants'}, inplace=True)
        group_grant_df.to_pickle(args.result)
        print('save group deduped grant to %s...' % args.result)
    else:
        print('load existing grouped deduped grant...')
        group_grant_df = pd.read_pickle(args.result)

    affiliation = pd.read_csv('../data/deduped_affiliations.csv')
    affiliation_dict = dict(zip(affiliation.dedupe_id, affiliation.institution_name))

    grant_type = args.type
    if grant_type is not None:
        grant_type = grant_type.lower()
    df = summarize_grant(group_grant_df, dedupe_id=args.index, grant_type=grant_type).fillna('')
    x = 'year'
    y = 'n_grants'
    val = 'amount'
    f = figure(
        width=args.width,
        height=args.height,
        title=affiliation_dict[args.index].title(),
        y_axis_type="log",
        x_axis_label="year",
        x_range=[1970, 2020],
        y_range=[np.min(df[y])-5, np.max(df[y])*2],
        y_axis_label="Number of grants",
        tools = "save"
    )
    output_file(args.output)
    if len(df) == 0:
        print("no grants found for this dedupe index...")
    else:
        fig = scatter_with_hover(df, x, y, fig=f, marker='o', cols=[x, y, val])
        show(fig)
