from cadmus.retrieval.is_ipython import is_ipython
import os
import platform
from IPython.display import clear_output
# this function is to clean the terminal windows to keep only the relevant information
def clear():
    #finding if the code is run from a program like jupyter notebook
    if is_ipython() == True:
        clear_output()
    else:
        #the clear comand  will depend on the OS
        if platform.system() == 'Windows':
            os.system('cls')
        else:
            os.system('clear')