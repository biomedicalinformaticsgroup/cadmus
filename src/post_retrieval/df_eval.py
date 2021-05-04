# this script is to evaluate the success of the retrieval
# its a simple list of counts and percentages which should be printed out.
import numpy as np

def df_eval(df):
    # quick percentage func
    def pc(x, y):
        return(f'{np.round(x/y*100,1)}%')
    
    # count for any format retrival
    retrieved = 0
    # count for tagged and pdf retrieval
    criteria = 0
    
    for index, row in df.iterrows():
        if row['html'] == 1\
        or row['pdf'] ==1\
        or row['xml'] == 1\
        or row['plain'] == 1:
            retrieved +=1
            
        if (row['html'] == 1\
        or row['xml'] == 1)\
        and (row['pdf'] == 1):
            criteria +=1
        
    html_c = sum(df['html'] == 1)
    pdf_c = sum(df['pdf'] == 1)  
    xml_c = sum(df['xml'] == 1)
    plain_c = sum(df['plain'] == 1)
    
    
    
    
    print(f'Out of {len(df)} articles\nwe got at least one version for {retrieved} = {pc(retrieved, len(df))}\n')
    print(f'We got a pdf and tagged version for {criteria} artilces = {pc(criteria,len(df))}\n')
    print(f'{html_c} HTMLs were retrieved = {pc(html_c, len(df))}')
    print(f'{pdf_c} PDFs were retrieved = {pc(pdf_c, len(df))}')
    print(f'{xml_c} XMLs were retrieved = {pc(xml_c, len(df))}')
    print(f'{plain_c} plain texts were retrieved = {pc(plain_c, len(df))}')