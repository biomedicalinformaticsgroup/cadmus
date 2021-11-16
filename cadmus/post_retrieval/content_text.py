import pandas as pd
import numpy as np

def content_text(retrieval_df):
    # this function is to determine among all the formats retrieved what is the best format available
    # from experience and quality of parsing we prefer teh following order xml html plain pdf
    for index, row in retrieval_df.iterrows():
        #creating the variable we used to make our decision
        xml_d = None
        html_d = None
        pdf_d = None
        plain_d = None
        html_wc = None
        xml_wc = None
        pdf_wc = None
        plain_wc = None
        #for each format we take the wordcount and the content_text
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
        # we set the best text to none for now
        best_text = None
        # we create a list that keep all our values i.e. None or the value
        texts = [xml_d, html_d, plain_d, pdf_d]
        wcs = [xml_wc, html_wc, plain_wc, pdf_wc]
        # we look at the number of formats we retrieved
        choice_count = 0
        for i in range (len(texts)):
            if texts[i] != None:
                choice_count += 1
        # if we only retrieved one format then it's this one
        if choice_count == 1:
            for i in range(len(texts)):
                if texts[i] != None:
                    best_text = texts[i]
                    break
        # if we have more than one option, then we want to compute the average of the WC across all formats
        numerator = 0 
        denominator = 0
        if choice_count > 1:
            for i in range(len(wcs)):
                if wcs[i] != None:
                    numerator += wcs[i]
                    denominator += 1
        # computing the mean word count
        if choice_count > 1:
            mean_wcs = int(float(numerator) / float(denominator))

        default_text = False
        default_format = 0
        text_found = False
        if choice_count > 1:
            for i in range(len(texts)):
                if texts[i] != None:
                    # we want to select the first format available between xml html plain pdf as long that the current word count is at least 80% the mean word count and less than 2.5. this is to avoid outliers
                    if int(wcs[i]) > int(round(mean_wcs * 0.8)) and int(wcs[i]) < int(round(mean_wcs * 2.5)) and text_found == False:
                        best_text = texts[i]
                        text_found = True
                        break   
                    # in case none follow the previous condition then we will take the first format available
                    if  default_text == False:
                        default_format = i
                        default_text = True

        if best_text == None:
            best_text = texts[default_format]
        
        #in case we have no text or the text is smaller than the abstract thenusing the abstract as content
        if row['abstract'] == row['abstract'] and row['abstract'] != None and row['abstract'] != '':
            if (best_text == None) or (len(best_text.split()) < len(str(row['abstract']).split()) and len(row['abstract'].split()) < 1000):
                best_text = str('ABS: ' + row['abstract'])
        #setting the value
        retrieval_df.loc[index, 'content_text'] = best_text

    return retrieval_df