import os

def output_files ():
    #creating the directories we are planning on using the save the result of the system
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
                'output/formats/txts',
                'output/formats/zips',
                'output/formats/tgzs']:
        try:
            #try to create the directory, most likely will work for new project
            os.mkdir(path)
            print(f'Now creating {path}')
        except:
            #if the directory already exist just pass
            pass