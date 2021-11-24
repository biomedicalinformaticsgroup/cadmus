import pandas as pd
import numpy as np
import pickle
import subprocess
import re
import os

def clean_up_dir(df):
    # this function is here to clean up directories from file sthat are not used 
    # this files can be previous index not used anymore due to update or false positive 


    # first directory we clean is the crossref
    # we first load the list all the files available in one directory 
    command = subprocess.getstatusoutput("ls -l ./output/crossref/p/")
    # we change the output as a list
    command = list(command)
    # the list as 2 elements, first the answer_code from subprocess, second the actual output
    command = command[1]
    # here we split everything in order to have one line per file
    my_list = []
    for i in range(1,len(str(command).split('\n'))):
        my_list.append(str(command).split('\n')[i])
    command = my_list
    # we remove all the other information to only keep the the file name without extension
    files = []
    for i in range(len(command)):
        files.append(command[i].split()[-1][:-2])
    # we create a list that keep all the index that should be saved
    list_to_keep = list(df.index)
    for i in range(len(files)):
        if files[i] in list_to_keep:
            pass
        else:
            # if the file name doesn't have a corresponding line in the df we can remove the file
            os.remove(f'./output/crossref/p/{files[i]}.p')

    # we now apply the same method to the medline directory
    command = subprocess.getstatusoutput("ls -l ./output/medline/p/")
    command = list(command)
    command = command[1]
    my_list = []
    for i in range(1,len(str(command).split('\n'))):
        my_list.append(str(command).split('\n')[i])
    command = my_list
    files = []
    for i in range(len(command)):
        files.append(command[i].split()[-1][:-2])
    list_to_keep = list(df.index)
    for i in range(len(files)):
        if files[i] in list_to_keep:
            pass
        else:
            os.remove(f'./output/medline/p/{files[i]}.p')

    # we now apply it to the htmls directory
    command = subprocess.getstatusoutput("ls -l ./output/formats/htmls/")
    command = list(command)
    command = command[1]
    my_list = []
    for i in range(1,len(str(command).split('\n'))):
        my_list.append(str(command).split('\n')[i])
    command = my_list
    files = []
    for i in range(len(command)):
        files.append(command[i].split()[-1][:-5])
    list_to_keep = list(df[df.html == 1].index)
    for i in range(len(files)):
        if files[i] in list_to_keep:
            pass
        else:
            os.remove(f'./output/formats/htmls/{files[i]}.html')
    
    # we now apply it to the pdfs directory
    command = subprocess.getstatusoutput("ls -l ./output/formats/pdfs/")
    command = list(command)
    command = command[1]
    my_list = []
    for i in range(1,len(str(command).split('\n'))):
        my_list.append(str(command).split('\n')[i])
    command = my_list
    files = []
    for i in range(len(command)):
        files.append(command[i].split()[-1][:-4])
    list_to_keep = list(df[df.pdf == 1].index)
    for i in range(len(files)):
        if files[i] in list_to_keep:
            pass
        else:
            os.remove(f'./output/formats/pdfs/{files[i]}.pdf')

    # same to the xmls directory
    command = subprocess.getstatusoutput("ls -l ./output/formats/xmls/")
    command = list(command)
    command = command[1]
    my_list = []
    for i in range(1,len(str(command).split('\n'))):
        my_list.append(str(command).split('\n')[i])
    command = my_list
    files = []
    for i in range(len(command)):
        files.append(command[i].split()[-1][:-4])
    list_to_keep = list(df[df.xml == 1].index)
    for i in range(len(files)):
        if files[i] in list_to_keep:
            pass
        else:
            os.remove(f'./output/formats/xmls/{files[i]}.xml')

    # again for the txts directory
    command = subprocess.getstatusoutput("ls -l ./output/formats/txts/")
    command = list(command)
    command = command[1]
    my_list = []
    for i in range(1,len(str(command).split('\n'))):
        my_list.append(str(command).split('\n')[i])
    command = my_list
    files = []
    for i in range(len(command)):
        files.append(command[i].split()[-1][:-4])
    list_to_keep = list(df[df.plain == 1].index)
    for i in range(len(files)):
        if files[i] in list_to_keep:
            pass
        else:
            os.remove(f'./output/formats/txts/{files[i]}.txt')
    
    # finally, we are now finishing with the tgzs directory
    command = subprocess.getstatusoutput("ls -l ./output/formats/tgzs/")
    command = list(command)
    command = command[1]
    my_list = []
    for i in range(1,len(str(command).split('\n'))):
        my_list.append(str(command).split('\n')[i])
    command = my_list
    files = []
    for i in range(len(command)):
        files.append(command[i].split()[-1][:-4])
    list_to_keep = list(df.index)
    for i in range(len(files)):
        if files[i] in list_to_keep:
            pass
        else:
            os.remove(f'./output/formats/tgzs/{files[i]}.tgz')