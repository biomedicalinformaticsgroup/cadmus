def is_ipython():
    from IPython import get_ipython
    return get_ipython() is not None