import setuptools
   
setuptools.setup(
    name="cadmus",
    version="0.3.9",
    author="Jamie Campbell, Ian Simpson, Antoine Lain",
    author_email="Jamie.campbell@igmm.ed.ac.uk, Ian.Simpson@ed.ac.uk, Antoine.Lain@ed.ac.uk",
    description="This projects is to build full text retrieval system setup for generation of large biomedical corpora from published literature.",
    packages=setuptools.find_packages(),
    classifiers=[
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: LINUX/MACOS",
    ],
    install_requires=[
'pandas',
'numpy',
'requests',
'bs4',
'tika==1.24',
'urllib3',
'wget',
'biopython',
'python-dateutil',
'lxml',
'IPython',
'fuzzywuzzy'
],
    python_requires='>=3.6'
)