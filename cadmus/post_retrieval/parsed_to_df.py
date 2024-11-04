import pandas as pd
import subprocess
import zipfile

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
        with zipfile.ZipFile(f"{path}/{files[i]}.zip", "r") as z:
            for filename in z.namelist():
                with z.open(filename) as f:
                    d = f.read()
                    d = d.decode()
                    content_text.append(d)
                f.close()
        z.close()
    df = pd.DataFrame(content_text, columns=["content_text"])
    df.index = files
    return df
