import os

def output_files ():
    for path in ['output',
                'output/master_df',
                'output/esearch_results',
                'output/medline',
                'output/medline/txts',
                'output/medline/p',
                'output/crossref',
                'output/crossref/p',
                'output/formats',
                'output/formats/xmls',
                'output/formats/pdfs',
                'output/formats/htmls',
                ## Jamie testing 
                'output/formats/testing',
                ##finish test
                'output/formats/txts',
                'output/formats/zips',
                'output/formats/tgzs']:
        try:
            os.mkdir(path)
            print(f'Now creating {path}')
        except:
            pass
            #print(f'{path} already exists')