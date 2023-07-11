import json
import pandas as pd
import subprocess
import zipfile
import glob
import os

def add_keywords(df):

    #retrieving the names of the file present in the medline file to extract previously fectched mesh terms
    command = subprocess.getstatusoutput(f"ls -lR ./output/medline/txts")
    command = list(command)
    command = command[1]
    command = str(command).split('\n')
    my_medline_files = []
    for i in range(2,len(command)):
        my_medline_files.append(command[i].split()[-1])

    total_list = []
    for i in range(len(my_medline_files)):
        my_file = ''
        with zipfile.ZipFile(f"./output/medline/txts/{my_medline_files[i]}", "r") as z:
            for filename in z.namelist():
                with z.open(filename) as f:
                    my_file = f.read()
                f.close()
        z.close()
        total_list.append(str(str(my_file.decode('utf-8'))))

    total_list = total_list[0].split('\n')
    
    my_pmid_filtered = []
    my_kw_filtered = []
    current_kw = []
    current = False
    for i in range(len(total_list)):
        if total_list[i][:4] == 'PMID' and current == False:
            my_pmid_filtered.append(total_list[i])
            current = True
        if total_list[i][:2] == 'OT' and total_list[i][:3] != 'OTO':
            current_kw.append(total_list[i])
        if total_list[i][:4] == 'PMID' and current == True:
            my_kw_filtered.append(current_kw)
            current_kw = []
            my_pmid_filtered.append(total_list[i])
    my_kw_filtered.append(current_kw)

    for i in range(len(my_pmid_filtered)):
        my_pmid_filtered[i] = my_pmid_filtered[i].replace('PMID- ', '')
    for i in range(len(my_kw_filtered)):
        for j in range(len(my_kw_filtered[i])):
            my_kw_filtered[i][j] = my_kw_filtered[i][j].replace('OT  - ', '')

    df_keywords = pd.DataFrame(list(zip(my_pmid_filtered, my_kw_filtered)),
               columns =['pmid', 'keywords'])
    
    df_keywords = df_keywords.drop_duplicates(subset=['pmid'])
    for index, row in df_keywords.iterrows():
        if df_keywords.keywords.loc[index] == []:
            df_keywords.loc[index, 'keywords'] = None

    df = df.reset_index().merge(df_keywords, on='pmid').set_index('index')
    df = df[['pmid', 'pmcid', 'title', 'abstract', 'mesh', 'keywords', 'authors', 'journal', 'pub_type', 'pub_date', 'doi', 'issn', 'crossref', 'full_text_links', 'licenses', 'pdf', 'xml', 'html', 'plain', 'pmc_tgz', 'xml_parse_d', 'html_parse_d', 'pdf_parse_d', 'plain_parse_d', 'content_text']]

    df.pub_date = df.pub_date.astype(str)
    result = df.to_json(orient="index")
    if len(glob.glob('./output/retrieved_df/retrieved_df2.json.zip')) == 0:
        with zipfile.ZipFile("./output/retrieved_df/retrieved_df2.json.zip", mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zip_file:
            dumped_JSON: str = json.dumps(result, indent=4)
            zip_file.writestr("retrieved_df2.json", data=dumped_JSON)
            zip_file.testzip()
        zip_file.close()
    else:
        os.rename('./output/retrieved_df/retrieved_df2.json.zip', './output/retrieved_df/temp_retrieved_df2.json.zip')
        with zipfile.ZipFile("./output/retrieved_df/retrieved_df2.json.zip", mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zip_file:
            dumped_JSON: str = json.dumps(result, indent=4)
            zip_file.writestr("retrieved_df2.json", data=dumped_JSON)
            zip_file.testzip()
        zip_file.close()
        os.remove('./output/retrieved_df/temp_retrieved_df2.json.zip')
    
    return df