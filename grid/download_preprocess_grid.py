"""Downloads and preprocess grid files"""
import urllib
import zipfile
import os
import pandas as pd


# set GRID file. Update when a new version comes along
GRID_URL = 'http://ndownloader.figshare.com/files/4901572'

def download_file():
    """Download latest version of GRID datafile"""
    if os.path.isfile('grid_affil.zip'):
        print("File exists already")
    else:
        print("Downloading file")
        grid_affil = urllib.FancyURLopener()
        grid_affil.retrieve(GRID_URL, 'grid_affil.zip')


def unzip_file():
    """Unzip to folder"""
    if os.path.isdir('raw_grid'):
        print("Files already extracted")
    else:
        print("Extracting files")
        with zipfile.ZipFile('grid_affil.zip', 'r') as zip_file:
            zip_file.extractall('raw_grid')

def preprocess_files():
    def merge_acronyms_aliases(df):
        new_df = df[['grid_id', 'Name', 'City', 'State', 'Country']].iloc[[0]]
        new_name = new_df.Name.iloc[0] + ' ' + \
                   ' '.join(df.acronym.unique()) + ' ' + \
                   ' '.join(df.alias.unique())
        new_df['NameMerged'] = new_name.strip()
        new_df['Acrynyms'] = (' '.join(df.acronym)).strip()
        new_df['Aliases'] = (' '.join(df.alias)).strip()
        return new_df

    print("Reading raw GRID data")
    grid_df = pd.read_csv('raw_grid/grid.csv')
    grid_df.rename(columns={'ID': 'grid_id'}, inplace=True)
    acronyms_df = pd.read_csv('raw_grid/full_tables/acronyms.csv')
    aliases_df = pd.read_csv('raw_grid/full_tables/aliases.csv')
    addresses_df = pd.read_csv('raw_grid/full_tables/addresses.csv')
    grid_enriched_df = grid_df.merge(acronyms_df, how='left').merge(aliases_df, how='left').fillna('')
    grouped_df = grid_enriched_df.groupby('grid_id')
    print("Merging acronyms and aliases")
    merged_acronyms_aliases_df = grouped_df.apply(merge_acronyms_aliases)
    all_affil_info_df = merged_acronyms_aliases_df.merge(addresses_df[['grid_id', 'lat', 'lng']], how='left')
    print("Saving")
    all_affil_info_df.to_csv('../data/grid/grid_merged_affil.csv', index=False)
    print("Done.")

if __name__ == '__main__':
    download_file()
    unzip_file()
    preprocess_files()