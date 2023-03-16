from cadmus.parsing.clean_soup import clean_soup
from cadmus.parsing.xml_body_p_parse import xml_body_p_parse
from cadmus.parsing.pdf_file_to_parse_d import pdf_file_to_parse_d
from cadmus.parsing.get_ab import get_ab
from cadmus.evaluation.abstract_similarity_score import abstract_similarity_score
from cadmus.evaluation.body_unique_score import body_unique_score
from cadmus.evaluation.evaluation_funct import evaluation_funct
import os
import tarfile
from pathlib import Path
import bs4
from bs4 import BeautifulSoup
import lxml
import shutil
import time
import zipfile

def tgz_unpacking(index, retrieval_df, tgz_path, ftp_link, keep_abstract):

    condition = False
    start = time.time()
    # creating a condition to not exceed 5 minutes, usually that's when the machine is stuck in a tgz file
    while time.time() - start <= 300 and condition == False:
        try:
            try:
                os.mkdir('./output/formats/tgzs/temp_dir')   
            except:
                pass
            
            # read the tgz into a python object
            tgz = tarfile.open(tgz_path)
            # unpack the tgz into the temp dir named after the index
            tgz.extractall(f'./output/formats/tgzs/temp_dir/{index}')
            
            # unpacking the tgz automatically names all the the files which we will want to redefine according to our index
            # iterate through each file in the directory looking for the file name with PMC 
            for file in Path(f'./output/formats/tgzs/temp_dir/{index}').iterdir():
                if 'PMC' in file.name:
                    pmc = file.name 
            
            # first we'll check if the pdf is required or already downloaded.
            if retrieval_df.at[index, 'pdf'] != 1:
                
                # set default to none
                pdf_path = None

                # most of the time there is only one pdf provided which will be the main pdf. Sometimes there are more than one.
                # first make a list of all the pdf file paths
                pdfs = [path for path in Path(f'./output/formats/tgzs/temp_dir/{index}/{pmc}').iterdir() if path.suffix == '.pdf']
                
                # whern there is only one pdf then assume that is the main pdf
                if len(pdfs) == 1:
                    pdf_path = pdfs[0]
                # otherwise it will most often be name main.pdf
                elif len(pdfs) > 1:
                    for path in pdfs:
                        if path.name == 'main.pdf':
                            pdf_path = path
                else:
                    print('No PDF found in the tgz')
                    condition = True
                
                
                if pdf_path:
                    
                    # perform pdf evaluation and build a parse_d 
                    
                    # parse
                    
                    # build URL (PMC_open access url with PMCID on the end)
                    
                    # evaluate the pdf using the evaluation function ab_sim_score, bd_score, wc, file_size, text, abstract, evaluation, 
                    
                    # if the pdf is TP then save to file under the index - save as path on parse_d
                    to_file = Path(f'./output/formats/pdfs/{index}.pdf')
                    print(' Main PDF found = writing to file')
                    pdf_path.rename(to_file)
                    try:
                        pdf_d, p_text = pdf_file_to_parse_d(retrieval_df, index, f'./output/formats/pdfs/{index}.pdf', ftp_link, keep_abstract)
                        if pdf_d['Content_type'] == 'pdf' and p_text != '' and (pdf_d['wc_abs'] < pdf_d['wc'] or pdf_d['wc_abs'] > 1000 if pdf_d['wc_abs'] != 0 else True) and 100 < pdf_d['wc']:
                            zipfile.ZipFile(f'./output/formats/pdfs/{index}.pdf.zip', mode='w').write(f'./output/formats/pdfs/{index}.pdf', arcname=f'{index}.pdf')
                            os.remove(to_file)
                            retrieval_df.loc[index, 'pdf'] = 1
                            retrieval_df.loc[index, 'pdf_parse_d'].update(pdf_d)
                            with zipfile.ZipFile(f"./output/retrieved_parsed_files/pdfs/{index}.txt.zip", mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zip_file:
                                zip_file.writestr(f"{index}.txt", data=p_text)
                                zip_file.testzip()
                            zip_file.close()
                            condition = True
                        else:
                            # no need to spend more time in the tgz the function could not identify the file we are looking for
                            condition = True
                            os.remove(to_file)
                            pass
                    except:
                        # no need to spend more time in the tgz the function could not identify the file we are looking for
                        os.remove(to_file)
                        condition = True
                        pass
                else:
                    # no need to spend more time in the tgz the function could not identify the file we are looking for
                    condition = True
            else:
                # no pdf required, move on to the xml extraction
                condition = True
                pass
            
            
            # now lets look for the nxmls
            if retrieval_df.at[index, 'xml'] != 1:

                # most of the time there is only one pdf provided which will be the main pdf. Sometimes there are more than one.
                # first make a list of all the pdf file paths
                xmls = [path for path in Path(f'./output/formats/tgzs/temp_dir/{index}/{pmc}').iterdir() if (path.suffix == '.nxml') or (path.suffix == '.xml')]
                
                # lets loop through each xml path and try extract the full text
                for xml in xmls:
                    # check to see if the xml is needed
                    if retrieval_df.at[index, 'xml'] != 1:
                        # set the parse_d as empty
                        parse_d = {}
                        # read in the xml from the path
                        with open(str(xml), 'r') as xml_file:
                            # create a soup object
                            soup = BeautifulSoup(xml_file, 'lxml')
                            # remove unwanted tags
                            soup = clean_soup(soup)
                            # check for abstract in retrieved_df
                            if retrieval_df.loc[index, 'abstract'] != '' and retrieval_df.loc[index, 'abstract'] != None and retrieval_df.loc[index, 'abstract'] != retrieval_df.loc[index, 'abstract']:
                                ab = retrieval_df.loc[index, 'abstract']
                            else:    
                                # try parse the abstract
                                ab = get_ab(soup)
                            # try parse the text
                            p_text = xml_body_p_parse(soup, ab, keep_abstract)
                            # get the file_size
                            size = xml.stat().st_size
                            # get the word_count
                            wc = len(p_text.split())
                            if ab != None:
                                wc_abs = len(ab.split())
                            else:
                                wc_abs = 0

                            bu_score = body_unique_score(p_text, ab)
                            as_score = abstract_similarity_score(p_text, ab)
                            
                            # get the pmcid for the url 
                            pmcid = retrieval_df.at[index, "pmcid"]

                            # use the output from each function to build a output dictionary to use for our evaluation
                            parse_d.update({'file_path':f'./output/formats/xmls/{index}.xml.zip',
                                            'size':size,
                                            'wc':wc,
                                            'wc_abs': wc_abs,
                                            'url':f'https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id={pmcid}&format=',
                                            'body_unique_score':bu_score,
                                            'ab_sim_score':as_score})
                            
                            
                            parse_d = evaluation_funct(parse_d)
                            
                            if parse_d['evaluation'] == 'TP' and (parse_d['wc_abs'] < parse_d['wc'] or parse_d['wc_abs'] > 1000 if parse_d['wc_abs'] != 0 else True) and 100 < parse_d['wc']:
                                to_file = Path(f'./output/formats/xmls/{index}.xml')
                                print('XML found = writing to file')
                                xml.rename(to_file)
                                zipfile.ZipFile(f'./output/formats/xmls/{index}.xml.zip', mode='w').write(f'./output/formats/xmls/{index}.xml', arcname=f'{index}.xml')
                                # then record success on the retrieved_df
                                retrieval_df.loc[index,'xml'] = 1
                                retrieval_df.loc[index,'xml_parse_d'] = parse_d
                                with zipfile.ZipFile(f"./output/retrieved_parsed_files/xmls/{index}.txt.zip", mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zip_file:
                                    zip_file.writestr(f"{index}.txt", data=p_text)
                                    zip_file.testzip()
                                zip_file.close()
                                os.remove(to_file)
                                condition = True
                            else:
                                # no need to spend more time in the tgz the function could not identify the file we are looking for
                                condition = True
                            if 'wc' in retrieval_df.loc[index, 'xml_parse_d'].keys():
                                pass
                            else:
                                retrieval_df.loc[index, 'xml'] = int(0)

                    else:
                        # no need to spend more time in the tgz the function could not identify the file we are looking for
                        condition = True
            else:
                # no need to spend more time in the tgz the function could not identify the file we are looking for
                condition = True
                                                        
            # delete the temp dir
            shutil.rmtree('./output/formats/tgzs/temp_dir')
        except:
            condition = True
            pass
    if time.time() - start <= 300 and condition == True:   
        return retrieval_df
    else:
        pass
