import urllib.request as request
import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, HTTPError, Timeout
from urllib3.util.retry import Retry

def HTTP_setup_elsevier(mail): 
    
    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
        'Accept-Language': "en,en-US;q=0,5",
        'Accept': "text/html,application/pdf,application/xhtml+xml,application/xml,text/plain,text/xml",
        'mailto':mail,
        'Accept-Encoding': 'gzip, deflate, compress',
        'Accept-Charset': 'ascii, iso-8859-1;q=0.5, *;q=0.1'}
    base_url = ""
        
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
 
    return http, headers 