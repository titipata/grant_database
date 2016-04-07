import os
import glob
import pandas as pd


def create_grant_info():
    """Read and concat all downloaded NIH grant projects"""
    path_list = glob.glob('data/proj/*/*.csv', recursive=True)
    sel_name = ['APPLICATION_ID', 'ACTIVITY', 'APPLICATION_TYPE',
                'AWARD_NOTICE_DATE', 'BUDGET_START', 'BUDGET_END',
                'IC_NAME', 'ORG_NAME', 'ORG_CITY', 'ORG_STATE',
                'ORG_DISTRICT', 'ORG_ZIPCODE', 'PROJECT_TITLE', 'PROJECT_TERMS',
                'ED_INST_TYPE', 'TOTAL_COST', 'PHR']
    cname = list(map(lambda x: x.lower(), sel_name)) # lower case column name
    df_all = []
    for p in path_list:
        df = pd.read_csv(p, encoding = "ISO-8859-1").fillna('')
        df_sel = df[sel_name]
        df_sel.columns = cname
        df_all.append(df[cname])
    df_all = pd.concat(df_all) # concat all dataframe
    return df_all


def create_grant_abstract():
    """Read and concat all downloaded NIH grant abstracts"""
    path_list = glob.glob('data/abs/*/*.csv', recursive=True)
    df_all = []
    for p in path_list:
        df = pd.read_csv(p, encoding = "ISO-8859-1")
        col_name = list(map(lambda x: x.lower(), df.columns))
        df.columns = col_name
        df_all.append(df)
    df_all = pd.concat(df_all) # concat all dataframe
    return df_all


if __name__ == '__main__':
    df_info = create_grant_info()
    df_abstract = create_grant_abstract()
    # df_merge = df_info.merge(df_abstract, how='left') # merge 2 tables together
    # df_merge.fillna('').to_csv('nih_grant_info.csv', index=False)
    df_info.to_csv('nih_grant_info.csv', index=False)
    df_abstract.to_csv('nih_grant_abstract.csv', index=False)
