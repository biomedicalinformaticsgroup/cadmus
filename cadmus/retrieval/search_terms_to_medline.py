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
            bash_profile_file = [
                "export PATH=./output/medline/edirect",
                f"export NCBI_API_KEY={api_key}"
            ]
            with open('./.bash_profile', 'w') as fp:
                for item in bash_profile_file:
                    # write each item on a new line
                    fp.write(item)
                    fp.write('\n')
    else:
        os.remove('./.bash_profile')
        bash_profile_file = [
            "export PATH=./output/medline/edirect",
            f"export NCBI_API_KEY={api_key}"
        ]
        with open('./.bash_profile', 'w') as fp:
            for item in bash_profile_file:
                # write each item on a new line
                fp.write(item)
                fp.write('\n')
    subprocess.call(["./output/medline/edirect_setup.sh", api_key])
    # send the query string by esearch then retrieve by efetch in medline format
    search_results = pipeline(f'esearch -db pubmed -query "{query_string}" | efetch -format medline')
    with open('./output/medline/txts/medline_output.txt', 'w') as file:
        file.write(search_results)
    print('Medline Records retrieved and saved')
