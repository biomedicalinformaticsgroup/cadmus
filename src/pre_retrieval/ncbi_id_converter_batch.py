import urllib.request as request
import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, HTTPError, Timeout
from urllib3.util.retry import Retry
import json

def ncbi_id_converter_batch(master_df, email):

    # we only need one type of id per article to check the NCBI API
    # the pmid should be the first choice rather than doi
    
    # we are going to be resetting the index several times so lets create a new column to hold the current index
    master_df['index'] = master_df.index 
    
    
    # get the pmid_list
    pmid_list = []
    doi_list = []
    pmcid_list = []
    
    # lets get one uid for each record 
    for index, row in master_df.iterrows():
        if type(row['pmid']) == str:
            pmid_list.append(row['pmid'])
        elif type(row['doi']) == str:
            doi_list.append(row['doi'])
        elif type(row['pmcid']) == str:
            pmcid_list.append(row['pmcid'])
            
    print(f'Now running the NCBI converter.\nWe have {len(pmid_list)} PMIDs, {len(doi_list)} DOIs and {len(pmcid_list)} PMCIDs to search for')
    
    if len(pmid_list) == 0 and len(doi_list) == 0 and len(pmcid_list) == 0:
        print('The previous step failed, please wait a few minutes and try again with the same command')
        exit()

    base_url = 'https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/'
    email = email
    headers= {'Accept':'application/json'}

    for input_list in ['pmid_list', 'doi_list', 'pmcid_list']:
        
        # set the appropriate column as the index
        col = str(input_list).replace('_list', '')
        print(f'Working on the {col} List...')
        master_df.set_index(col, drop=False, inplace = True)
        
        # each process starts at record 0 and retrieves in batches up to a max of 200 per batch.
        start = 0
        batch_size = 200

        # set the total number to check
        total = len(input_list)
       
        # create a while loop to run the batches until the end of the list
        while start < total:
            batch_size = min(batch_size, (total - start))
            end = start + batch_size
            
            # set the parameters for the api
            params = {'ids':str(','.join(input_list[start:end])),
                     'tool':"genepopi_search_developer",
                     'versions':'no',
                     'format':'json',
                     'email':email}
            
            
            attempt = 1
            while attempt <3:
                try:
                    # send the request using the batch list of pmids
                    r = requests.get(base_url, headers=headers,params=params)
                    # ensure the status response is ok e.g. 2**
                    r.raise_for_status()
                    attempt = 3 
                    # convert json to dictionary
                    response =json.loads(r.text)

                    # write the dictionaries to the holding list
                    records = response['records']
                    
                    # now we have 200 records to loop through.
                    # we can use the new index to fill in the missing values for the other ids.
                    # check the record for a error message (when the id is not known)
                    for record in records:
                        status = record.get('status')
                        # if there is no error message we can try parse out the extra ids
                        if status != 'error':
                            # get the index to update the values
                            i = record.get(col)
                            # loop through each key value pair and insert the value if missing
                            for key, value in record.items():
                                if type(master_df.at[i,key]) == float:
                                    master_df.at[i,key] = value
                                 
                        
                        
                except:
                    attempt+=1
                    pass
            # iterate the batch size for our request    
            start += batch_size
    # now lets reset the master_df index back to the original index
    master_df.set_index('index', drop =True, inplace = True)

    return master_df