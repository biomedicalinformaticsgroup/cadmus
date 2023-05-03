import os
import wget

def output_files ():
    #creating the directories we are planning on using the save the result of the system
    for path in [
                'output',
                'output/retrieved_df',
                'output/esearch_results',
                'output/medline',
                'output/medline/txts',
                'output/medline/json',
                'output/crossref',
                'output/crossref/json',
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

    if os.path.isfile('./output/medline/edirect_setup.sh') == False:
        # check for the Edirect setup and install it if not already present
        path_to_edirect = str(str('export PATH=${\PATH}:') + str(os.path.realpath('.')) + str('/output/medline/edirect'))
        path_to_edirect = path_to_edirect.replace('\\', '')
        edirect_setup_script = f'''#!/bin/bash
        # this script aims to set up edirect for use in cadmus
        # first check if edirect is present in the home directory 
        echo checking if edirect is already installed
        DIR="./output/medline/edirect"
        if [ -d "$DIR" ]; then
        check=1
        else
        check=0
        fi
        if (($check ==0)); then 
        echo edirect not installed, begining download
        yes | sh -c "$(./output/medline/install-edirect.sh)"
        echo "{path_to_edirect}" >> ./.bash_profile
        echo "export NCBI_API_KEY=$1" >> ./.bash_profile
        echo install finished
        else 
        echo edirect already installed
        exit;
        fi'''

        edirect_setup_script = edirect_setup_script.split('\n')
        for i in range(len(edirect_setup_script)):
            while edirect_setup_script[i][0] == ' ':
                edirect_setup_script[i] = edirect_setup_script[i][1:]

        with open('./output/medline/edirect_setup.sh', 'w') as fp:
            for item in edirect_setup_script:
                # write each item on a new line
                fp.write(item)
                fp.write('\n')
        
        os.chmod("./output/medline/edirect_setup.sh", 0o755)

    if os.path.isfile('./output/medline/install-edirect.sh') == False:
        url = "https://ftp.ncbi.nlm.nih.gov/entrez/entrezdirect/install-edirect.sh"
        wget.download(url, out=f"./output/medline")
        print('\n')
        f = open("./output/medline/install-edirect.sh", "r")
        edirect_install_script = f.read()
        f.close()
        os.remove("./output/medline/install-edirect.sh")
        edirect_install_script = edirect_install_script.split('\n')
        edirect_install_script = edirect_install_script[:93]
        with open('./output/medline/install-edirect.sh', 'w') as fp:
            for item in edirect_install_script:
                if item != 'cd ~':
                    # write each item on a new line
                    fp.write(item)
                    fp.write('\n')
                else:
                    fp.write('cd ./output/medline')
                    fp.write('\n')
                
        os.chmod("./output/medline/install-edirect.sh", 0o755)