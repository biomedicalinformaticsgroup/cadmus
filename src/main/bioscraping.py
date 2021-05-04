import datetime
import json
import os
import pickle
import random
import re
import shutil
import string
import tarfile
import time
import urllib.parse
import urllib.request as request
import uuid
from collections import Counter
from contextlib import closing
from datetime import timedelta
from pathlib import Path
from time import sleep
from urllib.parse import urlparse
import platform
import lxml

import bs4
import numpy as np
import pandas as pd
import requests
import tika
import urllib3
import wget
from Bio import Entrez, Medline
from bs4 import BeautifulSoup
from dateutil import parser
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, HTTPError, Timeout
from urllib3.util.retry import Retry
from urllib3.exceptions import NewConnectionError

os.environ['TIKA_SERVER_JAR'] = 'https://repo1.maven.org/maven2/org/apache/tika/tika-server/'+tika.__version__+'/tika-server-'+tika.__version__+'.jar'
from tika import parser

from cadmus.src.pre_retrieval import output_files
from cadmus.src.retrieval import search_terms_to_pmid_list
from cadmus.src.pre_retrieval import pmids_to_medline_file
from cadmus.src.parsing import get_medline_doi
from cadmus.src.pre_retrieval import pdat_to_datetime
from cadmus.src.pre_retrieval import creation_master_df
from cadmus.src.pre_retrieval import ncbi_id_converter_batch
from cadmus.src.retrieval import HTTP_setup
from cadmus.src.retrieval import get_request
from cadmus.src.retrieval import get_tdm_links
from cadmus.src.pre_retrieval import key_fields
from cadmus.src.pre_retrieval import get_crossref_links_and_licenses
from cadmus.src.parsing import doctype
from cadmus.src.parsing import clean_soup
from cadmus.src.parsing import xml_body_p_parse
from cadmus.src.parsing import get_ab
from cadmus.src.parsing import html_to_parsed_text
from cadmus.src.parsing import html_get_ab
from cadmus.src.retrieval import redirect_check
from cadmus.src.parsing.html_response_to_parse_d import html_response_to_parse_d
from cadmus.src.parsing import xml_response_to_parse_d
from cadmus.src.parsing import xml_file_to_parse_d
from cadmus.src.parsing import remove_link
from cadmus.src.parsing import clean_pdf_body
from cadmus.src.parsing import limit_body
from cadmus.src.parsing import get_abstract_pdf
from cadmus.src.parsing import pdf_file_to_parse_d
from cadmus.src.retrieval import get_base_url
from cadmus.src.retrieval import html_link_from_meta
from cadmus.src.retrieval import pdf_links_from_meta
from cadmus.src.retrieval import explicit_pdf_links
from cadmus.src.retrieval import links_from_a_tags
from cadmus.src.retrieval import complete_html_link_parser
from cadmus.src.parsing import text_prep
from cadmus.src.evaluation import abstract_similarity_score
from cadmus.src.evaluation import body_unique_score
from cadmus.src.parsing import get_attrs
from cadmus.src.evaluation import evaluation_funct
from cadmus.src.parsing import tgz_unpacking
from cadmus.src.retrieval import pubmed_linkout_parse
from cadmus.src.main import retrieval
from cadmus.src.retrieval.parse_link_retrieval import parse_link_retrieval
from cadmus.src.pre_retrieval import check_for_master_df
from cadmus.src.retrieval import clear
from cadmus.src.post_retrieval import working_text
from cadmus.src.retrieval import is_ipython
from cadmus.src.post_retrieval import evaluation
from cadmus.src.post_retrieval import correct_date_format

def bioscraping(input_function, email, api_key, click_through_api_key, start = None, idx = None , full_search = None):
    
    # lets check whether this is an update of a previous search or a new search.
    update = check_for_master_df()
    
    if update:
        print('There is already a Master Dataframe, we shall add new results to this existing dataframe, excluding duplicates.')
        # save the original df to use downstream.
        original_df = pickle.load(open('./output/master_df/master_df2.p', 'rb'))
        # we need to save all the find all the pmids where already a PDF and (HTML or XML)
        # these pmids will then be removed from the the search df
        original_pmids = []
        drop_lines = []
        # loop through all rows checking the criteria
        if full_search == None:
            print('We are not updating the previous search(es) of the DataFrame, only looking for new lines')
            original_pmids = (np.array(original_df.pmid))
        if full_search == 'light':
            print('We are doing a light search, from the previous search we are only going to take a look at the missing working_text')
            for index, row in original_df.iterrows():
                if row.working_text == '' or row.working_text == None or row.working_text != row.working_text or row.working_text[:4] == 'ABS:':
                    drop_lines.append(index)
                else:
                    original_pmids.append(row['pmid'])
        if full_search == 'heavy':
            print('We are doing a heavy search, trying to find new taged version from previous search')
            for index, row in original_df.iterrows():
                if (row['pdf'] == 1 and row['html'] == 1) or (row['pdf'] == 1 and row['xml'] == 1):
                    original_pmids.append(row['pmid'])
                else:
                    drop_lines.append(index)
        
    else:
        if start != None:
            pass
        else:    
            print('This is a new project, creating all directories')
    
    # search strings and pmid lists have the same basic pipeline +/- the search at the start
    if type(input_function) == str or input_function[0].isdigit() == True:
        print('This look like a search string or list of pmids. \nIf this is not correct Please stop now')
        # create all the output directories if they do not already exist
        
        if input_function == '':
            print('You did not enter any search term')

        else:
            # run the search if the input is a string
            if type(input_function) == str:
                # This is the search step when a query string is provided resulting in a list of pmids within a dictionary
                results_d = search_terms_to_pmid_list(input_function, email, api_key)
            else:
                # the input is a list of pmids we just need to make a results_d to maintain the output variables
                
                # get todays date 
                date = datetime.datetime.today()
                date = f'{date.year}_{date.month}_{date.day}_{date.hour}_{date.minute}'
                # construct the output dict
                results_d = {'date':date, 'search_term':'', 'total_count':len(input_function), 'pmids':input_function}
                # save the output dictionary for our records of what terms used and number of records returned for a given date.
                pickle.dump(results_d, open(f'./output/esearch_results/{date}.p', 'wb'))

            # at this stage we need to see if the search is a new search or update of previous list.
            if update:
                # when this is an update we need to remove the previously used pmids from our current pipeline (the orignal df and new df will be merged at the end)
                current_pmids = results_d.get('pmids')
                # use set difference to get the new pmids only
                new_pmids = list(set(current_pmids).difference(set(original_pmids)))
                if len(new_pmids) == 0:
                    print('There are no new lines since your previous search stop the function.')
                    exit()
                else:
                    print(f'There are {len(new_pmids)} new lines since last run.')
                # set the new pmids into the results d for the next step
                results_d.update({'pmids':new_pmids}) 
            else:
                # this project is new, no need to subset the pmids
                pass

            if idx != None and start == None:
                print(f"You can't have your parameter idx not equal to None and your start = None, changing your idx to None")
                idx = None

            if start != None:
                try:
                    master_df = pickle.load(open(f'./output/master_df/master_df.p','rb'))
                    if update:
                        master_df = master_df[master_df.pmid.isin(new_pmids)]
                except:
                    print(f"You don't have any previous master_df we changed your parameters start and idx to None")
                    start = None
                    idx = None
            
            if start == None:
                # make a medline records text file for a given list of pmids
                medline_file_name = pmids_to_medline_file(results_d['date'], results_d['pmids'], email, api_key)
                # parse the medline file and create a master_df with unique indexes for each record
                master_df = pd.DataFrame(creation_master_df(medline_file_name))
                
                # standardise the empty values and ensure there are no duplicates of pmids or dois in our master_df
                master_df.fillna(value=np.nan, inplace=True)
                master_df = master_df.drop_duplicates(keep='first', ignore_index=False, subset=['doi', 'pmid'])
                
                # use the NCBI id converter API to get any missing IDs known to the NCBI databases
                master_df = ncbi_id_converter_batch(master_df, email)     
                
                # we now have a master_df of metadata. 
                # We can use the previous master_df index to exclude ones we have looked for already.
                
                
                
                
                
            
    ######################################### STILL to DO --- Using PMC and DOI list - HOW TO MAKE MASTER_DF ####################################

    # - identify list type = DONE
    # - send id converter api - get back list of identifiers  = DONE
    # - create list of available ids - PMID first then list of doi only
    # - send PMIDs to entrez as normal creating hex uids as we go
    # - for articles without a pmid, send DOIs to crossref and extract metadata from there creating UIDs as we go
    # - merge dataframes into a single metadata df
    # - will need to create the master_df first then add the doi only records after
    # - need to check that we can get a minimum dataset for metadata from both metadata sources.
    # - then the master_df will be complete - ready to go to normal full text retrieval options.
    # - need to consider if some articles only have PMCID (would this happen?) maybe we could parse metadata from PMC APIs - not done this yet would need a new function
    #######################################################################################################################################
    #
    #     # Now we'll write the function with the other type of list inputs.   
    #     elif type(input_function) == list:
    #         # check it is not an empty list
    #         if len(input_function)== 0:
    #             print('Your list is empty, please provide a python list of pmids, PMCids or DOIs')

    #         else:
    #             # make the output files if they dont already exist
    #             output_files ()
                    
    #             if input_function[0][:3] == 'PMC':
    #                 print('This looks like a list of PMCIDs')
                    
    #                 # now we need to run this through the id converter to get the corresponding PMIDs
    #                 id_dict = ncbi_id_converter_single_list(input_function, email)
                    
                    
    #                 from here we need to use the id_dict to get metadata and create a master_df
                    
                    
                    
                    
                    
                    
                    
    #             else:
    #                 dois, pmcids, pmid_doi = convert_DOI_PMID_PMCID(input_function, email, 'doi', True)
    #                 input_list = dois
            
    #             http, base_url = HTTP_setup(email, click_through_api_key, 'base')
    #             crossref_dict = Crossref_metadata(input_list, http, base_url)
    #             cr_df = key_fields(crossref_dict, dois, pmid_doi, pmcids, True)

    #             cr_df['tdm_links'] = cr_df['links'].apply(get_tdm_links)
    #             avail = sum([tdm != None for tdm in cr_df["tdm_links"]])
    #             print(f'We have {avail} articles with at least one full tdm link given\n = {np.round(avail/len(cr_df)*100,1)}%')
    #             cr_df.fillna(value=np.nan, inplace=True)
    #             master_df = cr_df    
            
            
        
    ####################### full text retrieval step ################################################################    
        
        
        
                # set up the crossref metadata http request ('base')
                http, base_url, headers = HTTP_setup(email, click_through_api_key, 'base')

                #create a new column to note whether there is a crossref metadata record available - default - 0 (NO).
                master_df['crossref'] = 0
                # we're going to start collection full text links now. so lets make a new column on the master_df to hold a dictionary of links
                master_df['full_text_links'] = [{'cr_tdm':[],'html_parse':[], 'pubmed_links':[]} for value in master_df.index]
                master_df['licenses'] = [{} for val in master_df.index]

                # work through the master_df for every available doi and query crossref for full text links
                master_df = get_crossref_links_and_licenses(master_df, http, base_url, headers)


                # now time to download some fulltexts, will need to create some new columns to show success or failure for each format and the actual parse dictionary

                master_df['pdf'] = 0
                master_df['xml'] = 0
                master_df['html'] = 0
                master_df['plain'] = 0
                master_df['pmc_tgz'] = 0
                master_df['xml_parse_d'] = [{} for index in master_df.index]
                master_df['html_parse_d'] = [{} for index in master_df.index]
                master_df['pdf_parse_d'] = [{} for index in master_df.index]
                master_df['plain_parse_d'] = [{} for index in master_df.index]

                pickle.dump(master_df, open(f'./output/master_df/master_df.p', 'wb'))
            else:
                pass    
            # set up the http session for crossref requests
            # http is the session object
            # base URL is empty in this case
            # headers include a clickthrough api key
            if start == None and idx == None:
                http, base_url, headers = HTTP_setup(email, click_through_api_key, 'crossref')
                # now use the http request set up to request for each of the master_df 
                master_df = retrieval(master_df, http, base_url, headers, 'crossref')
            elif start == 'crossref' and idx == None:
                http, base_url, headers = HTTP_setup(email, click_through_api_key, 'crossref')
                # now use the http request set up to request for each of the master_df 
                master_df = retrieval(master_df, http, base_url, headers, 'crossref')
                start = None
            elif start == 'crossref_only':
                try:
                    master_df2 = pickle.load(open(f'./output/master_df/master_df2.p', 'rb'))
                    if update:
                        master_df2 = master_df2[master_df2.pmid.isin(new_pmids)]
                except:
                    master_df2 = master_df
                if idx != None:
                    try:
                        divide_at = master_df2.index.get_loc(idx)
                    except:
                        print(f"The idx you enter was not found in the master_df, please enter a correct index")
                        exit()
                    if divide_at != 0:
                        finish = master_df2[divide_at:]
                        done = master_df2[:divide_at]
                        http, base_url, headers = HTTP_setup(email, click_through_api_key, 'crossref')
                        # now use the http request set up to request for each of the master_df 
                        finish = retrieval(finish, http, base_url, headers, 'crossref')
                        master_df2 = pd.concat([done, finish], axis=0, join='outer', ignore_index=False, copy=True)
                    else:
                        http, base_url, headers = HTTP_setup(email, click_through_api_key, 'crossref')
                        # now use the http request set up to request for each of the master_df 
                        master_df2 = retrieval(master_df2, http, base_url, headers, 'crossref')

                else:
                    http, base_url, headers = HTTP_setup(email, click_through_api_key, 'crossref')
                    # now use the http request set up to request for each of the master_df 
                    master_df2 = retrieval(master_df2, http, base_url, headers, 'crossref')
            elif start == 'crossref' and idx != None:
                try:
                    divide_at = master_df.index.get_loc(idx)
                except:
                    print(f"The idx you enter was not found in the master_df, please enter a correct index")
                    exit()
                if divide_at != 0:
                    finish = master_df[divide_at:]
                    done = master_df[:divide_at]
                    http, base_url, headers = HTTP_setup(email, click_through_api_key, 'crossref')
                    # now use the http request set up to request for each of the master_df 
                    finish = retrieval(finish, http, base_url, headers, 'crossref')
                    master_df = pd.concat([done, finish], axis=0, join='outer', ignore_index=False, copy=True)
                    start = None
                    idx = None
                else:
                    http, base_url, headers = HTTP_setup(email, click_through_api_key, 'crossref')
                    # now use the http request set up to request for each of the master_df 
                    master_df = retrieval(master_df, http, base_url, headers, 'crossref')
                    start = None
                    idx = None
            else:
                pass

            if start == None and idx == None:
                http, base_url, headers = HTTP_setup(email, click_through_api_key, 'doiorg')
                # now use the http request set up to request for each of the master_df 
                master_df = retrieval(master_df, http, base_url, headers, 'doiorg')
            elif start == 'doiorg' and idx == None:
                http, base_url, headers = HTTP_setup(email, click_through_api_key, 'doiorg')
                # now use the http request set up to request for each of the master_df 
                master_df = retrieval(master_df, http, base_url, headers, 'doiorg')
                start = None
            elif start == 'doiorg_only':
                try:
                    master_df2 = pickle.load(open(f'./output/master_df/master_df2.p', 'rb'))
                    if update:
                        master_df2 = master_df2[master_df2.pmid.isin(new_pmids)]
                except:
                    master_df2 = master_df
                if idx != None:
                    try:
                        divide_at = master_df2.index.get_loc(idx)
                    except:
                        print(f"The idx you enter was not found in the master_df, please enter a correct index")
                        exit()
                    if divide_at != 0:
                        finish = master_df2[divide_at:]
                        done = master_df2[:divide_at]
                        http, base_url, headers = HTTP_setup(email, click_through_api_key, 'doiorg')
                        # now use the http request set up to request for each of the master_df 
                        finish = retrieval(finish, http, base_url, headers, 'doiorg')
                        master_df2 = pd.concat([done, finish], axis=0, join='outer', ignore_index=False, copy=True)
                    else:
                        http, base_url, headers = HTTP_setup(email, click_through_api_key, 'doiorg')
                        # now use the http request set up to request for each of the master_df 
                        master_df2 = retrieval(master_df2, http, base_url, headers, 'doiorg')

                else:
                    http, base_url, headers = HTTP_setup(email, click_through_api_key, 'doiorg')
                    # now use the http request set up to request for each of the master_df 
                    master_df2 = retrieval(master_df2, http, base_url, headers, 'doiorg')
            elif start == 'doiorg' and idx != None:
                try:
                    divide_at = master_df.index.get_loc(idx)
                except:
                    print(f"The idx you enter was not found in the master_df, please enter a correct index")
                    exit()
                if divide_at != 0:
                    finish = master_df[divide_at:]
                    done = master_df[:divide_at]
                    http, base_url, headers = HTTP_setup(email, click_through_api_key, 'doiorg')
                    # now use the http request set up to request for each of the master_df 
                    finish = retrieval(finish, http, base_url, headers, 'doiorg')
                    master_df = pd.concat([done, finish], axis=0, join='outer', ignore_index=False, copy=True)
                    start = None
                    idx = None
                else:
                    http, base_url, headers = HTTP_setup(email, click_through_api_key, 'doiorg')
                    # now use the http request set up to request for each of the master_df 
                    master_df = retrieval(master_df, http, base_url, headers, 'doiorg')
                    start = None
                    idx = None
            else:
                pass

            if start == None and idx == None:
                http, base_url, headers = HTTP_setup(email, click_through_api_key, 'epmcxml')
                # now use the http request set up to request for each of the master_df 
                master_df = retrieval(master_df, http, base_url, headers, 'epmcxml')
            elif start == 'epmcxml' and idx == None:
                http, base_url, headers = HTTP_setup(email, click_through_api_key, 'epmcxml')
                # now use the http request set up to request for each of the master_df 
                master_df = retrieval(master_df, http, base_url, headers, 'epmcxml')
                start = None
            elif start == 'epmcxml_only':
                try:
                    master_df2 = pickle.load(open(f'./output/master_df/master_df2.p', 'rb'))
                    if update:
                        master_df2 = master_df2[master_df2.pmid.isin(new_pmids)]
                except:
                    master_df2 = master_df
                if idx != None:
                    try:
                        divide_at = master_df2.index.get_loc(idx)
                    except:
                        print(f"The idx you enter was not found in the master_df, please enter a correct index")
                        exit()
                    if divide_at != 0:
                        finish = master_df2[divide_at:]
                        done = master_df2[:divide_at]
                        http, base_url, headers = HTTP_setup(email, click_through_api_key, 'epmcxml')
                        # now use the http request set up to request for each of the master_df 
                        finish = retrieval(finish, http, base_url, headers, 'epmcxml')
                        master_df2 = pd.concat([done, finish], axis=0, join='outer', ignore_index=False, copy=True)
                    else:
                        http, base_url, headers = HTTP_setup(email, click_through_api_key, 'epmcxml')
                        # now use the http request set up to request for each of the master_df 
                        master_df2 = retrieval(master_df2, http, base_url, headers, 'epmcxml')

                else:
                    http, base_url, headers = HTTP_setup(email, click_through_api_key, 'epmcxml')
                    # now use the http request set up to request for each of the master_df 
                    master_df2 = retrieval(master_df2, http, base_url, headers, 'epmcxml')
            elif start == 'epmcxml' and idx != None:
                try:
                    divide_at = master_df.index.get_loc(idx)
                except:
                    print(f"The idx you enter was not found in the master_df, please enter a correct index")
                    exit()
                if divide_at != 0:
                    finish = master_df[divide_at:]
                    done = master_df[:divide_at]
                    http, base_url, headers = HTTP_setup(email, click_through_api_key, 'epmcxml')
                    # now use the http request set up to request for each of the master_df 
                    finish = retrieval(finish, http, base_url, headers, 'epmcxml')
                    master_df = pd.concat([done, finish], axis=0, join='outer', ignore_index=False, copy=True)
                    start = None
                    idx = None
                else:
                    http, base_url, headers = HTTP_setup(email, click_through_api_key, 'epmcxml')
                    # now use the http request set up to request for each of the master_df 
                    master_df = retrieval(master_df, http, base_url, headers, 'epmcxml')
                    start = None
                    idx = None
            else:
                pass  

            if start == None and idx == None:
                http, base_url, headers = HTTP_setup(email, click_through_api_key, 'pmcxmls')
                # now use the http request set up to request for each of the master_df 
                master_df = retrieval(master_df, http, base_url, headers, 'pmcxmls')
            elif start == 'pmcxmls' and idx == None:
                http, base_url, headers = HTTP_setup(email, click_through_api_key, 'pmcxmls')
                # now use the http request set up to request for each of the master_df 
                master_df = retrieval(master_df, http, base_url, headers, 'pmcxmls')
                start = None
            elif start == 'pmcxmls_only':
                try:
                    master_df2 = pickle.load(open(f'./output/master_df/master_df2.p', 'rb'))
                    if update:
                        master_df2 = master_df2[master_df2.pmid.isin(new_pmids)]
                except:
                    master_df2 = master_df
                if idx != None:
                    try:
                        divide_at = master_df2.index.get_loc(idx)
                    except:
                        print(f"The idx you enter was not found in the master_df, please enter a correct index")
                        exit()
                    if divide_at != 0:
                        finish = master_df2[divide_at:]
                        done = master_df2[:divide_at]
                        http, base_url, headers = HTTP_setup(email, click_through_api_key, 'pmcxmls')
                        # now use the http request set up to request for each of the master_df 
                        finish = retrieval(finish, http, base_url, headers, 'pmcxmls')
                        master_df2 = pd.concat([done, finish], axis=0, join='outer', ignore_index=False, copy=True)
                    else:
                        http, base_url, headers = HTTP_setup(email, click_through_api_key, 'pmcxmls')
                        # now use the http request set up to request for each of the master_df 
                        master_df2 = retrieval(master_df2, http, base_url, headers, 'pmcxmls')

                else:
                    http, base_url, headers = HTTP_setup(email, click_through_api_key, 'pmcxmls')
                    # now use the http request set up to request for each of the master_df 
                    master_df2 = retrieval(master_df2, http, base_url, headers, 'pmcxmls')
            elif start == 'pmcxmls' and idx != None:
                try:
                    divide_at = master_df.index.get_loc(idx)
                except:
                    print(f"The idx you enter was not found in the master_df, please enter a correct index")
                    exit()
                if divide_at != 0:
                    finish = master_df[divide_at:]
                    done = master_df[:divide_at]
                    http, base_url, headers = HTTP_setup(email, click_through_api_key, 'pmcxmls')
                    # now use the http request set up to request for each of the master_df 
                    finish = retrieval(finish, http, base_url, headers, 'pmcxmls')
                    master_df = pd.concat([done, finish], axis=0, join='outer', ignore_index=False, copy=True)
                    start = None
                    idx = None
                else:
                    http, base_url, headers = HTTP_setup(email, click_through_api_key, 'pmcxmls')
                    # now use the http request set up to request for each of the master_df 
                    master_df = retrieval(master_df, http, base_url, headers, 'pmcxmls')
                    start = None
                    idx = None
            else:
                pass
            
            if start == None and idx == None:
                http, base_url, headers = HTTP_setup(email, click_through_api_key, 'pmctgz')
                # now use the http request set up to request for each of the master_df 
                master_df = retrieval(master_df, http, base_url, headers, 'pmctgz')
            elif start == 'pmctgz' and idx == None:
                http, base_url, headers = HTTP_setup(email, click_through_api_key, 'pmctgz')
                # now use the http request set up to request for each of the master_df 
                master_df = retrieval(master_df, http, base_url, headers, 'pmctgz')
                start = None
            elif start == 'pmctgz_only':
                try:
                    master_df2 = pickle.load(open(f'./output/master_df/master_df2.p', 'rb'))
                    if update:
                        master_df2 = master_df2[master_df2.pmid.isin(new_pmids)]
                except:
                    master_df2 = master_df
                if idx != None:
                    try:
                        divide_at = master_df2.index.get_loc(idx)
                    except:
                        print(f"The idx you enter was not found in the master_df, please enter a correct index")
                        exit()
                    if divide_at != 0:
                        finish = master_df2[divide_at:]
                        done = master_df2[:divide_at]
                        http, base_url, headers = HTTP_setup(email, click_through_api_key, 'pmctgz')
                        # now use the http request set up to request for each of the master_df 
                        finish = retrieval(finish, http, base_url, headers, 'pmctgz')
                        master_df2 = pd.concat([done, finish], axis=0, join='outer', ignore_index=False, copy=True)
                    else:
                        http, base_url, headers = HTTP_setup(email, click_through_api_key, 'pmctgz')
                        # now use the http request set up to request for each of the master_df 
                        master_df2 = retrieval(master_df2, http, base_url, headers, 'pmctgz')

                else:
                    http, base_url, headers = HTTP_setup(email, click_through_api_key, 'pmctgz')
                    # now use the http request set up to request for each of the master_df 
                    master_df2 = retrieval(master_df2, http, base_url, headers, 'pmctgz')
            elif start == 'pmctgz' and idx != None:
                try:
                    divide_at = master_df.index.get_loc(idx)
                except:
                    print(f"The idx you enter was not found in the master_df, please enter a correct index")
                    exit()
                if divide_at != 0:
                    finish = master_df[divide_at:]
                    done = master_df[:divide_at]
                    http, base_url, headers = HTTP_setup(email, click_through_api_key, 'pmctgz')
                    # now use the http request set up to request for each of the master_df 
                    finish = retrieval(finish, http, base_url, headers, 'pmctgz')
                    master_df = pd.concat([done, finish], axis=0, join='outer', ignore_index=False, copy=True)
                    start = None
                    idx = None
                else:
                    http, base_url, headers = HTTP_setup(email, click_through_api_key, 'pmctgz')
                    # now use the http request set up to request for each of the master_df 
                    master_df = retrieval(master_df, http, base_url, headers, 'pmctgz')
                    start = None
                    idx = None
            else:
                pass

            if start == None and idx == None:
                http, base_url, headers = HTTP_setup(email, click_through_api_key, 'pmcpdfs')
                # now use the http request set up to request for each of the master_df 
                master_df = retrieval(master_df, http, base_url, '', 'pmcpdfs')
            elif start == 'pmcpdfs' and idx == None:
                http, base_url, headers = HTTP_setup(email, click_through_api_key, 'pmcpdfs')
                # now use the http request set up to request for each of the master_df 
                master_df = retrieval(master_df, http, base_url, '', 'pmcpdfs')
                start = None
            elif start == 'pmcpdfs_only':
                try:
                    master_df2 = pickle.load(open(f'./output/master_df/master_df2.p', 'rb'))
                    if update:
                        master_df2 = master_df2[master_df2.pmid.isin(new_pmids)]
                except:
                    master_df2 = master_df
                if idx != None:
                    try:
                        divide_at = master_df2.index.get_loc(idx)
                    except:
                        print(f"The idx you enter was not found in the master_df, please enter a correct index")
                        exit()
                    if divide_at != 0:
                        finish = master_df2[divide_at:]
                        done = master_df2[:divide_at]
                        http, base_url, headers = HTTP_setup(email, click_through_api_key, 'pmcpdfs')
                        # now use the http request set up to request for each of the master_df 
                        finish = retrieval(finish, http, base_url, '', 'pmcpdfs')
                        master_df2 = pd.concat([done, finish], axis=0, join='outer', ignore_index=False, copy=True)
                    else:
                        http, base_url, headers = HTTP_setup(email, click_through_api_key, 'pmcpdfs')
                        # now use the http request set up to request for each of the master_df 
                        master_df2 = retrieval(master_df2, http, base_url, '', 'pmcpdfs')

                else:
                    http, base_url, headers = HTTP_setup(email, click_through_api_key, 'pmcpdfs')
                    # now use the http request set up to request for each of the master_df 
                    master_df2 = retrieval(master_df2, http, base_url, '', 'pmcpdfs')
            elif start == 'pmcpdfs' and idx != None:
                try:
                    divide_at = master_df.index.get_loc(idx)
                except:
                    print(f"The idx you enter was not found in the master_df, please enter a correct index")
                    exit()
                if divide_at != 0:
                    finish = master_df[divide_at:]
                    done = master_df[:divide_at]
                    http, base_url, headers = HTTP_setup(email, click_through_api_key, 'pmcpdfs')
                    # now use the http request set up to request for each of the master_df 
                    finish = retrieval(finish, http, base_url, '', 'pmcpdfs')
                    master_df = pd.concat([done, finish], axis=0, join='outer', ignore_index=False, copy=True)
                    start = None
                    idx = None
                else:
                    http, base_url, headers = HTTP_setup(email, click_through_api_key, 'pmcpdfs')
                    # now use the http request set up to request for each of the master_df 
                    master_df = retrieval(master_df, http, base_url, '', 'pmcpdfs')
                    start = None
                    idx = None
            else:
                pass

            if start == None and idx == None:
                http, base_url, headers = HTTP_setup(email, click_through_api_key, 'pubmed')
                # now use the http request set up to request for each of the master_df 
                master_df = retrieval(master_df, http, base_url, headers, 'pubmed')
            elif start == 'pubmed' and idx == None:
                http, base_url, headers = HTTP_setup(email, click_through_api_key, 'pubmed')
                # now use the http request set up to request for each of the master_df 
                master_df = retrieval(master_df, http, base_url, headers, 'pubmed')
                start = None
            elif start == 'pubmed_only':
                try:
                    master_df2 = pickle.load(open(f'./output/master_df/master_df2.p', 'rb'))
                    if update:
                        master_df2 = master_df2[master_df2.pmid.isin(new_pmids)]
                except:
                    master_df2 = master_df
                if idx != None:
                    try:
                        divide_at = master_df2.index.get_loc(idx)
                    except:
                        print(f"The idx you enter was not found in the master_df, please enter a correct index")
                        exit()
                    if divide_at != 0:
                        finish = master_df2[divide_at:]
                        done = master_df2[:divide_at]
                        http, base_url, headers = HTTP_setup(email, click_through_api_key, 'pubmed')
                        # now use the http request set up to request for each of the master_df 
                        finish = retrieval(finish, http, base_url, headers, 'pubmed')
                        master_df2 = pd.concat([done, finish], axis=0, join='outer', ignore_index=False, copy=True)
                    else:
                        http, base_url, headers = HTTP_setup(email, click_through_api_key, 'pubmed')
                        # now use the http request set up to request for each of the master_df 
                        master_df2 = retrieval(master_df2, http, base_url, headers, 'pubmed')

                else:
                    http, base_url, headers = HTTP_setup(email, click_through_api_key, 'pubmed')
                    # now use the http request set up to request for each of the master_df 
                    master_df2 = retrieval(master_df2, http, base_url, headers, 'pubmed')
            elif start == 'pubmed' and idx != None:
                try:
                    divide_at = master_df.index.get_loc(idx)
                except:
                    print(f"The idx you enter was not found in the master_df, please enter a correct index")
                    exit()
                if divide_at != 0:
                    finish = master_df[divide_at:]
                    done = master_df[:divide_at]
                    http, base_url, headers = HTTP_setup(email, click_through_api_key, 'pubmed')
                    # now use the http request set up to request for each of the master_df 
                    finish = retrieval(finish, http, base_url, headers, 'pubmed')
                    master_df = pd.concat([done, finish], axis=0, join='outer', ignore_index=False, copy=True)
                    start = None
                    idx = None
                else:
                    http, base_url, headers = HTTP_setup(email, click_through_api_key, 'pubmed')
                    # now use the http request set up to request for each of the master_df 
                    master_df = retrieval(master_df, http, base_url, headers, 'pubmed')
                    start = None
                    idx = None
            else:
                pass

            if start == None:
                master_df = working_text(master_df)
                master_df = correct_date_format(master_df)
                eval_master_df = master_df[['pdf', 'html', 'plain', 'xml', 'working_text']]
                pickle.dump(master_df, open(f'./output/master_df/master_df.p', 'wb'))
            else:
                eval_master_df = master_df[['pdf', 'html', 'plain', 'xml', 'working_text']]

            if start == None and idx == None:
                master_df2 = parse_link_retrieval(master_df, email, click_through_api_key)
            elif start == 'master2' and idx == None:
                master_df2 = parse_link_retrieval(master_df, email, click_through_api_key)
                start = None
            elif start == 'master2_only':
                try:
                    master_df2 = pickle.load(open(f'./output/master_df/master_df2.p', 'rb'))
                    if update:
                        master_df2 = master_df2[master_df2.pmid.isin(new_pmids)]
                except:
                    master_df2 = master_df
                if idx != None:
                    try:
                        divide_at = master_df2.index.get_loc(idx)
                    except:
                        print(f"The idx you enter was not found in the master_df, please enter a correct index")
                        exit()
                    if divide_at != 0:
                        finish = master_df2[divide_at:]
                        done = master_df2[:divide_at]                       
                        finish = parse_link_retrieval(finish, email, click_through_api_key)
                        master_df2 = pd.concat([done, finish], axis=0, join='outer', ignore_index=False, copy=True)
                    else:
                        master_df2 = parse_link_retrieval(master_df2, email, click_through_api_key)

                else:
                    master_df2 = parse_link_retrieval(master_df2, email, click_through_api_key)
            elif start == 'master2' and idx != None:
                try:
                    divide_at = master_df.index.get_loc(idx)
                except:
                    print(f"The idx you enter was not found in the master_df, please enter a correct index")
                    exit()
                if divide_at != 0:
                    finish = master_df[divide_at:]
                    done = master_df[:divide_at]
                    finish = parse_link_retrieval(finish, email, click_through_api_key)
                    master_df2 = pd.concat([done, finish], axis=0, join='outer', ignore_index=False, copy=True)
                    start = None
                    idx = None
                else:
                    master_df2 = parse_link_retrieval(master_df, email, click_through_api_key)
                    start = None
                    idx = None
            else:
                pass

            master_df2 = working_text(master_df2)
            master_df2 = correct_date_format(master_df2)
            
            # finally if this is an update then we need to concatenate the original df and the new working df
            if update:
                original_df = original_df.drop(drop_lines)
                master_df2 = pd.concat([original_df, master_df2], axis=0, join='outer', ignore_index=False, copy=True)
            else:
                # no merge to perform
                pass
            
            clear()
            if start == None:
                print(f'Result for master_df : ') 
                evaluation(eval_master_df)
                print('\n')
            print(f'Result for master_df2 : ')
            evaluation(master_df2)
            
            pickle.dump(master_df2, open(f'./output/master_df/master_df2.p', 'wb'))        
    else:
        print('Your input is not handle by the function please enter Pubmed search terms or a list of single type(dois, pmids, pmcids), without header')