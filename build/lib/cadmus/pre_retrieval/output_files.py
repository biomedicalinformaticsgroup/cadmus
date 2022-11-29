import os

def output_files ():
    #creating the directories we are planning on using the save the result of the system
    for path in [
                'output',
                'output/retrieved_df',
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
                'output/formats/tgzs',
                'output/retrieved_parsed_files',
                'output/retrieved_parsed_files/htmls',
                'output/retrieved_parsed_files/xmls',
                'output/retrieved_parsed_files/pdfs',
                'output/retrieved_parsed_files/txts',
                'output/retrieved_parsed_files/content_text'
                ]:
        try:
            #try to create the directory, most likely will work for new project
            os.mkdir(path)
            print(f'Now creating {path}')
        except:
            #if the directory already exist just pass
            pass