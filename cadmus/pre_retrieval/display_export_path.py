import os 

def display_export_path():
    path_to_edirect = str(str('export PATH=${\PATH}:') + str(os.path.realpath('.')) + str('/output/medline/edirect'))
    path_to_edirect = path_to_edirect.replace('\\', '')
    print(path_to_edirect)