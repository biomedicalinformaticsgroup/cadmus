from cadmus.parsing.xml_clean_soup import xml_clean_soup
from cadmus.parsing.xml_body_p_parse import xml_body_p_parse
from cadmus.parsing.get_ab import get_ab
from cadmus.evaluation.abstract_similarity_score import abstract_similarity_score
from cadmus.evaluation.body_unique_score import body_unique_score
from cadmus.parsing.clean_xml import clean_xml
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings("ignore")

def xml_response_to_parse_d(retrieval_df, index, xml_response, keep_abstract):
    parse_d = {}
    soup = BeautifulSoup(xml_response.text, features = 'lxml')
    # remove unwanted tags
    soup = xml_clean_soup(soup)
    # check for abstract in retrieved_df
    if retrieval_df.loc[index, 'abstract'] != '' and retrieval_df.loc[index, 'abstract'] != None and retrieval_df.loc[index, 'abstract'] == retrieval_df.loc[index, 'abstract']:
        ab = retrieval_df.loc[index, 'abstract']
    else:    
        # try parse the abstract since not provided by PubMed
        ab = get_ab(soup)
    # try parse the text
    p_text = xml_body_p_parse(soup, ab, keep_abstract)
    p_text = clean_xml(p_text)
    # get the file_size
    size = len(xml_response.content)
    # get the word_count
    wc = len(p_text.split())
    if ab != '' and ab != None: 
        wc_abs = len(ab.split())
    else:
        wc_abs = 0
    #compute the score for evaluation 
    bu_score = body_unique_score(p_text, ab)
    as_score = abstract_similarity_score(p_text, ab)
    

    # use the output from each function to build a output dictionary to use for our evaluation
    parse_d.update({'file_path':f'./output/formats/xmls/{index}.xml',
                    'size':size,
                    'wc':wc,
                    'wc_abs': wc_abs,
                    'url':xml_response.url,
                    'body_unique_score':bu_score,
                    'ab_sim_score':as_score})
    
    return parse_d, p_text