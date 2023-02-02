import subprocess
import os
from cadmus.retrieval.edirect import pipeline

# we can use the search terms provided to query pubmed using edirect esearch.
# This will provide us with a text file of papers in medline format
def search_terms_to_medline(query_string, api_key):
    if os.path.isfile('./.bash_profile') == False:
        if os.path.isdir('./output/medline/edirect') == False:
            pass
        else:
            path_to_edirect = str(str('export PATH=${\PATH}:') + str(os.path.realpath('.')) + str('/output/medline/edirect'))
            path_to_edirect = path_to_edirect.replace('\\', '')
            bash_profile_file = [
                path_to_edirect,
                f"export NCBI_API_KEY={api_key}"
            ]
            with open('./.bash_profile', 'w') as fp:
                for item in bash_profile_file:
                    # write each item on a new line
                    fp.write(item)
                    fp.write('\n')
    else:
        os.remove('./.bash_profile')
        path_to_edirect = str(str('export PATH=${PATH}:') + str(os.path.realpath('.')) + str('/output/medline/edirect'))
        path_to_edirect = path_to_edirect.replace('\\', '')
        bash_profile_file = [
            path_to_edirect,
            f"export NCBI_API_KEY={api_key}"
        ]
        with open('./.bash_profile', 'w') as fp:
            for item in bash_profile_file:
                # write each item on a new line
                fp.write(item)
                fp.write('\n')
    subprocess.call(["./output/medline/edirect_setup.sh", api_key])
    # send the query string by esearch then retrieve by efetch in medline format
    if type(query_string) == str:
        search_results = pipeline(f'esearch -db pubmed -query "{query_string}" | efetch -format medline')
        with open('./output/medline/txts/medline_output.txt', 'w') as file:
            file.write(search_results)
        file.close()
        print('Medline Records retrieved and saved')
    else:
        for i in range(len(query_string)):
            search_results = pipeline(f'esearch -db pubmed -query "{query_string[i]}" | efetch -format medline')
            print(search_results.split('\n')[0])
            with open('./output/medline/txts/medline_output.txt', 'a') as file:
                file.write(search_results)
            file.close()
            print(f'Medline Records retrieved and saved {i+1} out of {len(query_string)}')