def is_ipython():
    #this function is here to check if the code is run from a program like jupyter Notebook
    from IPython import get_ipython
    return get_ipython() is not None