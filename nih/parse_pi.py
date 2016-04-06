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
        if name[0] != '' and name[1] != '':
            pi_dict = {'first_name': name[-1].strip(), 'last_name': name[0].strip()}
            if 'contact' in name[0] or 'contact' in name[1] or len(pis) == 1:
                pi_dict['contact'] = True
            else:
                pi_dict['contact'] = False
            pis_list.append(pi_dict)
    return pis_list


if __name__ == '__main__':
    # example of getting one author table from year 2015
    path_list = glob.glob('data/proj/*/*.csv', recursive=True)
    print("Extract authors from %s ..." % path_list[30].split('/')[-1])
    df = pd.read_csv(path_list[30], encoding = "ISO-8859-1")
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
    pi_df.to_csv('nih_grant_investigators.csv', index=False)
    print("Finish saving to csv file")
