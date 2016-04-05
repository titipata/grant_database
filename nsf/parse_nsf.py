import re
import os
import glob
from lxml import etree
from lxml.etree import tostring
from itertools import chain
import pandas as pd


def stringify_children(node):
    """
    Filters and removes possible Nones in texts and tails
    ref: http://stackoverflow.com/questions/4624062/get-all-text-inside-a-tag-in-lxml
    """
    parts = ([node.text] +
             list(chain(*([c.text, c.tail] for c in node.getchildren()))) +
             [node.tail])
    return ''.join(filter(None, parts))


def list_xml_path(path):
    """
    list all xml file from particular folder (non-recursive)
    """
    path_list = glob.glob(os.path.join(path, '*', '*.xml'), recursive=True)
    return path_list


def parse_nsf_xml(path):
    """
    Parse NSF XML dataset
    return main 2 dictionary output one contains
    grants information and another contains principle
    investigation information
    """
    try:
        tree = etree.parse(path)
    except:
        try:
            tree = etree.fromstring(path)
        except:
            raise Exception("It was not able to read a path, a file-like object, or a string as an XML")

    number = path_list[1].split('/')[-1] # file name
    title = ''.join(tree.xpath('//Award/AwardTitle/text()'))
    effective_date = ''.join(tree.xpath('//Award/AwardEffectiveDate/text()'))
    expire_date = ''.join(tree.xpath('//Award/AwardExpirationDate/text()'))
    amount = ''.join(tree.xpath('//Award/AwardAmount/text()')[0])
    program_officer = ''.join(tree.xpath('//Award/ProgramOfficer/SignBlockName/text()'))
    abstract = ''.join(tree.xpath('//Award/AbstractNarration/text()'))
    award_id = ''.join(tree.xpath('//Award/AwardID/text()'))

    org = tree.xpath('//Award/Organization')
    for o in org:
        org_code = o.find('Code').text
        division = re.sub('\n', '', stringify_children(o.find('Division'))).strip()

    insti = tree.xpath('//Award/Institution')
    for i_ in insti:
        insti_name = i_.find('Name').text
        insti_city = i_.find('CityName').text
        insti_zip = i_.find('ZipCode').text
        insti_phone = i_.find('PhoneNumber').text
        insti_streetaddr = i_.find('StreetAddress').text
        insti_streetname = i_.find('StateName').text
        insti_code = i_.find('StateCode').text


    grant_info = {'file_name': number, 'title': title, 'abstract': abstract,
                  'effective_date': effective_date, 'expire_date': expire_date, 'amount': amount,
                  'program_officer': program_officer, 'award_id': award_id,
                  'org_code': org_code, 'division': division,
                  'insti_name': insti_name, 'insti_city': insti_city, 'insti_zip': insti_zip,
                  'insti_phone': insti_phone, 'insti_streetaddr': insti_streetaddr,
                  'insti_streetname': insti_streetname, 'insti_code': insti_code}

    grant_investigators = []
    t = tree.xpath('//Award/Investigator')
    for t_ in t:
        first_name = t_.findall('FirstName')[0].text
        last_name = t_.findall('LastName')[0].text
        email = t_.findall('EmailAddress')[0].text
        role_code = t_.findall('RoleCode')[0].text
        investigator = {'award_id': award_id,
                        'first_name': first_name, 'last_name': last_name,
                        'email': email, 'role_code': role_code}
        grant_investigators.append(investigator)

    return [grant_info, grant_investigators]


if __name__ == '__main__':
    # for loop through subset of xml files in downloaded data folder
    print("Start parsing ...")
    path_list = list_xml_path('data/')
    grant_info_all = []
    grant_investigators_all = []
    for p in path_list[0:50000]:
        [grant_info, grant_investigators] = parse_nsf_xml(p)
        grant_info_all.append(grant_info)
        grant_investigators_all.extend(grant_investigators)
    grant_investigators_all = list(chain(*grant_investigators_all))
    print("Finish parsing ...")

    grant_info_df = pd.DataFrame(grant_info_all).fillna('')
    grant_investigators_df = pd.DataFrame(grant_investigators_all).fillna('')
    grant_info_df.to_csv('grant_info.csv', index=False)
    grant_investigators_df.to_csv('grant_investigators.csv', index=False)
    print("Finish saving to csv files")
