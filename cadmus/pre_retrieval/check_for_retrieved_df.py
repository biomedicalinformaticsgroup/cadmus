# Here is a function to check for the existance of the retrieved df and ensure it is not empty.
from cadmus.pre_retrieval.output_files import output_files
from pathlib import Path
import os

def check_for_retrieved_df():
    output_files()
    # need to check the local directories for a retrieved df and that it is not empty.
    retrieved_path = [path for path in Path('output/retrieved_df').iterdir() if path.stem == 'retrieved_df2']
    # now check the file exists and that it has some content.
    if len(retrieved_path) == 0:
        result = False
    elif retrieved_path[0]:
        result = int(os.stat(retrieved_path[0]).st_size) > 10000
    else:
        result = False
    return result