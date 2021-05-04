from cadmus.src.parsing.clean_pdf_body import clean_pdf_body
from cadmus.src.parsing.limit_body import limit_body
from cadmus.src.parsing.get_abstract_pdf import get_abstract_pdf
from cadmus.src.evaluation.abstract_similarity_score import abstract_similarity_score
from cadmus.src.evaluation.body_unique_score import body_unique_score
import os
import tika
os.environ['TIKA_SERVER_JAR'] = 'https://repo1.maven.org/maven2/org/apache/tika/tika-server/'+tika.__version__+'/tika-server-'+tika.__version__+'.jar'
from tika import parser

def pdf_file_to_parse_d(retrieval_df, index, path_document, ftp_link):
    parse_d = {}
    # load pdf into tika 
    soup = parser.from_file(path_document)
    if soup['metadata']['Content-Type'] != 'application/pdf':
        Content_type = 'error'
        parse_d.update({'Content_type':Content_type})
        
    else:
    
        # try parse the text
        p_text = soup['content']
        if type(p_text) != str or p_text == '': 
            p_text = ''
            Content_type = 'error'
            parse_d.update({'Content_type':Content_type})
        else: 
            p_text = clean_pdf_body(p_text)
            p_text = limit_body(p_text)

        # check for abstract in master_df
        if retrieval_df.loc[index, 'abstract'] != '' and retrieval_df.loc[index, 'abstract'] != None and retrieval_df.loc[index, 'abstract'] == retrieval_df.loc[index, 'abstract']:
            ab = retrieval_df.loc[index, 'abstract']

        else:    
            # try parse the abstract
            ab = get_abstract_pdf(p_text)


        # get the file_size
        size = os.stat(path_document).st_size
        # get the word_count
        wc = len(p_text.split())
        Content_type = 'pdf'

        if 'Creation-Date' in soup['metadata'].keys():
            date = soup['metadata']['Creation-Date']
        elif 'date' in soup['metadata'].keys():
            date = soup['metadata']['date']
        else:
            date = None

        bu_score = body_unique_score(p_text, ab)
        as_score = abstract_similarity_score(p_text, ab)


        # use the output from each function to build a output dictionary to use for our evaluation
        parse_d.update({'file_path':f'./output/formats/pdfs/{index}.pdf',
                        'text':p_text,
                        'abstract':ab,
                        'date': date,
                        'size':size,
                        'wc':wc,
                        'Content_type':Content_type, 
                        'url': ftp_link,
                        'body_unique_score':bu_score,
                        'ab_sim_score':as_score})

        if retrieval_df.loc[index, 'abstract'] == '' or retrieval_df.loc[index, 'abstract'] == None or retrieval_df.loc[index, 'abstract'] != retrieval_df.loc[index, 'abstract']:
            retrieval_df.loc[index, 'abstract'] = ab
        else:
            pass

        ####### TO ADD change the date if not the right format 
    
    
    return parse_d