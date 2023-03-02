from cadmus.pre_retrieval.output_files import output_files

import pickle
import json
import pandas as pd

def change_output_structure(df):
    output_files()
    for index, row in df.iterrows():
        if row['content_text'] == '' or row['content_text'] == None or row['content_text'] != row['content_text'] or row['content_text'][:4] == ' ABS:':
            df.loc[index, 'content_text'] = int(0)
        else:
            w = open(f"./output/retrieved_parsed_files/content_text/{index}.txt", "w")
            w.write(row['content_text'])
            w.close()
            df.loc[index, 'content_text'] = int(1)

        if 'wc' in row['html_parse_d'].keys():
            w = open(f"./output/retrieved_parsed_files/htmls/{index}.txt", "w")
            w.write(row['html_parse_d']['text'])
            w.close()
            if row['abstract'] != '' and row['abstract'] != None:       
                wc_abs = len(row['abstract'].split())
            else:
                wc_abs = 0
            parse_d = {}
            parse_d.update({'file_path': row['html_parse_d']['file_path'],
                    'size':row['html_parse_d']['size'],
                    'wc':row['html_parse_d']['wc'],
                    'wc_abs': wc_abs,
                    'url':row['html_parse_d']['url'],
                    'body_unique_score':row['html_parse_d']['body_unique_score'],
                    'ab_sim_score':row['html_parse_d']['ab_sim_score']})
            df.loc[index, 'html_parse_d'].update(parse_d)
        else:
            df.loc[index, 'html'] = int(0)

        if 'wc' in row['xml_parse_d'].keys():
            w = open(f"./output/retrieved_parsed_files/xmls/{index}.txt", "w")
            w.write(row['xml_parse_d']['text'])
            w.close()
            if row['abstract'] != '' and row['abstract'] != None:       
                wc_abs = len(row['abstract'].split())
            else:
                wc_abs = 0
            parse_d = {}
            parse_d.update({'file_path': row['xml_parse_d']['file_path'],
                    'size':row['xml_parse_d']['size'],
                    'wc':row['xml_parse_d']['wc'],
                    'wc_abs': wc_abs,
                    'url':row['xml_parse_d']['url'],
                    'body_unique_score':row['xml_parse_d']['body_unique_score'],
                    'ab_sim_score':row['xml_parse_d']['ab_sim_score']})
            df.loc[index, 'xml_parse_d'].update(parse_d)
        else:
            df.loc[index, 'xml'] = int(0)

        if 'wc' in row['pdf_parse_d'].keys():
            w = open(f"./output/retrieved_parsed_files/pdfs/{index}.txt", "w")
            w.write(row['pdf_parse_d']['text'])
            w.close()
            if row['abstract'] != '' and row['abstract'] != None:       
                wc_abs = len(row['abstract'].split())
            else:
                wc_abs = 0
            parse_d = {}
            parse_d.update({'file_path': row['pdf_parse_d']['file_path'],
                    'date': row['pdf_parse_d']['date'],
                    'size':row['pdf_parse_d']['size'],
                    'wc':row['pdf_parse_d']['wc'],
                    'wc_abs': wc_abs,
                    'Content_type':row['pdf_parse_d']['Content_type'], 
                    'url':row['pdf_parse_d']['url'],
                    'body_unique_score':row['pdf_parse_d']['body_unique_score'],
                    'ab_sim_score':row['pdf_parse_d']['ab_sim_score']})
            df.loc[index, 'pdf_parse_d'].update(parse_d)
        else:
            df.loc[index, 'pdf'] = int(0)

        if 'wc' in row['plain_parse_d'].keys():
            w = open(f"./output/retrieved_parsed_files/txts/{index}.txt", "w")
            w.write(row['plain_parse_d']['text'])
            w.close()
            if row['abstract'] != '' and row['abstract'] != None:       
                wc_abs = len(row['abstract'].split())
            else:
                wc_abs = 0
            parse_d = {}
            parse_d.update({'file_path': row['plain_parse_d']['file_path'],
                    'size':row['plain_parse_d']['size'],
                    'wc':row['plain_parse_d']['wc'],
                    'wc_abs': wc_abs,
                    'url':row['plain_parse_d']['url'],
                    'body_unique_score':row['plain_parse_d']['body_unique_score'],
                    'ab_sim_score':row['plain_parse_d']['ab_sim_score']})
            df.loc[index, 'plain_parse_d'].update(parse_d)
        else:
            df.loc[index, 'plain'] = int(0)
    
    df.pub_date = df.pub_date.astype(str)
    result = df.to_json(orient="index")
    json_object = json.dumps(result, indent=4)
    with open("./output/retrieved_df/retrieved_df2.json", "w") as outfile:
        outfile.write(json_object)
    outfile.close()
    df.to_csv(f'./output/retrieved_df/retrieved_df2.tsv', sep='\t')

    return df