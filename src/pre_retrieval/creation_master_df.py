from cadmus.src.pre_retrieval import pdat_to_datetime
from cadmus.src.parsing import get_medline_doi
from Bio import Entrez, Medline
import uuid
import pickle
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, HTTPError, Timeout
from urllib3.util.retry import Retry
import urllib.request as requests

def creation_master_df(medline_file_name):
    # as input we provide the name of the medline file for parsing out all the individual records
    # now lets run the parser for all the new records 
    # as each record is parsed, we give it a unique index (hexidecimal string)
    # each medline record is then written to file(named the same as the unique index)so that we can find the metadata easily if we want to parse out other fields
    # the medline records are then added to a dictionary which will become the basic master_df.
    
    # set the input file
    in_file = medline_file_name
    # each record will be saved as a pickle file (using the unique index as the name) so we can re-parse medline records retrospectively for our master_df
    medline_ouptut_path = f'./output/medline/p/'
    
    # our main output will be a dictionary ready to be converted into a master df
    parse_d = {}

    #  read in the text file using Medline Parser from biopython
    with open(in_file, 'r') as handle:
        # biopython provides a medline parser so that each record is imported as a dictionary to extract from
        records = Medline.parse(handle)

        # loop through each record creating a set of the most important variables
        for record in records:
            # create a hexidecimal unique id for the record
            index = str(uuid.uuid4().hex)

            # now lets write the indexed medline record to a pickle object (a dictionary)
            pickle.dump(dict(record), open(f"{medline_ouptut_path}{index}.p", 'wb'))


            # we use the get() function for a dictionary to search each field.
            # if the field is populated add the value, else, add 'None'
            pmid = record.get('PMID')
            pmcid = record.get('PMC')
            title = record.get('TI')
            abstract = record.get('AB')
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
                                'authors':authors,
                                'journal':journal_title,
                                'pub_type':pub_type,
                                'pub_date':dt_pdat,
                                'doi': doi,
                                'issn':issn}})

    pm_df = pd.DataFrame.from_dict(parse_d, orient= 'index')

    print('Process Complete')
    return pm_df 