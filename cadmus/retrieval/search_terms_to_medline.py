import subprocess
import os
from cadmus.retrieval.edirect import pipeline
import glob 
import zipfile

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
        if len(glob.glob(f'./output/medline/txts/*.zip')) == 0:
            with zipfile.ZipFile("./output/medline/txts/medline_output.txt.zip", mode="a", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zip_file:
                zip_file.writestr("medline_output.txt", data=search_results)
                zip_file.testzip()
            zip_file.close()
            print('Medline Records retrieved and saved')
        else:
            with zipfile.ZipFile("./output/medline/txts/medline_output.txt.zip", "r") as z:
                for filename in z.namelist():
                    with z.open(filename) as f:
                        d = f.read()
                    f.close()
            z.close()
            d = str(str(d.decode('utf-8')) + '\n' + '\n' + str(search_results)).encode('utf-8')
            os.rename('./output/medline/txts/medline_output.txt.zip', './output/medline/txts/temp_medline_output.txt.zip')
            with zipfile.ZipFile("./output/medline/txts/medline_output.txt.zip", mode="a", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zip_file:
                zip_file.writestr("medline_output.txt", data=d)
                zip_file.testzip()
            zip_file.close()
            os.remove('./output/medline/txts/temp_medline_output.txt.zip')
            print('Medline Records retrieved and saved')
    else:
        #to avoid errors for large pmids list. We now chunk into smaller set of 9000. Finally we append every chunk in the medline text file.
        for i in range(len(query_string)):
            search_results = pipeline(f'esearch -db pubmed -query "{query_string[i]}" | efetch -format medline')
            if len(glob.glob(f'./output/medline/txts/*.zip')) == 0:
                with zipfile.ZipFile("./output/medline/txts/medline_output.txt.zip", mode="a", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zip_file:
                    zip_file.writestr("medline_output.txt", data=search_results)
                    zip_file.testzip()
                zip_file.close()
                print('Medline Records retrieved and saved')
            else:
                with zipfile.ZipFile("./output/medline/txts/medline_output.txt.zip", "r") as z:
                    for filename in z.namelist():
                        with z.open(filename) as f:
                            d = f.read()
                        f.close()
                z.close()
                d = str(str(d.decode('utf-8')) + '\n' + '\n' + str(search_results)).encode('utf-8')
                os.rename('./output/medline/txts/medline_output.txt.zip', './output/medline/txts/temp_medline_output.txt.zip')
                with zipfile.ZipFile("./output/medline/txts/medline_output.txt.zip", mode="a", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zip_file:
                    zip_file.writestr("medline_output.txt", data=d)
                    zip_file.testzip()
                zip_file.close()
                os.remove('./output/medline/txts/temp_medline_output.txt.zip')
            print(f'Medline Records retrieved and saved {i+1} out of {len(query_string)}')