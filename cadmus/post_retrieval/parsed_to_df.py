import pandas as pd
import subprocess

def parsed_to_df(path = './output/retrieved_parsed_files/content_text/'):
    command = subprocess.getstatusoutput(f"ls -l {path}")
    command = list(command)
    command = command[1]
    my_list = str(command).split('\n')[1:]
    command = my_list
    files = []
    for i in range(len(command)):
        files.append(command[i].split()[-1][:-4])
    content_text = []
    for i in range(len(files)):
        r = open(f"./output/retrieved_parsed_files/content_text/{files[i]}.txt", "r")
        text = r.read()
        content_text.append(text)
        r.close()
    df = pd.DataFrame(content_text, columns=["content_text"])
    df.index = files
    return df