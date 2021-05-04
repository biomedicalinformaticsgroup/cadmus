from cadmus.src.retrieval.is_ipython import is_ipython
import os
import platform
from IPython.display import clear_output

def clear():
    if is_ipython() == True:
        clear_output()
    else:
        if platform.system() == 'Windows':
            os.system('cls')
        else:
            os.system('clear')