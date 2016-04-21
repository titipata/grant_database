import re
import glob
from itertools import chain
import pandas as pd


def remove_contact_str(text):
    """Remove string '(contact)' from """
    return re.sub('\(contact\)', '', text).strip()


def process_pi_id(pi_id):
    """Transform PI ids in NIH format to list"""
    pi_ids = [n for n in map(lambda s: s.strip(), pi_id.split(';')) if n != '']
    return list(map(remove_contact_str, pi_ids))


def add(d, k, v):
    """Add key and value to dictionary"""
    d[k] = v
    return d


def process_pi_name(pi_name):
    """Input NIH format string and return list of dictionary of PIs"""
    pis_list = []
    pis = [n for n in map(lambda s: s.strip(), pi_name.split(';')) if n != '']
    for pi in pis:
        name = pi.split(',')
        try:
            if name[0] != '' and name[1] != '':
                pi_dict = {'first_name': name[-1].strip(), 'last_name': name[0].strip()}
                if 'contact' in name[0] or 'contact' in name[1] or len(pis) == 1:
                    pi_dict['contact'] = True
                else:
                    pi_dict['contact'] = False
                pis_list.append(pi_dict)
        except:
            print("skip line...")
    return pis_list


if __name__ == '__main__':
    print("Create investigators dataset ...")
    pi_df_all = []
    path_list = glob.glob('data/project/*/*.csv')
    for p in path_list:
        print("Extract authors from %s ..." % p.split('/')[-1])
        df = pd.read_csv(p, encoding = "ISO-8859-1").fillna('')
        pi_dicts = zip(df.APPLICATION_ID,
                       df.PI_IDS.map(lambda idx: process_pi_id(idx)),
                       df.PI_NAMEs.map(lambda n: process_pi_name(n)))

        pi_dicts_all = []
        for (application_id, pi_id, d) in pi_dicts:
            d = [add(d, 'pi_id', i) for (i, d) in zip(pi_id, d)] # add pi_id to dict
            d = list(map(lambda d: add(d, 'application_id', application_id), d)) # add application_id to dict
            pi_dicts_all.append(d)
        pi_dicts_all = list(chain(*pi_dicts_all)) # flatten list of list
        pi_df = pd.DataFrame(pi_dicts_all)
        pi_df_all.append(pi_df)
    pi_df_all = pd.concat(pi_df_all) # concat all dataframe
    pi_df_all.to_csv('nih_grant_investigators.csv', index=False)
    print("Finish saving to csv file ...")
