# Here is a function to check for the existance of the retrieved df and ensure it is not empty.
from cadmus.pre_retrieval.output_files import output_files
import os
import glob
import pickle
import json
import zipfile

def check_for_retrieved_df():
    output_files()
    # need to check the local directories for a retrieved df and that it is not empty.
    retrieved_path = glob.glob('./output/retrieved_df/*retrieved_df2*')
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

        if len(glob.glob(f'./output/retrieved_df/*.json', recursive=True)) > 0:
            print('Converting the json files from the retrieved_df directory to zip files')
            all_ps = glob.glob(f'./output/retrieved_df/*.json', recursive=True)
            for i in range(len(all_ps)):
                zipfile.ZipFile(f'{all_ps[i]}.zip', mode='w').write(f'{all_ps[i]}', arcname=f'{all_ps[i].split("/")[-1].split(".")[0]}.json')
                os.remove(f'{all_ps[i]}')
        
        if len(glob.glob(f'./output/retrieved_df/*.tsv', recursive=True)) > 0:
            print('Converting the tsv files from the retrieved_df directory to zip files')
            all_ps = glob.glob(f'./output/retrieved_df/*.tsv', recursive=True)
            for i in range(len(all_ps)):
                zipfile.ZipFile(f'{all_ps[i]}.zip', mode='w').write(f'{all_ps[i]}', arcname=f'{all_ps[i].split("/")[-1].split(".")[0]}.tsv')
                os.remove(f'{all_ps[i]}')
            retrieved_path[0] = 'output/retrieved_df/retrieved_df2.tsv.zip'

        if len(glob.glob(f'./output/crossref/json/*.json', recursive=True)) > 0:
            print('Converting the json files from the crossref directory to zip files')
            all_ps = glob.glob(f'./output/crossref/json/*.json', recursive=True)
            for i in range(len(all_ps)):
                zipfile.ZipFile(f'{all_ps[i]}.zip', mode='w').write(f'{all_ps[i]}', arcname=f'{all_ps[i].split("/")[-1].split(".")[0]}.json')
                os.remove(f'{all_ps[i]}')

        if len(glob.glob(f'./output/esearch_results/*.json', recursive=True)) > 0:
            print('Converting the json files from the esearch_results directory to zip files')
            all_ps = glob.glob(f'./output/esearch_results/*.json', recursive=True)
            for i in range(len(all_ps)):
                zipfile.ZipFile(f'{all_ps[i]}.zip', mode='w').write(f'{all_ps[i]}', arcname=f'{all_ps[i].split("/")[-1].split(".")[0]}.json')
                os.remove(f'{all_ps[i]}')
        
        if len(glob.glob(f'./output/medline/json/*.json', recursive=True)) > 0:
            print('Converting the json files from the medline directory to zip files')
            all_ps = glob.glob(f'./output/medline/json/*.json', recursive=True)
            for i in range(len(all_ps)):
                zipfile.ZipFile(f'{all_ps[i]}.zip', mode='w').write(f'{all_ps[i]}', arcname=f'{all_ps[i].split("/")[-1].split(".")[0]}.json')
                os.remove(f'{all_ps[i]}')
        
        if len(glob.glob(f'./output/medline/txts/*.txt', recursive=True)) > 0:
            print('Converting the txt files from the medline directory to zip files')
            all_ps = glob.glob(f'./output/medline/txts/*.txt', recursive=True)
            for i in range(len(all_ps)):
                zipfile.ZipFile(f'{all_ps[i]}.zip', mode='w').write(f'{all_ps[i]}', arcname=f'{all_ps[i].split("/")[-1].split(".")[0]}.txt')
                os.remove(f'{all_ps[i]}')
        
        if len(glob.glob(f'./output/retrieved_parsed_files/content_text/*.txt', recursive=True)) > 0:
            print('Converting the txt files from the retrieved_parsed_files/content_text directory to zip files')
            all_ps = glob.glob(f'./output/retrieved_parsed_files/content_text/*.txt', recursive=True)
            for i in range(len(all_ps)):
                zipfile.ZipFile(f'{all_ps[i]}.zip', mode='w').write(f'{all_ps[i]}', arcname=f'{all_ps[i].split("/")[-1].split(".")[0]}.txt')
                os.remove(f'{all_ps[i]}')

        if len(glob.glob(f'./output/retrieved_parsed_files/htmls/*.txt', recursive=True)) > 0:
            print('Converting the txt files from the retrieved_parsed_files/htmls directory to zip files')
            all_ps = glob.glob(f'./output/retrieved_parsed_files/htmls/*.txt', recursive=True)
            for i in range(len(all_ps)):
                zipfile.ZipFile(f'{all_ps[i]}.zip', mode='w').write(f'{all_ps[i]}', arcname=f'{all_ps[i].split("/")[-1].split(".")[0]}.txt')
                os.remove(f'{all_ps[i]}')

        if len(glob.glob(f'./output/retrieved_parsed_files/pdfs/*.txt', recursive=True)) > 0:
            print('Converting the txt files from the retrieved_parsed_files/pdfs directory to zip files')
            all_ps = glob.glob(f'./output/retrieved_parsed_files/pdfs/*.txt', recursive=True)
            for i in range(len(all_ps)):
                zipfile.ZipFile(f'{all_ps[i]}.zip', mode='w').write(f'{all_ps[i]}', arcname=f'{all_ps[i].split("/")[-1].split(".")[0]}.txt')
                os.remove(f'{all_ps[i]}')
        
        if len(glob.glob(f'./output/retrieved_parsed_files/txts/*.txt', recursive=True)) > 0:
            print('Converting the txt files from the retrieved_parsed_files/txts directory to zip files')
            all_ps = glob.glob(f'./output/retrieved_parsed_files/txts/*.txt', recursive=True)
            for i in range(len(all_ps)):
                zipfile.ZipFile(f'{all_ps[i]}.zip', mode='w').write(f'{all_ps[i]}', arcname=f'{all_ps[i].split("/")[-1].split(".")[0]}.txt')
                os.remove(f'{all_ps[i]}')
        
        if len(glob.glob(f'./output/retrieved_parsed_files/xmls/*.txt', recursive=True)) > 0:
            print('Converting the txt files from the retrieved_parsed_files/xmls directory to zip files')
            all_ps = glob.glob(f'./output/retrieved_parsed_files/xmls/*.txt', recursive=True)
            for i in range(len(all_ps)):
                zipfile.ZipFile(f'{all_ps[i]}.zip', mode='w').write(f'{all_ps[i]}', arcname=f'{all_ps[i].split("/")[-1].split(".")[0]}.txt')
                os.remove(f'{all_ps[i]}')
        
        if len(glob.glob(f'./output/formats/htmls/*.html', recursive=True)) > 0:
            print('Converting the html files from the formats/htmls directory to zip files')
            all_ps = glob.glob(f'./output/formats/htmls/*.html', recursive=True)
            for i in range(len(all_ps)):
                zipfile.ZipFile(f'{all_ps[i]}.zip', mode='w').write(f'{all_ps[i]}', arcname=f'{all_ps[i].split("/")[-1].split(".")[0]}.html')
                os.remove(f'{all_ps[i]}')
        
        if len(glob.glob(f'./output/formats/pdfs/*.pdf', recursive=True)) > 0:
            print('Converting the pdf files from the formats/pdfs directory to zip files')
            all_ps = glob.glob(f'./output/formats/pdfs/*.pdf', recursive=True)
            for i in range(len(all_ps)):
                zipfile.ZipFile(f'{all_ps[i]}.zip', mode='w').write(f'{all_ps[i]}', arcname=f'{all_ps[i].split("/")[-1].split(".")[0]}.pdf')
                os.remove(f'{all_ps[i]}')
        
        if len(glob.glob(f'./output/formats/txts/*.txt', recursive=True)) > 0:
            print('Converting the txt files from the formats/txts directory to zip files')
            all_ps = glob.glob(f'./output/formats/txts/*.txt', recursive=True)
            for i in range(len(all_ps)):
                zipfile.ZipFile(f'{all_ps[i]}.zip', mode='w').write(f'{all_ps[i]}', arcname=f'{all_ps[i].split("/")[-1].split(".")[0]}.txt')
                os.remove(f'{all_ps[i]}')

        if len(glob.glob(f'./output/formats/xmls/*.xml', recursive=True)) > 0:
            print('Converting the xml files from the formats/xmls directory to zip files')
            all_ps = glob.glob(f'./output/formats/xmls/*.xml', recursive=True)
            for i in range(len(all_ps)):
                zipfile.ZipFile(f'{all_ps[i]}.zip', mode='w').write(f'{all_ps[i]}', arcname=f'{all_ps[i].split("/")[-1].split(".")[0]}.xml')
                os.remove(f'{all_ps[i]}')

        result = int(os.stat(retrieved_path[0]).st_size) > 10000
    else:
        result = False
    
    if len(glob.glob('./output/medline/txts/temp_medline_output.txt.zip')) > 0:
        os.rename('./output/medline/txts/temp_medline_output.txt.zip', './output/medline/txts/medline_output.txt.zip')
    if len(glob.glob('./output/medline/txts/temp_retrieved_df.json.zip')) > 0:
        os.rename('./output/retrieved_df/temp_retrieved_df.json.zip', './output/retrieved_df/retrieved_df.json.zip')
    if len(glob.glob('./output/medline/txts/temp_retrieved_df2.json.zip')) > 0:
        os.rename('./output/retrieved_df/temp_retrieved_df2.json.zip', './output/retrieved_df/retrieved_df2.json.zip')
    if len(glob.glob('./output/medline/txts/temp_retrieved_df2.tsv.zip')) > 0:
        os.rename('./output/retrieved_df/temp_retrieved_df2.tsv.zip', './output/retrieved_df/retrieved_df2.tsv.zip')
    
    return result