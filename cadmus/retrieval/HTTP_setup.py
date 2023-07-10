import urllib.request as request
import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, HTTPError, Timeout
from urllib3.util.retry import Retry

def HTTP_setup(email, click_through_api_key, wiley_api_key, stage): 
    
    #each stage modifies the base url and parameters for that part of the process whilst the general set up and exceptions remain the same
    # set the headers as a mailto
    if stage == 'base':
        # base stage is about the basic crossref metadata requests
        headers = {'mailto':email}
        base_url = "https://api.crossref.org/works/"
    
    elif stage == 'crossref':
        # crossref is used for downloading full texts from links provided by crossref.
        # this stage requires a clickthrough API key to be provided and there is no base URL
        if wiley_api_key != None:
            headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
                'Accept-Language': "en,en-US;q=0,5",
                'Accept': "text/html,application/pdf,application/xhtml+xml,application/xml,text/plain,text/xml",
                'mailto':email,
                'Wiley-TDM-Client-Token': wiley_api_key,
                'CR-Clickthrough-Client-Token': click_through_api_key,
                'Accept-Encoding': 'gzip, deflate, compress',
                'Accept-Charset': 'ascii, iso-8859-1;q=0.5, *;q=0.1'}
        else:
            headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
                'Accept-Language': "en,en-US;q=0,5",
                'Accept': "text/html,application/pdf,application/xhtml+xml,application/xml,text/plain,text/xml",
                'mailto':email,
                'CR-Clickthrough-Client-Token': click_through_api_key,
                'Accept-Encoding': 'gzip, deflate, compress',
                'Accept-Charset': 'ascii, iso-8859-1;q=0.5, *;q=0.1'}
        base_url = ""
    else:
        # all other stages are generic request headers for full text or webpages requests
        headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
               'Accept-Language': "en,en-US;q=0,5",
               'Accept': "text/html,application/pdf,application/xhtml+xml,application/xml,text/plain,text/xml",
               'mailto':email,
               'Accept-Encoding': 'gzip, deflate, compress',
               'Accept-Charset': 'utf-8, iso-8859-1;q=0.5, *;q=0.1'}
    
    # now set the base urls for the other stages 
    if stage == 'epmcxml':
        base_url = 'https://www.ebi.ac.uk/europepmc/webservices/rest/'
    elif stage == 'epmcsupp':
        base_url = 'https://www.ebi.ac.uk/europepmc/webservices/rest/'
    elif stage == 'pmcxmls':
        base_url = 'https://www.ncbi.nlm.nih.gov/pmc/oai/oai.cgi?verb=GetRecord&identifier=oai:pubmedcentral.nih.gov:'
    elif stage == 'pmcpdfs' or stage == 'pmctgz':
        base_url ='https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id='
    elif stage == 'doiorg':
        base_url = "https://doi.org/"
    elif stage == 'pubmed':
        base_url = "https://www.ncbi.nlm.nih.gov/pubmed/"
    else:
        pass
        
    # initiate a requests.session so we can send multiple requests with the same parameters and cookies persist
    http = requests.Session()
    
    # set the base url, in this case it is the works url for the crossref api
    http.headers.update(headers)

    # set up a retry strategy
    retry_strategy = Retry(
            total=3,
            status_forcelist = [429, 500, 502, 503, 504],
            method_whitelist = ["GET"],
            backoff_factor = 1
        )
    
    # add the retry strategy to the adapter for a session
    adapter = HTTPAdapter(max_retries=retry_strategy)
    
    # mount these settings to our session
    http.mount(base_url, adapter)
    
 
    return http, base_url, headers 