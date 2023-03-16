from cadmus.pre_retrieval.pdat_to_datetime import pdat_to_datetime
from cadmus.parsing.get_medline_doi import get_medline_doi
from Bio import Entrez, Medline
import uuid
import pickle
import json
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, HTTPError, Timeout
from urllib3.util.retry import Retry
import urllib.request as requests
import zipfile

def creation_retrieved_df(medline_file_name):
    # as input we provide the name of the medline file for parsing out all the individual records
    # now lets run the parser for all the new records 
    # as each record is parsed, we give it a unique index (hexidecimal string)
    # each medline record is then written to file(named the same as the unique index)so that we can find the metadata easily if we want to parse out other fields
    # the medline records are then added to a dictionary which will become the basic retrieved_df.
    
    # each record will be saved as a json file (using the unique index as the name) so we can re-parse medline records retrospectively for our retrieved_df
    medline_ouptut_path = f'./output/medline/json/'
    
    # our main output will be a dictionary ready to be converted into a retrieved df
    parse_d = {}

    with zipfile.ZipFile("./output/medline/txts/medline_output.txt.zip", "r") as z:
        for filename in z.namelist():
            with z.open(filename) as f:
                d = f.readlines()
            f.close()
    z.close()
    for i in range(len(d)):
        d[i] = d[i].decode('utf-8')

    # biopython provides a medline parser so that each record is imported as a dictionary to extract from
    records = Medline.parse(d)

    # loop through each record creating a set of the most important variables
    for record in records:
        # create a hexidecimal unique id for the record
        index = str(uuid.uuid4().hex)

        # now lets write the indexed medline record to a json object (a dictionary)
        result = dict(record)
        with zipfile.ZipFile(f"{medline_ouptut_path}{index}.json.zip", mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zip_file:
            dumped_JSON: str = json.dumps(result, ensure_ascii=False, indent=4)
            zip_file.writestr(f"{index}.json", data=dumped_JSON)
            zip_file.testzip()
        zip_file.close()

        # we use the get() function for a dictionary to search each field.
        # if the field is populated add the value, else, add 'None'
        pmid = record.get('PMID')
        pmcid = record.get('PMC')
        title = record.get('TI')
        # sometimes the title is a book title - check BTI if TI is empty
        if title == None or title == '':
            title = record.get('BTI')
        abstract = record.get('AB')
        # sometimes the abstract is added later and stored as other Abstract OAB
        if abstract == None or abstract == '':
            abstract = record.get('OAB')
        mesh_terms = record.get('MH')
        authors = record.get('AU')
        journal_title = record.get('JT')
        pub_type = record.get('PT')
        issn = record.get('IS')

        # use our function above to get a datetime obj for the pdat provided (or None)                               
        pdat = record.get('DP')
        dt_pdat = pdat_to_datetime(pdat)                                

        # now get the doi using the function above          
        doi = get_medline_doi(record)

        # now we save all the variables to the parse dictionary
        parse_d.update({index:{'pmid': pmid,
                            'pmcid':pmcid,
                            'title': title,
                            'abstract': abstract,
                            'mesh': mesh_terms,
                            'authors':authors,
                            'journal':journal_title,
                            'pub_type':pub_type,
                            'pub_date':dt_pdat,
                            'doi': doi,
                            'issn':issn}})

    pm_df = pd.DataFrame.from_dict(parse_d, orient= 'index')
    index_to_keep = []
    for i in range(len(pm_df)):
        if 'Preprint' in pm_df.pub_type.iloc[i]:
            pass
        else:
            index_to_keep.append(pm_df.index[i])
    pm_df = pm_df[pm_df.index.isin(index_to_keep)]
    print('Process Complete')
    return pm_df 