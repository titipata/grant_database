import pandas as pd


if __name__ == '__main__':
    nih_grant_info = pd.read_csv('../data/nih/nih_grant_info.csv')
    nsf_grant_info = pd.read_csv('../data/nsf/nsf_grant_info.csv')
    affil_df = pd.read_csv('application_vs_affiliation.csv')
    institution_disambiguated = pd.read_csv('institutions_disambiguated.csv')
    institution_disambiguated['affiliation_id'] = range(len(institution_disambiguated))
    nih_abstract_df = pd.read_csv('../data/nih/nih_grant_abstract.csv')
    nsf_column_mapping = {
        'application_id': 'award_id',
        'title': 'title',
        'abstract': 'abstract',
        'amount': 'amount',
        'start_date': 'effective_date',
        'end_date': 'expire_date',
        'instition_name': 'insti_name',
        'city': 'insti_city',
        'state': 'insti_code',
        'country': 'insti_country',
    }

    nih_grant_all_info = nih_grant_info.merge(nih_abstract_df, how='left')
    nih_column_mapping = {
        'application_id': 'application_id',
        'title': 'project_title',
        'abstract': 'abstract_text',
        'amount': 'total_cost',
        'start_date': 'budget_start',
        'end_date': 'budget_end',
        'type': 'activity',
        'instition_name': 'org_name',
        'city': 'org_city',
        'state': 'org_state',
        'country': 'org_country',
    }
    nsf_grant_info['activity'] = None
    nih_unified_df = nih_grant_all_info[nih_column_mapping.values()] \
        .rename(columns={v: k for k, v in nih_column_mapping.items()})
    nih_unified_df['grant'] = 'nih'
    nsf_unified_df = nsf_grant_info[nsf_column_mapping.values()] \
        .rename(columns={v: k for k, v in nsf_column_mapping.items()})
    nsf_unified_df['grant'] = 'nsf'
    all_grants_df = pd.concat((nih_unified_df, nsf_unified_df))

    # linking grants with deduplicated affiliation
    deduped_grants_df = all_grants_df \
        .merge(affil_df.merge(institution_disambiguated)[['application_id', 'grant', 'dedupe_id']])
    # saving
    deduped_grants_df.to_csv('../data/deduped_grants_df.csv', index=False)