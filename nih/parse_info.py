import pandas as pd
import glob


if __name__ == '__main__':
    # concat all project csv and put into one csv
    path_list = glob.glob('nih/data/proj/*/*.csv', recursive=True)
    sel_name = ['APPLICATION_ID', 'ACTIVITY', 'APPLICATION_TYPE',
                'AWARD_NOTICE_DATE', 'BUDGET_START', 'BUDGET_END',
                'IC_NAME', 'ORG_NAME', 'ORG_CITY', 'ORG_STATE',
                'ORG_DISTRICT', 'ORG_ZIPCODE', 'PROJECT_TITLE', 'PROJECT_TERMS',
                'ED_INST_TYPE', 'TOTAL_COST', 'IC_NAME', 'PHR']
    cname = list(map(lambda x: x.lower(), sel_name)) # lower case column name

    df_all = []
    for p in path_list:
        df = pd.read_csv(p, encoding = "ISO-8859-1").fillna('')
        df_sel = df[sel_name]
        df_sel.columns = cname
        df_all.append(df[sel_name])
    df_all = pd.concat(df_all) # concat all files
    df_all.to_csv('nih_grant_info.csv', index=False)
