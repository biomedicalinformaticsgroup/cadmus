import pandas as pd
import numpy as np

def working_text(retrieval_df):
    for index, row in retrieval_df.iterrows():
        #print(row['html_parse_d']['text'])
        xml_d = None
        html_d = None
        pdf_d = None
        plain_d = None
        html_wc = 0
        xml_wc = 0
        pdf_wc = 0
        plain_wc = 0

        if 'text' in row['html_parse_d'].keys():
            html_d = str(row['html_parse_d']['text'])
            html_wc = row['html_parse_d']['wc']
        else:
            None
        if 'text' in row['xml_parse_d'].keys():
            xml_d = str(row['xml_parse_d']['text'])
            xml_wc = row['xml_parse_d']['wc']
        else:
            None
        if 'text' in row['pdf_parse_d'].keys():    
            pdf_d = str(row['pdf_parse_d']['text'])
            pdf_wc = row['pdf_parse_d']['wc']
        else:
            None
        if 'text' in row['plain_parse_d'].keys():    
            plain_d = str(row['plain_parse_d']['text'])
            plain_wc = row['plain_parse_d']['wc']
        else:
            None
        
        best_text = None
        texts = [xml_d, html_d, plain_d, pdf_d]
        wcs = [xml_wc, html_wc, plain_wc, pdf_wc]
        max_wcs = 0 
        for i in range(len(wcs)):
            if wcs[i] != None:
                if wcs[i] > max_wcs:
                    max_wcs = wcs[i]
        max_wcs = round(max_wcs * 0.7)
        for i in range(len(texts)):
            if texts[i] != None:
                if wcs[i] > max_wcs:
                    best_text = texts[i]
                    break
        if row['abstract'] == row['abstract'] and row['abstract'] != None and row['abstract'] != '':
            if (best_text == None) or (len(best_text.split()) < len(str(row['abstract']).split()) and len(row['abstract'].split()) < 1000):
                best_text = str('ABS: ' + row['abstract'])

        retrieval_df.loc[index, 'working_text'] = best_text

    return retrieval_df