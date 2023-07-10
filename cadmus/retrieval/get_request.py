import urllib.request as request
import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, HTTPError, Timeout
from urllib3.util import Retry
from urllib3.exceptions import NewConnectionError
import time

from cadmus.retrieval.HTTP_setup_elsevier import HTTP_setup_elsevier

def get_request(input_id, http, base_url, headers, stage, elsevier_api_key, mail = ''):
    
     
    # for text retrieval its best to clear cookies before each request
    http.cookies.clear()
    
    # The response dictionary (r_d) will hold the output from our request, succeed or fail
    r_d = {}
    exception = None
    attempt = 1
    need_to_back_off = False
    is_elsevier = False
    while attempt <3:
        # we're going to set up a try except system so that we deal with the most common errors
        try:
            # send the request to the different APIs website
            if stage == 'base' or stage == 'doiorg' or stage == 'pubmed':
                base_url = f'{base_url}{input_id}'
                r = http.get(url = f'{base_url}', headers=headers, timeout = (20,120))
            elif stage == 'crossref':
                if 'api' in base_url and 'elsevier' in base_url:
                    if elsevier_api_key != None:
                        http, headers = HTTP_setup_elsevier(mail)
                        previous = base_url
                        base_url = f'{base_url.split("?")[0]}?APIKey={elsevier_api_key}&{base_url.split("?")[1]}'
                        r = http.get(f'{base_url}', headers=headers, timeout = (20,120))
                        is_elsevier = True
                        base_url = previous
                        time.sleep(0.3)
                    else:
                        r = http.get(f'{base_url}', headers=headers, timeout = (20,120))
                else:
                    r = http.get(f'{base_url}', headers=headers, timeout = (20,120))
            elif stage == 'epmcxml':
                base_url = f'{base_url}{input_id}/fullTextXML'
                r = http.get(f'{base_url}', headers=headers, timeout = (20,120))
            elif stage == 'epmcsupp':
                base_url = f'{base_url}{input_id}/supplementaryFiles'
                r = http.get(f'{base_url}', headers=headers, timeout = (20,120), stream=True)
            elif stage == 'pmcxmls':
                base_url = f'{base_url}{input_id}&metadataPrefix=pmc'
                r = http.get(f'{base_url}', headers=headers, timeout = (20,120))
            elif stage == 'pmcpdfs' or stage == 'pmctgz':
                base_url = f'{base_url}{input_id}&format='
                r = http.get(f'{base_url}', headers=headers, timeout = (20,120), stream=True)
            else:
                pass
            
            # check for 200 response and raise exception if not so.
            if r.status_code != 200:
                print(f'Error {r.status_code} for {base_url}')
        
        #now we have a set of multiple exceptions that might occur
        except HTTPError as error:
            print(f"HTTP error occurred:\n{error}")
            if r.status_code == 429:
                need_to_back_off = True
            exception = error
            r = None
            attempt = 3
        except NewConnectionError as nce:
            print(f'New connection error occurred \n{nce}')
            exception = nce
            attempt = 3
            r = None
        except Timeout:
            print('Request timed out')
            exception = 'timeout'
            attempt = 3
            r= None
        except ConnectionError as ce:
            print(f'Max Retries error:\n{ce}')
            exception = ce
            attempt = 3
            r= None
        except Exception as err:
            print(f'Another sort of error occured: \n{err}')
            exception = err
            attempt = 3
            r= None
        else:
            # No Exceptions Occured
            # set the output variables from the response object
            exception = None
            status_code = r.status_code
            headers = r.headers
            text = r.text
            r_url = r.url
            content = r.content
            attempt = 3

        finally:
            
            if (r == None) or (r.status_code != 200):
                
                # set the default response_dict values before we parse
                status_code = None
                headers = None
                text = None
                r_url = None
                content = None
            else:
                pass
            
            if is_elsevier == False:
                # build the output dictionary and return
                r_d.update({'status_code':status_code,
                            'headers':headers,
                            'content':content,
                            'text':text,
                            'url':r_url,
                            'error':exception})
            else:
                r_d.update({'status_code':status_code,
                            'headers':headers,
                            'content':content,
                            'text':text,
                            'url':base_url,
                            'error':exception})
        
        # now we close the response objects to keep the number of open files to a minimum
        if r != None:
            r.close()
    
    if need_to_back_off == True:
        exit()
            
    return r_d, r