import numpy as np
#quick percentage function
def percent(num, denom):
    result = np.round((num/denom)*100,1)
    return f'{result}%'

def evaluation(df):
    #initialize the variable to 0
    pdf_count = 0
    html_count = 0
    xml_count = 0
    plain_count = 0
    abstract_count = 0
    content_count = 0
    
    tag_count = 0
    any_count = 0
    
    for index, row in df.iterrows():
        #iterate the retrieval value for each format
        if row['pdf'] == 1:
            pdf_count += 1
        if row['xml'] == 1:
            xml_count += 1
        if row['html'] == 1:
            html_count += 1
        if row['plain'] == 1:
            plain_count += 1
        if row.content_text == 0:
            pass
        else:
            # computing the value of retreived document(any format)
            content_count += 1
        if row.content_text == 0:
            if row['abstract'] == None or row['abstract'] == '':
                pass
            else:
                #keeping count of the time we did not retreive the full text but we found the abastract
                abstract_count += 1
        if row['xml'] == 1 or row['html'] == 1:
        #number of document we have at least one taged version available            
            tag_count +=1
        if row['xml'] == 1 or row['html'] == 1 or row['pdf'] == 1 or row['plain'] == 1:
            #number of document we have at least one format available
            any_count +=1
    #printing the result    
    print(f'Here is the performance thus far:')
    print(f'PDF:{pdf_count} = {percent(pdf_count, len(df))}')
    print(f'XML:{xml_count} = {percent(xml_count, len(df))}')
    print(f'HTML:{html_count} = {percent(html_count, len(df))}')
    print(f'Plain Text:{plain_count} = {percent(plain_count, len(df))}')
    print(f'\nWe have a tagged version (HTML, XML) for {tag_count} articles = {percent(tag_count, len(df))}')
    print(f'\nWe only have the abstract but not the associated content text for {abstract_count} articles = {percent(abstract_count, len(df))}')     
    print(f'\nWe have a content text for {content_count} out of {len(df)} articles = {percent(content_count, len(df))}')     