from cadmus.retrieval.get_request import get_request
from cadmus.parsing.xml_response_to_parse_d import xml_response_to_parse_d
from cadmus.parsing.doctype import doctype
from cadmus.evaluation.evaluation_funct import evaluation_funct
from cadmus.retrieval.complete_html_link_parser import complete_html_link_parser
from cadmus.parsing.html_response_to_parse_d import html_response_to_parse_d
from cadmus.parsing.pdf_file_to_parse_d import pdf_file_to_parse_d
from cadmus.parsing.plain_file_to_parse_d import plain_file_to_parse_d
from cadmus.parsing.tgz_unpacking import tgz_unpacking
from cadmus.retrieval.pubmed_linkout_parse import pubmed_linkout_parse
from cadmus.retrieval.clear import clear
from cadmus.retrieval.timeout import timeout
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
import pandas as pd
import json

def retrieval(retrieval_df, http, base_url, headers, stage, keep_abstract, done = None):
    # the input will be the retrieved_df and each process will be subset so that the required input is always available (doi or pmid or pmcid)
    #the counter variable keep track on when to save the current result, every 100 rows or when a step is completed
    counter = 0

    #subset the original df to the lines with an identifier only (PMCID, PMID, DOI), the function is doing that to minimise the time to spent
    if stage == 'crossref':
        condition = []
        for i in range(len(retrieval_df)):
            if len(retrieval_df.iloc[i]['full_text_links'].get('cr_tdm')) > 0:
                condition.append(True)
            else:
                condition.append(False)
        cr_df = retrieval_df[condition]

    elif stage == 'epmcxml' or stage == 'epmcsupp' or stage == 'pmcxmls' or stage == 'pmcpdfs' or stage == 'pmctgz':
        cr_df = retrieval_df[retrieval_df.pmcid.notnull()]
    elif stage == 'doiorg':
        cr_df = retrieval_df[retrieval_df.doi.notnull()]
    elif stage == 'pubmed':
        cr_df = retrieval_df[retrieval_df.pmid.notnull()]

    else:
        print('There is an error in the stage idendification please fill a bug repport')
        exit()

    for index, row in cr_df.iterrows():
        if counter == 0:
            #cleaning the terminal windows
            clear()
            #showing on top of the screen what to put in case of failure
            print(f'In case of faillure please put the parameters start="{stage}" (or "{stage}_only" if in only mode) and idx="{index}"') 
            # save the last stage and index where we saved the df
            saved_stage = stage
            saved_index = index   
            print('\n')   
        counter += 1
        if stage == 'crossref':
            #printing the number of row remaining on the crossref step
            print('Downloading Crossref TDM links now...')
            print(f'tdm full link {counter} of {len(cr_df)}') 
            
        elif stage == 'epmcxml' or stage == 'epmcsupp' or stage == 'pmcxmls' or stage == 'pmcpdfs' or stage == 'pmctgz':
            #checking that the PMCID is not nan, PMICD is the key needed for epmc pmc
            if retrieval_df.pmcid.loc[index] != None:
                pmcid = row['pmcid']
                print(f'Looking for {pmcid} which is record {counter} of {len(cr_df)}')
                if stage == 'pmcxmls' or stage == 'pmcpdfs':
                    #formating the value to the right format for these APIs
                    pmcid = pmcid.replace('PMC', '')
                else:
                    pass
            else:
                pass
        
        elif stage == 'doiorg':
            # checking the DOI is not nan
            if retrieval_df.doi.loc[index] != None:
                #extracting the doi needed for doiorg
                doi = row['doi']
                print(f'DOI {counter} of {len(cr_df)}')
            else:
                pass
        
        elif stage == 'pubmed':
            # checking the pmid is not nan
            if retrieval_df.pmid.loc[index] == retrieval_df.pmid.loc[index]:
                #extracting the pmid needed for the pubmed step
                pmid = row['pmid']
                print(f'working on pmid:{pmid}, record {counter} of {len(cr_df)}')
            else:
                pass
        
        else:
            pass
            
        if stage == 'crossref':
            #collect all the crossref links available for text mining
            links = row['full_text_links'].get('cr_tdm')
            if links:                               
                for link in links: 
                    #trying to indentifying the format from the link in order to not request a document if it is already retreive for that format
                    if ('.pdf' in link and retrieval_df.pdf.loc[index] == 1) or  ('.xml' in link and retrieval_df.xml.loc[index] == 1) or ('plain' in link and retrieval_df.plain.loc[index] == 1):  
                        pass
                    else: 
                        #printing the link we are trying to download from          
                        print(f'trying to download from: \n{link}')
                        try:
                            #requesting the document by creatng the header and the request
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

                            if format_type == None:
                                format_type = ''
                            print(f'Format:{format_type} found')

                            #in case the link suggest that the link direct to a pdf format
                            if ('pdf' in format_type.lower()) or ('.pdf' in link):
                                #looking if the pdf format was already retreived, if not we will try, if already retreived we go to the next record
                                if retrieval_df.pdf.loc[index] != 1:
                                    #looking if the docuemnt retreived is really a pdf
                                    if response_d['headers']['Content-Type'] == 'application/pdf':
                                        with open(f'./output/formats/pdfs/{index}.pdf', 'wb') as file:
                                            #saving the finle to the appropriate path
                                            file.write(response.content)
                                        try:
                                            #looking at the content of the pdf, if the content showed evidence it is the full text we modify the df to update with the new information
                                            pdf_d, p_text = pdf_file_to_parse_d(retrieval_df, index, f'./output/formats/pdfs/{index}.pdf', link, keep_abstract)
                                            if pdf_d['Content_type'] == 'pdf' and pdf_d['wc'] != 0 and (pdf_d['wc_abs'] < pdf_d['wc'] or pdf_d['wc_abs'] > 1000 if pdf_d['wc_abs'] != 0 else True) and 100 < pdf_d['wc']:
                                                # we change the value to 1 in order to not look for that format again
                                                retrieval_df.loc[index, 'pdf'] = 1                                    
                                                retrieval_df.loc[index, 'pdf_parse_d'].update(pdf_d)
                                                f = open(f"./output/retrieved_parsed_files/pdfs/{index}.txt", "w")
                                                f.write(p_text)
                                                f.close()
                                            else:
                                                pass
                                            if 'wc' in row['pdf_parse_d'].keys():
                                                pass
                                            else:
                                                retrieval_df.loc[index, 'pdf'] = int(0)
                                        except:
                                            pass
                                    else:
                                        pass
                                else:
                                    pass
                            # trying to indentify if the link will provide the algorithm with a xml format
                            elif ('xml' in format_type.lower()) or ('.xml' in link):
                                # the algorithm will spend time on the following only if it has not retrieved it already
                                if retrieval_df.xml.loc[index] != 1:
                                    # perform xml parsing and FP detection
                                    xml_d, p_text = xml_response_to_parse_d(retrieval_df, index, response, keep_abstract)
                                    xml_d = evaluation_funct(xml_d)
                                    # now we have the xml_d we can evaluate to decide if it is a TP, FP or AB
                                    if xml_d['evaluation'] == 'TP' and (xml_d['wc_abs'] < xml_d['wc'] or xml_d['wc_abs'] > 1000 if xml_d['wc_abs'] != 0 else True) and 100 < xml_d['wc']:
                                        with open(f'./output/formats/xmls/{index}.xml', 'w') as file:
                                                # saving the  file to a pre-defines directory as we identified it as TP
                                                file.write(response.text.encode('ascii', 'ignore').decode())
                                        # changing the value to one for future references
                                        retrieval_df.loc[index,'xml'] = 1
                                        retrieval_df.loc[index,'xml_parse_d'].update(xml_d)
                                        f = open(f"./output/retrieved_parsed_files/xmls/{index}.txt", "w")
                                        f.write(p_text)
                                        f.close()

                                    else:
                                        pass
                                    if 'wc' in row['xml_parse_d'].keys():
                                        pass
                                    else:
                                        retrieval_df.loc[index, 'xml'] = int(0)
                                else:
                                    pass

                            elif 'html' in format_type.lower():
                                # the function will spend time to the following only if no html were saved before
                                if retrieval_df.html.loc[index] != 1:
                                    # all the htmls should be checked for candidate link(s) regardless of whether they are FP or AB
                                    html_links = complete_html_link_parser(response)
                                    # list of potential candidate links
                                    if len(html_links) != 0:
                                        # the dictionary that contains the list is updated as we try new pages
                                        full_text_link_dict = retrieval_df.loc[index, 'full_text_links']
                                        full_text_link_dict.update({'html_parse':html_links})
                                        retrieval_df.at[index, 'full_text_links'] = full_text_link_dict
                                    
                                    # perform html parsing and FP detection
                                    html_d, p_text = html_response_to_parse_d(retrieval_df, index, response, keep_abstract)
                                    html_d = evaluation_funct(html_d)
                                    # now we have the html_d we can evaluate to decide if it is a TP, FP or AB
                                    if html_d['evaluation'] == 'TP' and (html_d['wc_abs'] < html_d['wc'] or html_d['wc_abs'] > 1000 if html_d['wc_abs'] != 0 else True) and 100 < html_d['wc']:
                                        with open(f'./output/formats/htmls/{index}.html', 'w') as file:
                                                # since the file as been identified as TP we save it to a pre-defined structure
                                                file.write(response.text.encode('ascii', 'ignore').decode())
                                        retrieval_df.loc[index,'html'] = 1
                                        retrieval_df.loc[index,'html_parse_d'].update(html_d)
                                        f = open(f"./output/retrieved_parsed_files/htmls/{index}.txt", "w")
                                        f.write(p_text)
                                        f.close()

                                    else:
                                        pass
                                    if 'wc' in row['html_parse_d'].keys():
                                        pass
                                    else:
                                        retrieval_df.loc[index, 'html'] = int(0)
                                else:
                                    pass
                            #doing the same as before for .txt file format
                            elif 'plain' in format_type.lower():
                                if retrieval_df.plain.loc[index] != 1:
                                    with open(f'./output/formats/txts/{index}.txt', 'w') as file:
                                            file.write(response.text.encode('ascii', 'ignore').decode())
                                    plain_d, p_text = plain_file_to_parse_d(retrieval_df, index, f'./output/formats/txts/{index}.txt', link, keep_abstract)
                                    if plain_d['wc'] != 0 and (plain_d['wc_abs'] < plain_d['wc'] or plain_d['wc_abs'] > 1000 if plain_d['wc_abs'] != 0 else True) and 100 < plain_d['wc']:
                                        retrieval_df.loc[index, 'plain_parse_d'].update(plain_d)
                                        retrieval_df.loc[index,'plain'] = 1
                                        f = open(f"./output/retrieved_parsed_files/txts/{index}.txt", "w")
                                        f.write(p_text)
                                        f.close()
                                    if 'wc' in row['plain_parse_d'].keys():
                                        pass
                                    else:
                                        retrieval_df.loc[index, 'plain'] = int(0)

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
            #if xml already retrieved or if the identifier is mising going to the next record
            if retrieval_df.xml.loc[index] != 1 and retrieval_df.pmcid.loc[index] != None:
                try:
                    #creating the header and the protocol to retreive the file from epmc API
                    response_d, response = get_request(pmcid, http, base_url, headers, 'epmcxml')
                except:
                    pass
                #if the code status we get from the server is 429, we notifiy the user and stop the process to give some time to rest
                if response_d['status_code'] == 429:
                    print('"Too many requests error [429]" received')
                    print('Risk of IP address block: stopping script')
                    exit()
                #if status code is 200, it means everything works correctly
                elif response_d['status_code'] == 200:
                    # perform xml parsing and FP detection
                    xml_d, p_text = xml_response_to_parse_d(retrieval_df, index, response, keep_abstract)
                    xml_d = evaluation_funct(xml_d)
                    # now we have the xml_d we can compare look at the parsed text to decide if it is a TP, FP or AB class
                    if xml_d['evaluation'] == 'TP' and (xml_d['wc_abs'] < xml_d['wc'] or xml_d['wc_abs'] > 1000 if xml_d['wc_abs'] != 0 else True) and 100 < xml_d['wc']:
                        print('success, now writing to file')
                        # the file as been classified as TP, saving the file
                        with open(f'./output/formats/xmls/{index}.xml', 'w+') as file:
                            file.write(response_d['text'].encode('ascii', 'ignore').decode())
                        # we can keep track of the sucesses as we go by saving 1 to xml column and avoid trying again
                        retrieval_df.loc[index,'xml'] = 1
                        retrieval_df.loc[index,'xml_parse_d'].update(xml_d)
                        f = open(f"./output/retrieved_parsed_files/xmls/{index}.txt", "w")
                        f.write(p_text)
                        f.close()
                    if 'wc' in row['xml_parse_d'].keys():
                        pass
                    else:
                        retrieval_df.loc[index, 'xml'] = int(0)

                else:
                    print('error with request')
                    print(f'{response_d["error"]}')
            else:
                pass
        
        elif stage == 'pmcxmls':
            #if xml already retreived, or identifier missing going to next record
            if retrieval_df.xml.loc[index] != 1 and retrieval_df.pmcid.loc[index] != None:
                try:
                    #creating the header and protocol to retreive the document from PMC API
                    response_d, response = get_request(pmcid, http, base_url, headers, 'pmcxmls')
                except:
                    pass
                #if the error code is 429 stoping the process to give time to rest
                if response_d['status_code'] == 429:
                        print('"Too many requests error [429]" received')
                        print('Risk of IP address block: stopping script')
                        exit()
                # code 200 everything works correctly
                elif response_d['status_code'] == 200:
                    # perform xml parsing and FP detection
                    xml_d, p_text = xml_response_to_parse_d(retrieval_df, index, response, keep_abstract)
                    xml_d = evaluation_funct(xml_d)
                    # now we have the xml_d we can decide if it is a TP, FP or AB class
                    if xml_d['evaluation'] == 'TP' and (xml_d['wc_abs'] < xml_d['wc'] or xml_d['wc_abs'] > 1000 if xml_d['wc_abs'] != 0 else True) and 100 < xml_d['wc']:
                        print('success, now writing to file')
                        with open(f'./output/formats/xmls/{index}.xml', 'w') as file:
                            # saving the file as it has been evaluated as TP
                            file.write(response_d['text'].encode('ascii', 'ignore').decode())
                        retrieval_df.loc[index,'xml'] = 1
                        retrieval_df.loc[index,'xml_parse_d'].update(xml_d)
                        f = open(f"./output/retrieved_parsed_files/xmls/{index}.txt", "w")
                        f.write(p_text)
                        f.close()
                    if 'wc' in row['xml_parse_d'].keys():
                        pass
                    else:
                        retrieval_df.loc[index, 'xml'] = int(0)

                else:
                    # in case the status code is different than 200 or 429
                    print('error with request')
                    print(f'{response_d["error"]}')
            else:
                pass
                
        elif stage == 'pmcpdfs':
            # looking if the pdf is already retreived for that row, if yes moving to the next record
            # the condition alse check if an identifier is present
            if retrieval_df.pdf.loc[index] != 1 and retrieval_df.pmcid.loc[index] != None:
                try:
                    #creating the header and the protocol to request the docuemnt from PMC API
                    response_d, response = get_request(pmcid, http, base_url, headers, 'pmcpdfs')
                except:
                    pass
                #stop the process in case of 429 status code
                if response_d['status_code'] == 429:
                    print('"Too many requests error [429]" received')
                    print('Risk of IP address block: stopping script')
                    exit()
                #status code 200 means everything works perfectly
                elif response_d['status_code'] == 200:

                    # The response for this API is an xml which provides links to the resource
                    # lets use beautiful soup to parse the xml
                    soup = BeautifulSoup(response.text)
                    for link in soup.find_all('link'):

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
                                        pdf_d, p_text = pdf_file_to_parse_d(retrieval_df, index, f'./output/formats/pdfs/{index}.pdf', ftp_link, keep_abstract)           
                                        if pdf_d['Content_type'] == 'pdf' and pdf_d['wc'] != 0 and (pdf_d['wc_abs'] < pdf_d['wc'] or pdf_d['wc_abs'] > 1000 if pdf_d['wc_abs'] != 0 else True) and 100 < pdf_d['wc']:
                                            retrieval_df.loc[index, 'pdf'] = 1
                                            retrieval_df.loc[index,'pdf_parse_d'].update(pdf_d)
                                            f = open(f"./output/retrieved_parsed_files/pdfs/{index}.txt", "w")
                                            f.write(p_text)
                                            f.close()

                                        else:
                                            pass
                                        if 'wc' in row['pdf_parse_d'].keys():
                                            pass
                                        else:
                                            retrieval_df.loc[index, 'pdf'] = int(0)
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
            if retrieval_df.pmc_tgz.loc[index] != 1 and retrieval_df.pmcid.loc[index] != None:
                try:
                    #creating the header and protocol to request the tgz from PMC
                    response_d, response = get_request(pmcid, http, base_url, headers, 'pmctgz')
                except:
                    pass
                #stop the process in case of status code 429
                if response_d['status_code'] == 429:
                    print('"Too many requests error [429]" received')
                    print('Risk of IP address block: stopping script')
                    exit()
                #if status code 200 means we can process the document
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
                            out_file = f'./output/formats/tgzs/{index}.tgz'
                            try:
                                # we had previous experience where the code got stuck in the tgz, we set the time to maximun 300s before moving to the next records without changing the main df
                                timeout_time = 300 
                                start = time.time()
                                worked = False
                                #creating one process to kill it once the time is passed or when it's completed
                                pnum = 1
                                procs = []
                                for i in range(pnum):
                                    #downloading the tgz using the newly created process that will die at most 300s from the start
                                    p = Process(target=wget.download, args=(ftp_link, out_file), name = ('process_' + str(i+1)))
                                    procs.append(p)
                                    p.start()
                                #as long as when we started is less than 300s continue to try
                                while time.time() - start <= timeout_time:
                                    #checking if it's already completed or not, if yes stop and moving to next record
                                    if not any([p.is_alive() for p in procs]):
                                        # All the processes are done, break now.
                                        #Bolean to keep the fact that it worked
                                        worked = True
                                        #altering the main df
                                        retrieval_df.loc[index, 'pmc_tgz'] = 1
                                        #kill the process and merging the result
                                        p.terminate()
                                        p.join()
                                        break
                                    #only check if it's over every one second
                                    time.sleep(1)  # just to avoid bothering the CPU
                                else:
                                    # We only enter this if we didn't 'break' above.
                                    print("timed out, killing all processes")
                                    for p in procs:
                                        p.terminate()
                                        p.join()
                            except:
                                pass
                            # run the function to unpack the tgz looking for pdfs and xmls in case the tgz was sucessful
                            if worked == True:
                                try:
                                    #again using a timeout function to not get stuck in the tgz
                                    retrieval_df = timeout(300)(tgz_unpacking)(index, retrieval_df, f'./output/formats/tgzs/{index}.tgz', ftp_link, keep_abstract)
                                except:
                                    pass #handle errors                           
                        else:
                            pass

                # alternative error code, register the fail but keep going.     
                else:
                    print('error with request')
                    print(f'{response_d["error"]}')    
                    pass
            else:
                pass
            
        elif stage == 'doiorg':
            #cheking if the doi is not nan
            if retrieval_df.doi.loc[index] != None:
                try:
                    #creating the header and the protocol
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

                            # execute if we have identify pdf as a format
                            if 'pdf' in format_type.lower() and retrieval_df.pdf.loc[index] != 1:
                                if response_d['headers'].get('Content-Type') != None: 
                                    #the document retreived is the format we expected
                                    if response_d['headers']['Content-Type'] == 'application/pdf':
                                        with open(f'./output/formats/pdfs/{index}.pdf', 'wb') as file:
                                            file.write(response_d['content'])
                                        try:
                                            pdf_d, p_text = pdf_file_to_parse_d(retrieval_df, index, f'./output/formats/pdfs/{index}.pdf', f'{base_url}{doi}', keep_abstract)
                                            if pdf_d['Content_type'] == 'pdf' and pdf_d['wc'] != 0 and (pdf_d['wc_abs'] < pdf_d['wc'] or pdf_d['wc_abs'] > 1000 if pdf_d['wc_abs'] != 0 else True) and 100 < pdf_d['wc']:
                                                #if the content retreived from the docuemnt followed the rule we implemented we are altering the main df
                                                retrieval_df.loc[index, 'pdf'] = 1
                                                retrieval_df.loc[index,'pdf_parse_d'].update(pdf_d)
                                                f = open(f"./output/retrieved_parsed_files/pdfs/{index}.txt", "w")
                                                f.write(p_text)
                                                f.close()

                                            else:
                                                pass
                                            if 'wc' in row['pdf_parse_d'].keys():
                                                pass
                                            else:
                                                retrieval_df.loc[index, 'pdf'] = int(0)
                                        except:
                                            pass
                                    else:
                                        pass
                                else:
                                    pass
                            
                            elif 'xml' in format_type.lower() and retrieval_df.xml.loc[index] != 1:
                                # perform xml parsing and FP detection
                                xml_d, p_text = xml_response_to_parse_d(retrieval_df, index, response, keep_abstract)
                                xml_d = evaluation_funct(xml_d)
                                # now that we have the xml_d we can decide if it is a TP, FP or AB 
                                if xml_d['evaluation'] == 'TP' and (xml_d['wc_abs'] < xml_d['wc'] or xml_d['wc_abs'] > 1000 if xml_d['wc_abs'] != 0 else True) and 100 < xml_d['wc']:
                                    with open(f'./output/formats/xmls/{index}.xml', 'w') as file:
                                            file.write(response_d['text'].encode('ascii', 'ignore').decode())
                                    retrieval_df.loc[index,'xml'] = 1
                                    retrieval_df.loc[index,'xml_parse_d'].update(xml_d)
                                    f = open(f"./output/retrieved_parsed_files/xmls/{index}.txt", "w")
                                    f.write(p_text)
                                    f.close()
                                if 'wc' in row['xml_parse_d'].keys():
                                    pass
                                else:
                                    retrieval_df.loc[index, 'xml'] = int(0)



                            elif 'html' in format_type.lower() and retrieval_df.html.loc[index] != 1:
                                # all the htmls should be checked for links regardless of whether they are FP or AB
                                html_links = complete_html_link_parser(response)
                                if len(html_links) != 0:
                                    full_text_link_dict = retrieval_df.loc[index, 'full_text_links']
                                    full_text_link_dict.update({'html_parse':html_links})
                                    retrieval_df.at[index, 'full_text_links'] = full_text_link_dict
                            
                                # perform html parsing and FP detection
                                html_d, p_text = html_response_to_parse_d(retrieval_df, index, response, keep_abstract)
                                html_d = evaluation_funct(html_d)
                                # now we have the html_d we can compare to decide if it is a TP, FP or AB 
                                if html_d['evaluation'] == 'TP' and (html_d['wc_abs'] < html_d['wc'] or html_d['wc_abs'] > 1000 if html_d['wc_abs'] != 0 else True) and 100 < html_d['wc']:
                                    with open(f'./output/formats/htmls/{index}.html', 'w') as file:
                                            file.write(response_d['text'].encode('ascii', 'ignore').decode())
                                    retrieval_df.loc[index,'html'] = 1
                                    retrieval_df.loc[index,'html_parse_d'].update(html_d)
                                    f = open(f"./output/retrieved_parsed_files/htmls/{index}.txt", "w")
                                    f.write(p_text)
                                    f.close()
                                if 'wc' in row['html_parse_d'].keys():
                                    pass
                                else:
                                    retrieval_df.loc[index, 'html'] = int(0)

                        
                            elif 'plain' in format_type.lower() and retrieval_df.plain.loc[index] != 1:
                                with open(f'./output/formats/txts/{index}.txt', 'w') as file:
                                    file.write(response_d['text'].encode('ascii', 'ignore').decode())
                                plain_d, p_text = plain_file_to_parse_d(retrieval_df, index, f'./output/formats/txts/{index}.txt', f'{base_url}{doi}', keep_abstract)
                                if plain_d['wc'] != 0 and (plain_d['wc_abs'] < plain_d['wc'] or plain_d['wc_abs'] > 1000 if plain_d['wc_abs'] != 0 else True) and 100 < plain_d['wc']:
                                    retrieval_df.loc[index,'plain_parse_d'].update(plain_d)
                                    retrieval_df.loc[index,'plain'] = 1 
                                    f = open(f"./output/retrieved_parsed_files/txts/{index}.txt", "w")
                                    f.write(p_text)
                                    f.close()
                                if 'wc' in row['plain_parse_d'].keys():
                                    pass
                                else:
                                    retrieval_df.loc[index, 'plain'] = int(0)

                                
                                                

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
        # we don't need to save the page, just parse the request.text and save the links to the retrieved df
        # no html page are saved at this stage only candidate links
        elif stage == 'pubmed':
            # firstly check that there is a PMID to use (is equal to itself)
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
            #clearing the terminal output every 10 records, showing on top of the terminal the information in case of failure 
            #resting 2 seconds every 10 records to be polite 
            sleep(2)
            clear()
            print(f'In case of faillure please put the parameters start="{saved_stage}" (or "{saved_stage}_only" if in only mode) and idx="{saved_index}"')
            print('\n') 
        elif counter%100 == 0 and not counter == 0:
            #saving the main df every 100 records, updating the information on the top in case of failure
            #resting 2 seconds to be polite
            sleep(2)
            clear()
            saved_stage = stage
            saved_index = index
            if done is None:
                retrieval_df.pub_date = retrieval_df.pub_date.astype(str)
                result = retrieval_df.to_json(orient="index")
                json_object = json.dumps(result, indent=4)
                with open(f"./output/retrieved_df/retrieved_df.json", "w") as outfile:
                    outfile.write(json_object)
                outfile.close()
            else:
                saved_processed_df = pd.concat([done, retrieval_df], axis=0, join='outer', ignore_index=False, copy=True)
                saved_processed_df.pub_date = saved_processed_df.pub_date.astype(str)
                result = saved_processed_df.to_json(orient="index")
                json_object = json.dumps(result, indent=4)
                with open(f"./output/retrieved_df/retrieved_df.json", "w") as outfile:
                    outfile.write(json_object)
                outfile.close()
            print(f'In case of fa illure please put the parameters start="{saved_stage}" (or "{saved_stage}_only" if in only mode) and idx="{saved_index}"')
            print('\n')

    #When all the the rows have been completed saving the main df and the information of the current stage   
    print('process Complete')
    if done is None:
        retrieval_df.pub_date = retrieval_df.pub_date.astype(str)
        result = retrieval_df.to_json(orient="index")
        json_object = json.dumps(result, indent=4)
        with open(f"./output/retrieved_df/retrieved_df.json", "w") as outfile:
            outfile.write(json_object)
        outfile.close()
    else:
        saved_processed_df = pd.concat([done, retrieval_df], axis=0, join='outer', ignore_index=False, copy=True)
        saved_processed_df.pub_date = saved_processed_df.pub_date.astype(str)
        result = saved_processed_df.to_json(orient="index")
        json_object = json.dumps(result, indent=4)
        with open(f"./output/retrieved_df/retrieved_df.json", "w") as outfile:
            outfile.write(json_object)
        outfile.close()

    return retrieval_df
