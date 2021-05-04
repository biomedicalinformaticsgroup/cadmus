import numpy as np

def percent(num, denom):
    result = np.round((num/denom)*100,1)
    return f'{result}%'

def evaluation(df):
    pdf_count = 0
    html_count = 0
    xml_count = 0
    plain_count = 0
    abstract_count = 0
    working_count = 0
    
    tag_count = 0
    any_count = 0
    
    for index, row in df.iterrows():
        if row['pdf'] == 1:
            pdf_count += 1
        if row['xml'] == 1:
            xml_count += 1
        if row['html'] == 1:
            html_count += 1
        if row['plain'] == 1:
            plain_count += 1
        if row.working_text == '' or row.working_text == None or row.working_text != row.working_text:
            pass
        elif row.working_text[:4] == 'ABS:':
            abstract_count += 1
        else:
            working_count += 1
            
        if row['xml'] == 1 or row['html'] == 1:
            tag_count +=1
        if row['xml'] == 1 or row['html'] == 1 or row['pdf'] == 1 or row['plain'] == 1:
            any_count +=1
            
    print(f'Here is the performance thus far:')
    print(f'PDF:{pdf_count} = {percent(pdf_count, len(df))}')
    print(f'XML:{xml_count} = {percent(xml_count, len(df))}')
    print(f'HTML:{html_count} = {percent(html_count, len(df))}')
    print(f'Plain Text:{plain_count} = {percent(plain_count, len(df))}')
    print(f'\nWe have at least one fomat for {any_count} articles = {percent(any_count, len(df))}')
    print(f'\nWe have a tagged version for {tag_count} articles = {percent(tag_count, len(df))}')
    print(f'\nWe have only the abstract for {abstract_count} articles = {percent(abstract_count, len(df))}')     
    print(f'\nWe have a working text for {working_count} articles = {percent(working_count, len(df))}')     