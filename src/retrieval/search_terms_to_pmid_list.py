from Bio import Entrez, Medline
import datetime
import pickle

# we can use the search terms provided to query pubmed using entrez esearch. 
# This will provide us with a list of pmids to retrieve in medline format
# this function takes the search terms in the query string and returns a dictionary 
# the dict keys are: the date of serach, the query string used, the total count returned and the list of pmids 
def search_terms_to_pmid_list(query_string, email, api_key):
    # set the entrez variables which are set up in advance for each group/project
    Entrez.email = email
    Entrez.tool = "genepopi_search_developer"
    Entrez.api_key = api_key    
    # get todays date 
    date = datetime.datetime.today()
    date = f'{date.year}_{date.month}_{date.day}_{date.hour}_{date.minute}'
    # send the query string to entrez esearch with the retmax at 90,000
    # note if the number of returned records is > retmax we will need to iterate over the search results using a moving start and end point.
    search_results = Entrez.read(Entrez.esearch(db="pubmed", term = query_string, retmax=90000))
    # We can then save the total count returned and pmid list to new variables
    t_count = int(search_results['Count'])
    pmids = list(search_results['IdList'])
    
    # construct the output dict
    results_d = {'date':date, 'search_term':query_string, 'total_count':t_count, 'pmids':pmids}
    
    # save the output dictionary for our records of what terms used and number of records returned for a given date.
    pickle.dump(results_d, open(f'./output/esearch_results/{date}.p', 'wb'))

    return results_d