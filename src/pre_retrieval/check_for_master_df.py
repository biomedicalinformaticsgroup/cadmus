# Here is a function to check for the existance of the master df and ensure it is not empty.
from cadmus.src.pre_retrieval import output_files
from pathlib import Path
import os

def check_for_master_df():
    output_files()
    # need to check the local directories for a master df and that it is not empty.
    master_path = [path for path in Path('output/master_df').iterdir() if path.stem == 'master_df2']
    # now check the file exists and that it has some content.
    if len(master_path) == 0:
        result = False
    elif master_path[0]:
        result = int(os.stat(master_path[0]).st_size) > 10000
    else:
        result = False
    return result