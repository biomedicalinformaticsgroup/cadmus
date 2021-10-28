from cadmus.parsing.xml_clean_soup import xml_clean_soup
from cadmus.parsing.xml_body_p_parse import xml_body_p_parse
from cadmus.parsing.get_ab import get_ab
from cadmus.evaluation.abstract_similarity_score import abstract_similarity_score
from cadmus.evaluation.body_unique_score import body_unique_score
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings("ignore")

def xml_response_to_parse_d(retrieval_df, index, xml_response):
    parse_d = {}
    soup = BeautifulSoup(xml_response.text, features = 'lxml')
    # remove unwanted tags
    soup = xml_clean_soup(soup)
    # check for abstract in retrieved_df
    if retrieval_df.loc[index, 'abstract'] != '' and retrieval_df.loc[index, 'abstract'] != None and retrieval_df.loc[index, 'abstract'] == retrieval_df.loc[index, 'abstract']:
        ab = retrieval_df.loc[index, 'abstract']
    else:    
        # try parse the abstract
        ab = get_ab(soup)
    # try parse the text
    p_text = xml_body_p_parse(soup, ab)
    # get the file_size
    size = len(xml_response.content)
    # get the word_count
    wc = len(p_text.split())
    
    bu_score = body_unique_score(p_text, ab)
    as_score = abstract_similarity_score(p_text, ab)
    

    # use the output from each function to build a output dictionary to use for our evaluation
    parse_d.update({'file_path':f'./output/formats/xmls/{index}.xml',
                    'text':p_text,
                    'abstract':ab,
                    'size':size,
                    'wc':wc,
                    'url':xml_response.url,
                    'body_unique_score':bu_score,
                    'ab_sim_score':as_score})
    
    if retrieval_df.loc[index, 'abstract'] == '' or retrieval_df.loc[index, 'abstract'] == None or retrieval_df.loc[index, 'abstract'] != retrieval_df.loc[index, 'abstract']:
        retrieval_df.loc[index, 'abstract'] = ab
    else:
        pass
    
    return parse_d