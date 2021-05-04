from cadmus.src.retrieval import get_request
from cadmus.src.parsing import xml_response_to_parse_d
from cadmus.src.parsing import doctype
from cadmus.src.evaluation import evaluation_funct
from cadmus.src.retrieval import complete_html_link_parser
from cadmus.src.parsing.html_response_to_parse_d import html_response_to_parse_d
from cadmus.src.parsing import pdf_file_to_parse_d
from cadmus.src.parsing import plain_file_to_parse_d
from cadmus.src.parsing import tgz_unpacking
from cadmus.src.retrieval import pubmed_linkout_parse
from cadmus.src.retrieval import clear
from cadmus.src.retrieval import timeout
import bs4
from bs4 import BeautifulSoup
import pickle
import urllib.request as request
from contextlib import closing
import shutil
import wget
import time
from time import sleep
import warnings
warnings.filterwarnings("ignore")
from multiprocessing import Process

def retrieval(retrieval_df, http, base_url, headers, stage):
    # the input will be the master_df and each process will be subset so that the required input is always available (doi or pmid or pmcid)
    counter = 0
    for index, row in retrieval_df.iterrows():
        if counter == 0:
            clear()
            print(f'In case of faillure please put the parameters start="{stage}" (or "{stage}_only" if in only mode) and idx="{index}"') 
            saved_stage = stage
            saved_index = index   
            print('\n')   
        counter += 1
        if stage == 'crossref':
            print('Downloading Crossref TDM links now...')
            print(f'tdm full link {counter} of {len(retrieval_df)}') 
            
        elif stage == 'epmcxml' or stage == 'epmcsupp' or stage == 'pmcxmls' or stage == 'pmcpdfs' or stage == 'pmctgz':
            if retrieval_df.pmcid.loc[index] == retrieval_df.pmcid.loc[index]:
                pmcid = row['pmcid']
                print(f'Looking for {pmcid} which is record {counter} of {len(retrieval_df)}')
                if stage == 'pmcxmls' or stage == 'pmcpdfs':
                    pmcid = pmcid.replace('PMC', '')
                else:
                    pass
            else:
                pass
        
        elif stage == 'doiorg':
            if retrieval_df.doi.loc[index] == retrieval_df.doi.loc[index]:
                doi = row['doi']
                print(f'DOI {counter} of {len(retrieval_df)}')
            else:
                pass
        
        elif stage == 'pubmed':
            if retrieval_df.pmid.loc[index] == retrieval_df.pmid.loc[index]:
                pmid = row['pmid']
                print(f'working on pmid:{pmid}, record {counter} of {len(retrieval_df)}')
            else:
                pass
        
        else:
            pass
            
        if stage == 'crossref':
            links = row['full_text_links'].get('cr_tdm')
            if links:                               
                for link in links: 
                    if ('.pdf' in link and retrieval_df.pdf.loc[index] == 1) or  ('.xml' in link and retrieval_df.xml.loc[index] == 1) or ('plain' in link and retrieval_df.plain.loc[index] == 1):  
                        pass
                    else:           
                        print(f'trying to download from: \n{link}')
                        try:
                            response_d, response = get_request('', http, link, headers, 'crossref')
                        except:
                            pass

                        # we don't want to get the IP address blocked by the publisher so need to check responses to each request
                        # some publishers may not use the correct headers and might be missed
                        # in which case we need to look out for any "too many requests" response
                        if response_d['status_code'] == 429:
                            print('"Too many requests error [429]" received')
                            print('Risk of IP address block: stopping script')
                            print(response_d['text'])
                            exit()

                        elif response_d['status_code'] == 200:   
                            print('Request ok')

                            # This section looks for limit header from publisher API as set out on Crossref docs
                            # check to see if there has been a limit set
                            rate_limit = headers.get('CR-TDM-Rate-Limit')
                            if rate_limit:
                                print(f'Rate limit found = {rate_limit} / sec')
                            #  if we find a rate limit but we can look out for limit remaining 
                            limit_reset = headers.get('CR-TDM-Rate-Limit-Reset')
                            if limit_reset:
                                # now check to see if we have met the limit of download 
                                limit_remaining = headers.get('CR-TDM-Rate-Limit-Remaining')
                                if limit_remaining:
                                    if int(limit_remaining) == 0:
                                        print('download limit reached, need to back off')
                                        sleep(int(limit_reset))

                            # now lets look for the content type of the response
                            format_type = response.headers.get('Content-Type')
                            if format_type is None:
                                soup = BeautifulSoup(response.text)
                                format_type = doctype(soup)

                            print(f'Format:{format_type} found')


                            if ('pdf' in format_type.lower()) or ('.pdf' in link):
                                if retrieval_df.pdf.loc[index] != 1:
                                    if response_d['headers']['Content-Type'] == 'application/pdf':
                                        with open(f'./output/formats/pdfs/{index}.pdf', 'wb') as file:
                                            file.write(response.content)
                                        try:
                                            pdf_d = pdf_file_to_parse_d(retrieval_df, index, f'./output/formats/pdfs/{index}.pdf', link)
                                            if pdf_d['Content_type'] == 'pdf' and pdf_d['text'] != '' and (len(pdf_d['abstract'].split()) < pdf_d['wc'] or len(pdf_d['abstract'].split()) > 1000 if pdf_d['abstract'] != None else True) and 100 < pdf_d['wc']:
                                                retrieval_df.loc[index, 'pdf'] = 1                                    
                                                retrieval_df.loc[index, 'pdf_parse_d'] = [pdf_d]
                                            else:
                                                pass
                                        except:
                                            pass
                                    else:
                                        pass
                                else:
                                    pass

                            elif ('xml' in format_type.lower()) or ('.xml' in link):
                                if retrieval_df.xml.loc[index] != 1:
                                    # perform xml parsing and FP detection
                                    xml_d = xml_response_to_parse_d(retrieval_df, index, response)
                                    xml_d = evaluation_funct(xml_d)
                                    #print(xml_d['evaluation'])
                                    # now we have the xml_d we can compare look at the parsed text to decide if it is a TP, FP or AB class
                                    if xml_d['evaluation'] == 'TP' and (len(xml_d['abstract'].split()) < xml_d['wc'] or len(xml_d['abstract'].split()) > 1000 if xml_d['abstract'] != None else True) and 100 < xml_d['wc']:
                                        with open(f'./output/formats/xmls/{index}.xml', 'w') as file:
                                                file.write(response.text.encode('ascii', 'ignore').decode())
                                        retrieval_df.loc[index,'xml'] = 1
                                        retrieval_df.loc[index,'xml_parse_d'] = [xml_d]
                                    else:
                                        pass
                                else:
                                    pass

                            elif 'html' in format_type.lower():
                                if retrieval_df.html.loc[index] != 1:
                                    # all the htmls should be checked for links regardless of whether they are FT or AB
                                    html_links = complete_html_link_parser(response)
                                    if len(html_links) != 0:
                                        full_text_link_dict = retrieval_df.loc[index, 'full_text_links']
                                        full_text_link_dict.update({'html_parse':html_links})
                                        retrieval_df.at[index, 'full_text_links'] = full_text_link_dict
                                    
                                    # perform html parsing and FP detection
                                    html_d = html_response_to_parse_d(retrieval_df, index, response)
                                    html_d = evaluation_funct(html_d)
                                    #print(html_d['evaluation'])
                                    # now we have the xml_d we can compare look at the parsed text to decide if it is a TP, FP or AB class
                                    if html_d['evaluation'] == 'TP' and (len(html_d['abstract'].split()) < html_d['wc'] or len(html_d['abstract'].split()) > 1000 if html_d['abstract'] != None else True) and 100 < html_d['wc']:
                                        with open(f'./output/formats/htmls/{index}.html', 'w') as file:
                                                file.write(response.text.encode('ascii', 'ignore').decode())
                                        retrieval_df.loc[index,'html'] = 1
                                        retrieval_df.loc[index,'html_parse_d'] = [html_d]
                                    else:
                                        pass
                                else:
                                    pass

                            elif 'plain' in format_type.lower():
                                if retrieval_df.plain.loc[index] != 1:
                                    with open(f'./output/formats/txts/{index}.txt', 'w') as file:
                                            file.write(response.text.encode('ascii', 'ignore').decode())
                                    plain_d = plain_file_to_parse_d(retrieval_df, index, f'./output/formats/txts/{index}.txt', link)
                                    if plain_d['text'] != '' and (len(plain_d['abstract'].split()) < plain_d['wc'] or len(plain_d['abstract'].split()) > 1000 if plain_d['abstract'] != None else True) and 100 < plain_d['wc']:
                                        retrieval_df.loc[index, 'plain_parse_d'] = [plain_d]
                                        retrieval_df.loc[index,'plain'] = 1
                                else:
                                    pass

                        else:
                            # request failed, move on to the next one      
                            pass
            else:
                # no crossref links tdm links for this record 
                print('No Crossref links for this article')
                pass
            
        elif stage == 'epmcxml':
            if retrieval_df.xml.loc[index] != 1 and retrieval_df.pmcid.loc[index] == retrieval_df.pmcid.loc[index]:
                try:
                    response_d, response = get_request(pmcid, http, base_url, headers, 'epmcxml')
                except:
                    pass
                if response_d['status_code'] == 429:
                    print('"Too many requests error [429]" received')
                    print('Risk of IP address block: stopping script')
                    exit()
                elif response_d['status_code'] == 200:
                    # perform xml parsing and FP detection
                    xml_d = xml_response_to_parse_d(retrieval_df, index, response)
                    xml_d = evaluation_funct(xml_d)
                    # now we have the xml_d we can compare look at the parsed text to decide if it is a TP, FP or AB class
                    if xml_d['evaluation'] == 'TP' and (len(xml_d['abstract'].split()) < xml_d['wc'] or len(xml_d['abstract'].split()) > 1000 if xml_d['abstract'] != None else True) and 100 < xml_d['wc']:
                        print('success, now writing to file')
                        # if status code == 200 then write the response text to file as an xml
                        with open(f'./output/formats/xmls/{index}.xml', 'w+') as file:
                            file.write(response_d['text'].encode('ascii', 'ignore').decode())
                            # we can keep track of the sucesses as we go by saving 1 to xml column
                        retrieval_df.loc[index,'xml'] = 1
                        retrieval_df.loc[index,'xml_parse_d'] = [xml_d]
                else:
                    print('error with request')
                    print(f'{response_d["error"]}')
            else:
                pass
                
            '''elif stage == 'epmcsupp':
                response_d, response = get_request(pmcid, http, base_url, 'epmcsupp')
                if response_d['status_code'] == 429:
                    print('"Too many requests error [429]" received')
                    print('Risk of IP address block: stopping script')
                    break
                elif response_d['status_code'] == 200:
                    print('success, now writing zip to file')
                    handle = open(f'./output/formats/zips/{index}.zip', "wb")
                    for chunk in response.iter_content(chunk_size=2048):
                        if chunk:  # filter out keep-alive new chunks
                            handle.write(chunk)
                    handle.close()
                    retrieval_df.loc[index, 'supp'] = 1
                else:
                    response.close()'''
        
        elif stage == 'pmcxmls':
            if retrieval_df.xml.loc[index] != 1 and retrieval_df.pmcid.loc[index] == retrieval_df.pmcid.loc[index]:
                try:
                    response_d, response = get_request(pmcid, http, base_url, headers, 'pmcxmls')
                except:
                    pass
                if response_d['status_code'] == 429:
                        print('"Too many requests error [429]" received')
                        print('Risk of IP address block: stopping script')
                        exit()
                elif response_d['status_code'] == 200:
                    # perform xml parsing and FP detection
                    xml_d = xml_response_to_parse_d(retrieval_df, index, response)
                    xml_d = evaluation_funct(xml_d)
                    # now we have the xml_d we can compare look at the parsed text to decide if it is a TP, FP or AB class
                    if xml_d['evaluation'] == 'TP' and (len(xml_d['abstract'].split()) < xml_d['wc'] or len(xml_d['abstract'].split()) > 1000 if xml_d['abstract'] != None else True) and 100 < xml_d['wc']:
                        print('success, now writing to file')
                        with open(f'./output/formats/xmls/{index}.xml', 'w') as file:
                            file.write(response_d['text'].encode('ascii', 'ignore').decode())
                        retrieval_df.loc[index,'xml'] = 1
                        retrieval_df.loc[index,'xml_parse_d'] = [xml_d]
                else:
                    print('error with request')
                    print(f'{response_d["error"]}')
            else:
                pass
                
        elif stage == 'pmcpdfs':
            if retrieval_df.pdf.loc[index] != 1 and retrieval_df.pmcid.loc[index] == retrieval_df.pmcid.loc[index]:
                try:
                    response_d, response = get_request(pmcid, http, base_url, headers, 'pmcpdfs')
                except:
                    pass
                if response_d['status_code'] == 429:
                    print('"Too many requests error [429]" received')
                    print('Risk of IP address block: stopping script')
                    exit()
                elif response_d['status_code'] == 200:

                    # The response for this API is an xml which provides links to the resource
                    # lets use beautiful soup to parse the xml
                    soup = BeautifulSoup(response.text)
                    for link in soup.find_all('link'):

                        # the link could be to a tgz
                        ''' if link.attrs['format'] == 'tgz':
                            print('tar zip file available')
                            ftp_link = link.get('href')
                            # if it is a tgz then it'll probably need to be written in chunks 
                            # **** ? server hangs at this point? **********
                            with closing(request.urlopen(ftp_link)) as r:
                                with open(f'./output/formats/tgzs/{index}.tgz', 'wb') as f:
                                    shutil.copyfileobj(r, f)
                                    retrieval_df.loc[index, 'pmc_zip'] = 1'''

                        # check for pdf format
                        if link.attrs['format'] == 'pdf':
                            print('pdf file available')
                            # get the link for the pdf
                            ftp_link = link.get('href')
                            with closing(request.urlopen(ftp_link)) as r:
                                detection = r.info().get_content_subtype()
                                if detection == 'pdf':
                                    with open(f'./output/formats/pdfs/{index}.pdf', 'wb') as f:
                                        shutil.copyfileobj(r, f)
                                    try:
                                        pdf_d = pdf_file_to_parse_d(retrieval_df, index, f'./output/formats/pdfs/{index}.pdf', ftp_link)           
                                        if pdf_d['Content_type'] == 'pdf' and pdf_d['text'] != '' and (len(pdf_d['abstract'].split()) < pdf_d['wc'] or len(pdf_d['abstract'].split()) > 1000 if pdf_d['abstract'] != None else True) and 100 < pdf_d['wc']:
                                            retrieval_df.loc[index, 'pdf'] = 1
                                            retrieval_df.loc[index, 'pdf_parse_d'] = [pdf_d]
                                        else:
                                            pass
                                    except:
                                        pass
                                else:
                                    pass
                # alternative error code, register the fail but keep going.     
                else:
                    print('error with request')
                    print(f'{response_d["error"]}')    
                    pass
            else:
                pass
                            
        
        elif stage == 'pmctgz':
            if retrieval_df.pmc_tgz.loc[index] != 1 and retrieval_df.pmcid.loc[index] == retrieval_df.pmcid.loc[index]:
                try:
                    response_d, response = get_request(pmcid, http, base_url, headers, 'pmctgz')
                except:
                    pass
                if response_d['status_code'] == 429:
                    print('"Too many requests error [429]" received')
                    print('Risk of IP address block: stopping script')
                    exit()
                elif response_d['status_code'] == 200:

                    # The response for this API is an xml which provides links to the resource
                    # lets use beautiful soup to parse the xml
                    soup = BeautifulSoup(response.text)
                    for link in soup.find_all('link'):

                        # the link could be to a tgz
                        if link.attrs['format'] == 'tgz':
                            print('tar zip file available')
                            ftp_link = link.get('href')
                            # if it is a tgz then it'll probably need to be written in chunks 
                            # **** ? server hangs at this point? **********
                            out_file = f'./output/formats/tgzs/{index}.tgz'
                            try:
                                timeout_time = 300 
                                start = time.time()
                                worked = False

                                pnum = 1
                                procs = []
                                for i in range(pnum):
                                    p = Process(target=wget.download, args=(ftp_link, out_file), name = ('process_' + str(i+1)))
                                    procs.append(p)
                                    p.start()
                                while time.time() - start <= timeout_time:
                                    if not any([p.is_alive() for p in procs]):
                                        # All the processes are done, break now.
                                        worked = True
                                        retrieval_df.loc[index, 'pmc_tgz'] = 1
                                        p.terminate()
                                        p.join()
                                        break

                                    time.sleep(1)  # Just to avoid hogging the CPU
                                else:
                                    # We only enter this if we didn't 'break' above.
                                    print("timed out, killing all processes")
                                    for p in procs:
                                        p.terminate()
                                        p.join()
                            except:
                                pass
                            # run the function to unpack the tgz looking for pdfs and xmls
                            if worked == True:
                                try:
                                    retrieval_df = timeout(300)(tgz_unpacking)(index, retrieval_df, f'./output/formats/tgzs/{index}.tgz', ftp_link)
                                except:
                                    pass #handle errors                           
                        else:
                            pass

                            
                            
                            
#                                 with closing(request.urlopen(ftp_link)) as r:
#                                     try:
#                                         with open(, 'wb') as f:
#                                             shutil.copyfileobj(r, f)
#                                             retrieval_df.loc[index, 'pmc_tgz'] = 1
#                                             # run the function to unpack the tgz looking for pdfs and xmls
#                                             retrieval_df = tgz_unpacking(index, retrieval_df, f'./output/formats/tgzs/{index}.tgz')
#                                     except:
#                                         print('There seems to be an incomplete file download')

                                    

                # alternative error code, register the fail but keep going.     
                else:
                    print('error with request')
                    print(f'{response_d["error"]}')    
                    pass
            else:
                pass
                
        elif stage == 'doiorg':
            if retrieval_df.doi.loc[index] == retrieval_df.doi.loc[index]:
                try:
                    response_d, response = get_request(doi, http, base_url, headers, 'doiorg')
                except:
                    pass
                # check the response status
                if response_d['status_code'] == 429:
                    print('"Too many requests error [429]" received')
                    print('Risk of IP address block: stopping script')
                    exit()
                elif (response_d['status_code'] == 200):
                    # rule of thumb if content less than 10000 bytes, it is rubbish
                    if (len(response_d['content']) > 100):

                        # now lets get the format of the doc
                        if response_d['headers'].get('Content-Type') != None: 
                            format_type = response_d['headers']['Content-Type']
                        else:
                            format_type = ''
                        if format_type == '':
                            print('No format Type in the headers, trying to extract from soup object')
                            soup = BeautifulSoup(response_d['text'])
                            format_type = doctype(soup)
                            if format_type == None:
                                format_type = ''
                            print(f'Format type: {format_type}')
                        if format_type != None:
                            print(f'Format:{format_type} found')

                            # execute if we have a set format
                            if 'pdf' in format_type.lower() and retrieval_df.pdf.loc[index] != 1:
                                if response_d['headers'].get('Content-Type') != None: 
                                    if response_d['headers']['Content-Type'] == 'application/pdf':
                                        with open(f'./output/formats/pdfs/{index}.pdf', 'wb') as file:
                                            file.write(response_d['content'])
                                        try:
                                            pdf_d = pdf_file_to_parse_d(retrieval_df, index, f'./output/formats/pdfs/{index}.pdf', f'{base_url}{doi}')
                                            if pdf_d['Content_type'] == 'pdf' and pdf_d['text'] != '' and (len(pdf_d['abstract'].split()) < pdf_d['wc'] or len(pdf_d['abstract'].split()) > 1000 if pdf_d['abstract'] != None else True) and 100 < pdf_d['wc']:
                                                retrieval_df.loc[index, 'pdf'] = 1
                                                retrieval_df.loc[index, 'pdf_parse_d'] = [pdf_d]
                                            else:
                                                pass
                                        except:
                                            pass
                                    else:
                                        pass
                                else:
                                    pass
                            
                            elif 'xml' in format_type.lower() and retrieval_df.xml.loc[index] != 1:
                                # perform xml parsing and FP detection
                                xml_d = xml_response_to_parse_d(retrieval_df, index, response)
                                xml_d = evaluation_funct(xml_d)
                                # now we have the xml_d we can compare look at the parsed text to decide if it is a TP, FP or AB class
                                if xml_d['evaluation'] == 'TP' and (len(xml_d['abstract'].split()) < xml_d['wc'] or len(xml_d['abstract'].split()) > 1000 if xml_d['abstract'] != None else True) and 100 < xml_d['wc']:
                                    with open(f'./output/formats/xmls/{index}.xml', 'w') as file:
                                            file.write(response_d['text'].encode('ascii', 'ignore').decode())
                                    retrieval_df.loc[index,'xml'] = 1
                                    retrieval_df.loc[index,'xml_parse_d'] = [xml_d]

                            ## TESTING FOR JAMIE, GET FALSE POSITIVE PART 1/2
                            
                            elif 'html'in format_type.lower() and retrieval_df.html.loc[index] == 1:
                                # all the htmls should be checked for links regardless of whether they are FT or AB
                                html_links = complete_html_link_parser(response)
                                if len(html_links) != 0:
                                    full_text_link_dict = retrieval_df.loc[index, 'full_text_links']
                                    full_text_link_dict.update({'html_parse':html_links})
                                    retrieval_df.at[index, 'full_text_links'] = full_text_link_dict
                                html_d = html_response_to_parse_d(retrieval_df, index, response)
                                html_d = evaluation_funct(html_d)
                                if html_d['evaluation'] == 'FP':
                                        with open(f'./output/formats/testing/{index}.html', 'w') as file:
                                            file.write(response_d['text'].encode('ascii', 'ignore').decode())

                            ## FINISH TESTING PART 1/2

                            elif 'html' in format_type.lower() and retrieval_df.html.loc[index] != 1:
                                # all the htmls should be checked for links regardless of whether they are FT or AB
                                html_links = complete_html_link_parser(response)
                                if len(html_links) != 0:
                                    full_text_link_dict = retrieval_df.loc[index, 'full_text_links']
                                    full_text_link_dict.update({'html_parse':html_links})
                                    retrieval_df.at[index, 'full_text_links'] = full_text_link_dict
                            
                                # perform html parsing and FP detection
                                html_d = html_response_to_parse_d(retrieval_df, index, response)
                                html_d = evaluation_funct(html_d)
                                # now we have the xml_d we can compare look at the parsed text to decide if it is a TP, FP or AB class
                                if html_d['evaluation'] == 'TP' and (len(html_d['abstract'].split()) < html_d['wc'] or len(html_d['abstract'].split()) > 1000 if html_d['abstract'] != None else True) and 100 < html_d['wc']:
                                    with open(f'./output/formats/htmls/{index}.html', 'w') as file:
                                            file.write(response_d['text'].encode('ascii', 'ignore').decode())
                                    retrieval_df.loc[index,'html'] = 1
                                    retrieval_df.loc[index,'html_parse_d'] = [html_d]

                                ## TESTING FPs JAMIS PART 2/2
                                if html_d['evaluation'] == 'FP':
                                        with open(f'./output/formats/testing/{index}.html', 'w') as file:
                                            file.write(response_d['text'].encode('ascii', 'ignore').decode())
                                ##FINISH PART 2/2
                        
                            elif 'plain' in format_type.lower() and retrieval_df.plain.loc[index] != 1:
                                with open(f'./output/formats/txts/{index}.txt', 'w') as file:
                                    file.write(response_d['text'].encode('ascii', 'ignore').decode())
                                plain_d = plain_file_to_parse_d(retrieval_df, index, f'./output/formats/txts/{index}.txt', f'{base_url}{doi}')
                                if plain_d['text'] != '' and (len(plain_d['abstract'].split()) < plain_d['wc'] or len(plain_d['abstract'].split()) > 1000 if plain_d['abstract'] != None else True) and 100 < plain_d['wc']:
                                    retrieval_df.loc[index, 'plain_parse_d'] = [plain_d]
                                    retrieval_df.loc[index,'plain'] = 1 
                                
                                                

                        # if no format then fail this index
                        else:
                            pass
                    # if doc <10,000 bytes then fail this index
                    else:
                        pass
                # if response status not 200 then fail this index
                else:
                    pass
            else:
                pass
                            
                            
######################################### Pubmed PMID request and link extraction ####################################
#########################################  ####################################
        # This stage sends a get request using a pmid to PUBMED to try and get the Full text links from the html page 'linkout' section
        # we don't need to save the page, just parse the request.text and save the links to the master df
        elif stage == 'pubmed':
            # firstly check that there is a PMID to use (np.nan == np.nan == False)
            if retrieval_df.pmid.loc[index] == retrieval_df.pmid.loc[index]:
                # set the conditions for when to try (No Tagged version (HTML or XML) or no PDF)           
                if ((retrieval_df.html.loc[index] == 0) and (retrieval_df.xml.loc[index] == 0)) or (retrieval_df.pdf.loc[index]) == 0:
                    # send the request to pubmed using the base url and pmid
                    try:
                        response_d, response = get_request(pmid, http, base_url, headers, 'pubmed')
                    except:
                        pass
                    # check the resonse code
                    if response_d['status_code'] == 429:
                        print('"Too many requests error [429]" received')
                        print('Risk of IP address block: stopping script')
                        exit()
                    elif response_d['status_code'] == 200:
                        # if the response code is 200 then we can parse out the links from linkout section using our function above.
                        retrieval_df = pubmed_linkout_parse(index, retrieval_df, response) 
                            
                else:
                    # we already have all the required versions, no need to try the pubmed route
                    pass
                
            else:
                # we don't have a pmid so no point in trying this option
                pass
######################################### Pubmed PMID request and link extraction ####################################
#########################################  ####################################
                            
        else:
            pass
        
        print('\nnext record\n')
        if counter%10 == 0 and not counter%100 == 0 and not counter == 0:
            sleep(2)
            clear()
            print(f'In case of faillure please put the parameters start="{saved_stage}" (or "{saved_stage}_only" if in only mode) and idx="{saved_index}"')
            print('\n') 
        elif counter%100 == 0 and not counter == 0:
            sleep(2)
            clear()
            saved_stage = stage
            saved_index = index
            pickle.dump(retrieval_df, open(f'./output/master_df/master_df.p', 'wb'))
            print(f'In case of faillure please put the parameters start="{saved_stage}" (or "{saved_stage}_only" if in only mode) and idx="{saved_index}"')
            print('\n')

        
    print('process Complete')
    if stage == 'crossref':
        pickle.dump(retrieval_df, open('./output/master_df/crossref_download_df.p', 'wb'))
        pickle.dump(retrieval_df, open(f'./output/master_df/master_df.p', 'wb'))
    elif stage == 'epmcxml':
        pickle.dump(retrieval_df, open('./output/master_df/pmcid_df.p', 'wb'))
        pickle.dump(retrieval_df, open(f'./output/master_df/master_df.p', 'wb'))
    elif stage == 'epmcsupp':
        pickle.dump(retrieval_df, open('./output/master_df/epmc_supp_df.p', 'wb'))
        pickle.dump(retrieval_df, open(f'./output/master_df/master_df.p', 'wb'))
    elif stage == 'pmcxmls':
        pickle.dump(retrieval_df, open('./output/master_df/pmc_oai_df.p', 'wb'))
        pickle.dump(retrieval_df, open(f'./output/master_df/master_df.p', 'wb'))
    elif stage == 'pmcpdfs':
        pickle.dump(retrieval_df, open('./output/master_df/pmc_oai_pdf_df.p', 'wb'))
        pickle.dump(retrieval_df, open(f'./output/master_df/master_df.p', 'wb'))
    elif stage == 'doiorg':
        pickle.dump(retrieval_df, open('./output/master_df/doi_org.p', 'wb'))
        pickle.dump(retrieval_df, open(f'./output/master_df/master_df.p', 'wb'))
    elif stage == 'pubmed':
        pickle.dump(retrieval_df, open('./output/master_df/pubmed_df.p', 'wb'))
        pickle.dump(retrieval_df, open(f'./output/master_df/master_df.p', 'wb'))
    else:
        pass   

    return retrieval_df