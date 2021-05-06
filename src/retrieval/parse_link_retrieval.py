from cadmus.src.retrieval import HTTP_setup
from cadmus.src.retrieval import get_request
from cadmus.src.parsing import doctype
from cadmus.src.parsing import xml_response_to_parse_d
from cadmus.src.evaluation import evaluation_funct
from cadmus.src.retrieval import complete_html_link_parser
from cadmus.src.parsing.html_response_to_parse_d import html_response_to_parse_d
from cadmus.src.parsing.pdf_file_to_parse_d import pdf_file_to_parse_d
from cadmus.src.parsing import plain_file_to_parse_d
from cadmus.src.retrieval import clear
import bs4
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings("ignore")
from time import sleep
import pickle

# once we get to this stage we have tried quite a few approaches to get a full text document for each article.
# we can pull out the records that do not have a tagged version and a pdf version to keep trying for.
# we will now go through the dataframe and sequentially try the untried links in the full_text_links dictionary.
def parse_link_retrieval(retrieval_df, email, click_through_api_key):
    counter = -0
    stage = 'retrieved2'
    for index, row in retrieval_df.iterrows():
        if counter == 0:
            clear()
            print(f'In case of faillure please put the parameters start="{stage}" (or "{stage}_only" if in only mode) and idx="{index}"') 
            saved_stage = stage
            saved_index = index   
            print('\n')
        counter += 1
        print(f'Processing row number {counter} out of {len(retrieval_df)}')
        # check for a tagged version (HTML or XML) and a PDF version. If both criteria met, then move on.
        pdf = row['pdf']
        xml = row['xml']
        html = row['html']
        # first check the criteria for further checking
        if xml == 1 or html == 1:
            if pdf == 1 :
                # we'll create while loop to iterate through all available links 
                criteria = True
            else:
                criteria = False
        else:
            criteria = False
            
        

        count = 0

        # now we will work through all the available links to try and fill in the missing formats for each record
        full_text_links_d = row['full_text_links']
        # build a list of links to try
        link_list = []
        for key in ['html_parse', 'pubmed_links']:
            link_list.extend(full_text_links_d.get(key))
        print(f'{len(link_list)} links found to try get full text for')

        # now we have a list to try
        # we'll use a counter to keep track of how many we need to try
            
        for link in link_list:
            if criteria == True:
                break
            else:
                pass
            count +=1
            # we need to send each link in a get request to determine the response format type.
            # we can use the same settings as the doi.org step but provide an empty base_url for input along with the link
            try:
                http, base_url, headers= HTTP_setup(email, click_through_api_key, 'doiorg')
            except:
                pass

            # we send the request using our generic function
            try:
                response_d, response = get_request(link, http, '', headers, 'doiorg')
            except:
                pass

            # check the response status
            if response_d['status_code'] == 429:
                print('"Too many requests error [429]" received')
                print('Risk of IP address block: stopping script')
                exit()

            # if the response is 200 and of a decent byte size then we should look for a format
            elif (response_d['status_code'] == 200):
                # rule of thumb if content less than 10000 bytes, it is rubbish
                if (len(response_d['content']) > 10000):

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
                    else:
                        pass
                        # give some feedback about fomats detected
                    print(f'Format:\"{format_type}\" found')

                    # now we look for the format and check if it is already retrieved
                    # execute if we have a set format
                    if 'pdf' in format_type and retrieval_df.pdf.loc[index] != 1:
                        with open(f'./output/formats/pdfs/{index}.pdf', 'wb') as file:
                                file.write(response_d['content'])
                        try:
                            pdf_d = pdf_file_to_parse_d(retrieval_df, index, f'./output/formats/pdfs/{index}.pdf', link)
                            if pdf_d['Content_type'] == 'pdf' and pdf_d['text'] != '' and (len(pdf_d['abstract'].split()) < pdf_d['wc'] or len(pdf_d['abstract'].split()) > 1000 if pdf_d['abstract'] != None else True) and 100 < pdf_d['wc']:
                                retrieval_df.loc[index,'pdf'] = 1
                                retrieval_df.loc[index, 'pdf_parse_d'] = [pdf_d]
                                pdf = 1
                            else:
                                pass 
                        except:
                            pass
                        else:
                            pass

                    elif 'xml' in format_type and retrieval_df.xml.loc[index] != 1:
                        # perform xml parsing and FP detection
                        xml_d = xml_response_to_parse_d(retrieval_df, index, response)
                        xml_d = evaluation_funct(xml_d)
                        # now we have the xml_d we can compare look at the parsed text to decide if it is a TP, FP or AB class
                        if xml_d['evaluation'] == 'TP' and (len(xml_d['abstract'].split()) < xml_d['wc'] or len(xml_d['abstract'].split()) > 1000 if xml_d['abstract'] != None else True) and 100 < xml_d['wc']:
                            with open(f'./output/formats/xmls/{index}.xml', 'w') as file:
                                file.write(response_d['text'].encode('ascii', 'ignore').decode())
                            retrieval_df.loc[index,'xml'] = 1
                            retrieval_df.loc[index,'xml_parse_d'] = [xml_d]
                            xml = 1

                    elif 'html' in format_type and retrieval_df.html.loc[index] != 1:

                        # this may be a new html doc and thus should be parsed for more links (like pdf etc)
                        if row['full_text_links'].get('html_parse') == []:
                            # all the htmls should be checked for links regardless of whether they are FT or ABd
                            html_links = complete_html_link_parser(response)
                            if len(html_links) != 0:
                                full_text_link_dict = retrieval_df.loc[index, 'full_text_links']
                                full_text_link_dict.update({'html_parse':html_links})
                                retrieval_df.at[index, 'full_text_links'] = full_text_link_dict
                                link_list.extend([link for link in html_links if link not in link_list])

                        # perform html parsing and FP detection
                        html_d = html_response_to_parse_d(retrieval_df, index, response)
                        html_d = evaluation_funct(html_d)
                        # now we have the xml_d we can compare look at the parsed text to decide if it is a TP, FP or AB class
                        if html_d['evaluation'] == 'TP' and (len(html_d['abstract'].split()) < html_d['wc'] or len(html_d['abstract'].split()) > 1000 if html_d['abstract'] != None else True) and 100 < html_d['wc']:
                            with open(f'./output/formats/htmls/{index}.html', 'w') as file:
                                    file.write(response_d['text'].encode('ascii', 'ignore').decode())
                            retrieval_df.loc[index,'html'] = 1
                            retrieval_df.loc[index,'html_parse_d'] = [html_d]
                            html = 1

                    elif 'plain' in format_type and retrieval_df.plain.loc[index] != 1:
                        with open(f'./output/formats/txts/{index}.txt', 'w') as file:
                            file.write(response_d['text'].encode('ascii', 'ignore').decode())
                        plain_d = plain_file_to_parse_d(retrieval_df, index, f'./output/formats/txts/{index}.txt', link)
                        if plain_d['text'] != '' and (len(plain_d['abstract'].split()) < plain_d['wc'] or len(plain_d['abstract'].split()) > 1000 if plain_d['abstract'] != None else True) and 100 < plain_d['wc']:
                            retrieval_df.loc[index, 'plain_parse_d'] = [plain_d]
                            retrieval_df.loc[index,'plain'] = 1

                    else:
                        # unknown format found
                        pass
                else:
                    # the response is too short to consider (most likely a redirect)
                    pass
            else:
                # other status code for our request we need to move on.
                pass

            # after every link we need to check the criteria for trying more.                    
            # at the end of each link attmpt we should check if the criteria has been met or we have ran out of links so that we minimize the number of requests made
            if xml == 1 or html == 1:
                if pdf == 1:
                    criteria = True
                    print('all formats retrieved')
                    print('\n')
                    break
            elif count == len(link_list):
                criteria = True
                print('No More links to try')
                print('\n')
            else:
                pass
                    
        print('moving on to next record')
        print('\n')
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
            pickle.dump(retrieval_df, open(f'./output/retrieved_df/retrieved_df.p', 'wb'))
            print(f'In case of faillure please put the parameters start="{saved_stage}" (or "{saved_stage}_only" if in only mode) and idx="{saved_index}"')
            print('\n') 
            
    print('process Complete')
    pickle.dump(retrieval_df, open(f'./output/retrieved_df/retrieved_df.p', 'wb'))
    return retrieval_df