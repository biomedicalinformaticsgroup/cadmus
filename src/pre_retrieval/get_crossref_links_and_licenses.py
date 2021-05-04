from cadmus.src.retrieval import get_request
from cadmus.src.retrieval import get_tdm_links
import json
import pickle

# use this function when we already have a master_df with indexes and all available ids
def get_crossref_links_and_licenses(master_df, http, base_url, headers):
    
    # we send the doi to the crossref API server as a GET request using the function defined above
    # lets simplify the master_df to only have rows with dois available
    condition = [(type(doi) != float) for doi in master_df.doi]
    cr_df = master_df[condition]
    
    count = 0
    for index, row in cr_df.iterrows():
        count +=1
        
        # send the request using our function
        response_d, response = get_request(row['doi'], http, base_url, headers, 'base')

        # check the status code
        if response_d['status_code'] == 200:
            # if its good then read the json response from the r.text
            response_json = json.loads(response_d['text'])
            
            # dump a pickle of the response saved as the index
            pickle.dump(response_json, open(f'./output/crossref/p/{index}.p', 'wb'))
            master_df.loc[index, 'crossref'] = 1
            
            message = response_json['message']
            
            #lets start parsing out the key variables we want from the metadata                
            licenses = message.get('license')
            # now the full text links
            link_list = message.get('link')
            links = get_tdm_links(link_list)
            if links is not None:
                # set the tdm links into the master_df fulltext links dict
                full_text_links_dict = master_df.loc[index, 'full_text_links']
                full_text_links_dict.update({'cr_tdm':links})
                master_df.at[index, 'full_text_links'] = full_text_links_dict
            else:
                print('crossref record found but no TDM links supplied')
                pass
            # set the licenses into the master_df as well
            master_df.at[index, 'licenses'] = licenses
            
            
        else:
            # when the response is not 200, then the record is not known in crossref.
            pass

        # keep a note of progress in cell output
        if count%50 == 0:
            print(f'{count} out of {len(cr_df)}')
    
    # run a quick evaluation of the tdm link haul
    count = 0
    for index, row in master_df.iterrows():
        if row['full_text_links'].get('cr_tdm') != []:
            count+=1
    print(f'Out of the {len(cr_df)} articles with a doi, {sum(master_df.crossref ==1)} were found in crossref')
    print(f'We have found {count} crossref records with at least one TDM link available')
    return master_df