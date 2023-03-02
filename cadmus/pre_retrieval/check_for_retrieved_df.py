# Here is a function to check for the existance of the retrieved df and ensure it is not empty.
from cadmus.pre_retrieval.output_files import output_files
from pathlib import Path
import os
import glob
import pickle
import json

def check_for_retrieved_df():
    output_files()
    # need to check the local directories for a retrieved df and that it is not empty.
    retrieved_path = [path for path in Path('output/retrieved_df').iterdir() if path.stem == 'retrieved_df2']
    # now check the file exists and that it has some content.
    if len(retrieved_path) == 0:
        result = False
    elif retrieved_path[0]:
        #we used to saved result as pickle files, because there are some problems with loading pickle objects we decided to convert everything to jsons.
        if len(glob.glob(f'./output/crossref/p/*.p', recursive=True)) > 0:
            print('Converting the pickle files from the crossref directory to json files')
            all_ps = glob.glob(f'./output/crossref/p/*.p', recursive=True)
            for i in range(len(all_ps)):
                temp_p = pickle.load(open(f'{all_ps[i]}', 'rb'))
                json_object = json.dumps(temp_p, indent=4)
                with open(f"./output/crossref/json/{all_ps[i].split('/')[-1].split('.')[0]}.json", "w") as outfile:
                    outfile.write(json_object)
                outfile.close()
                os.remove(f'{all_ps[i]}')
            os.rmdir(f'./output/crossref/p')
        #same for Medline
        if len(glob.glob(f'./output/medline/p/*.p', recursive=True)) > 0:
            print('Converting the pickle files from the medline directory to json files')
            all_ps = glob.glob(f'./output/medline/p/*.p', recursive=True)
            for i in range(len(all_ps)):
                temp_p = pickle.load(open(f'{all_ps[i]}', 'rb'))
                json_object = json.dumps(temp_p, indent=4)
                with open(f"./output/medline/json/{all_ps[i].split('/')[-1].split('.')[0]}.json", "w") as outfile:
                    outfile.write(json_object)
                outfile.close()
                os.remove(f'{all_ps[i]}')
            os.rmdir(f'./output/medline/p')
        #same for retrieved_df
        if len(glob.glob(f'./output/retrieved_df/*.p', recursive=True)) > 0:
            print('Converting the pickle files from the retrieved_df directory to json files')
            all_ps = glob.glob(f'./output/retrieved_df/*.p', recursive=True)
            for i in range(len(all_ps)):
                temp_p = pickle.load(open(f'{all_ps[i]}', 'rb'))
                temp_p.pub_date = temp_p.pub_date.astype(str)
                result = temp_p.to_json(orient="index")
                json_object = json.dumps(result, indent=4)
                with open(f"./output/retrieved_df/{all_ps[i].split('/')[-1].split('.')[0]}.json", "w") as outfile:
                    outfile.write(json_object)
                outfile.close()
                os.remove(f'{all_ps[i]}')
        result = int(os.stat(retrieved_path[0]).st_size) > 10000
    else:
        result = False
    return result