from cadmus.parsing.structured_plain_text import structured_plain_text
from cadmus.parsing.unstructured_plain_text import unstructured_plain_text
from cadmus.parsing.get_abstract_txt import get_abstract_txt
from cadmus.evaluation.abstract_similarity_score import abstract_similarity_score
from cadmus.evaluation.body_unique_score import body_unique_score
import os

def plain_file_to_parse_d(retrieval_df, index, path_document, ftp_link, keep_abstract):
    parse_d = {}
    with open(f'./output/formats/txts/{index}.txt', 'r') as text:
        p_text = text.read()
    # check for abstract in retrieved_df
    if retrieval_df.loc[index, 'abstract'] != '' and retrieval_df.loc[index, 'abstract'] != None and retrieval_df.loc[index, 'abstract'] == retrieval_df.loc[index, 'abstract']:
        ab = retrieval_df.loc[index, 'abstract']
    else:    
        # try parse the abstract in case not provided by PubMed
        ab = get_abstract_txt(p_text)
    # different parsing algorithms depending the abstract is provided or not
    if ab != '':
        p_text = structured_plain_text(p_text, ab, keep_abstract)
    else:
        p_text = unstructured_plain_text(p_text, keep_abstract)

    # get the file_size
    size = os.stat(path_document).st_size
    # get the word_count
    wc = len(p_text.split())
    if ab != '' and ab != None: 
        wc_abs = len(ab.split())
    else:
        wc_abs = 0
    # computing the abs_score and body_unique
    bu_score = body_unique_score(p_text, ab)
    as_score = abstract_similarity_score(p_text, ab)


    # use the output from each function to build a output dictionary to use for our evaluation and saving the content if it's a true positive
    parse_d.update({'file_path':f'./output/formats/txts/{index}.txt',
                    'size':size,
                    'wc':wc,
                    'wc_abs': wc_abs,
                    'url': ftp_link,
                    'body_unique_score':bu_score,
                    'ab_sim_score':as_score})   
    
    return parse_d, p_text