import pandas as pd
import json

deduped_grants_df = pd.read_csv('../data/dedupe/deduped_grants.csv')
grants_sample_df = deduped_grants_df.fillna('')
grants_sample_df['id'] = grants_sample_df.grant + \
            '_' + \
            grants_sample_df.application_id.map(str)
dlist = grants_sample_df.to_dict('records')

with open('deduped_grants.json','w') as fp:
    for record in dlist:
        json_line = json.dumps(record)+"\n"
        fp.write(json_line)
