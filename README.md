# Cadmus [![DOI](https://zenodo.org/badge/364367629.svg)](https://zenodo.org/badge/latestdoi/364367629)
This project aims to build an automated full text retrieval system for generation of large biomedical corpora from published literature for research purposes.

## Requirements

In order to run the code, you will need a few things:

You need to have Java 7+.

You will need to git clone the project to the directory where you want to save your result.

An API key from NCBI (this is used to search PubMed from articles using a search string or list of PubMed IDs(you can find more information [here](https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/)).

An API key from Crossref. 
Crossref provides metadata via an API providing you with licensing information and links to full text documents (you can find more information [here](https://apps.crossref.org/clickthrough/researchers/#/) you will need to agree the following two licenses:

1. Wiley Text and Data Mining License v1.1
2. Elsevier Text and Data Mining Service Agreement)

## Installation
Cadmus has a number of dependencies on other Python packages, it is recommended to install in an isolated environment.

`git clone https://github.com/biomedicalinformaticsgroup/cadmus.git`

`pip install ./cadmus`

## Get started

The format we are using for the search term(s) is the same as the one for [PubMed](https://pubmed.ncbi.nlm.nih.gov/). You can first try your search term(s) on PubMed and then use the same search term(s) as input for Cadmus bioscraping.

In order to create your corpora you are going to use the function called 'bioscraping'. The function is taking the following required parameters:

1. A PubMed query string or a python list of PubMed IDs
2. An email address
3. Your NCBI_API_KEY
4. Your Crossref_API_KEY
   
The function can also receive optional parameters.

1. The "start" parameter tells the function at which service we were at before failure (e.g. crossref, doi, pubmed central API. . .).
2. The "idx" parameter tells the function what is the last saved row index (article).

Start and idx are designed to use when restarting cadmus after a program failure. When Cadmus is running, there is a repeated output feed at the top of the live output.  This line will show you the stage and index that your output dataframe was last saved in case of failure for whatever reason. By using these optional parameters, the programme will take off where it left off, saving you starting the process from the beginning again.

3. "full_search"
Finally, in case you want to check if a document became available since the last time you tried. The function takes a last optional parameter called full_search. full_search has three predefined values:

1. The default Value None, the function only looks for the new articles since the last run.
2. 'light', the function looks for the new articles since the last run and re-tried the row where we did not get any format.
3. 'heavy', the function looks for the new articles since the last run and re-tried the row where it did not retrieve a tagged version (i.e. html or xml).


```python
from cadmus import bioscraping
bioscraping(
    INPUT,
    EMAIL,
    NCBI_APY_KEY,
    CROSSREF_API_KEY
    )
```

## Load the result

The output from Cadmus is a Pickle object. In order to open the result use the following two lines of code.

```python
import pickle
retrieved_df = pickle.load(open('./output/retrieved_df/retrieved_df2.p', 'rb'))
```
---
Output details
---
The main output is a pandas dataframe saved as a pickle object.  
This is stored in the directory ```"./ouput/retrieved_df/retrieved_df2.p"```. 
The dataframe columns are 
- pmid <class 'str'>
    - pubmed id
- pmcid <class 'float'>
    - pubmed central id 
- title <class 'str'>
- abstract <class 'str'>
- authors <class 'list'>
- journal <class 'str'>
- pub_type <class 'list'>
    - Publication type (from pubmed metadata) 
- pub_date <class 'datetime.date'>
    - Publication type (from pubmed metadata)  
- doi <class 'str'>
- issn <class 'str'>
- crossref <class 'numpy.int64'>
    - 1/0 for presence of crossref record when searching on doi 
- full_text_links <class 'dict'>
    - dict_keys
        - 'cr_tdm' (list of crossref tdm links),
        - 'html_parse' (list of links parsed from html files,
        - 'pubmed_links' (list of links from "linkout" section on pubmed page, not including PMC])
- licenses <class 'list'>
- pdf <class 'numpy.int64'>
    - (1/0) for successful download of pdf version 
- xml <class 'numpy.int64'>
    - (1/0) for successful download of xml version
- html <class 'numpy.int64'>
    - (1/0) for successful download of html version
- plain <class 'numpy.int64'>
    - (1/0) for successful download of plain text version 
- pmc_tgz <class 'numpy.int64'>
    - (1/0) for successful download of Pubmed Central Tar g-zip 
- xml_parse_d <class 'dict'>
- html_parse_d <class 'dict'>
- pdf_parse_d <class 'dict'>
- plain_parse_d <class 'dict'>
    - **all parse_d have the same structure to the dictionary**
    - dict_keys
        - 'file_path' (string representation of path to raw file saved at ```"output/formats/{format}/{index}.{suffix}"```),
        - 'text' (parsed text str),
        - 'abstract' (str),
        - 'size' (file size - bytes),
        - 'wc' (rough word count based on string.split() (int)),
        - 'url' (the url used to retrieve the file),
        - 'body_unique_score 
            - score based on union and diffrence in words between the abstract and parsed text. the Higher the score, the more original content in the full text max = 1 min = 0
        - 'ab_sim_score'
            - Score based on the count of words in the intersection between the abstract and parsed text, divided by the total union of unique words in the abstract and parsed text, the higher the score, the more similar the abstract is to the parsed text. Max 1, min 0
        - 'evaluation' 
            - TP/FP/ABS true positive, false positive or abstract, calculation based on word count, file size, abstract similarity and body unique score.
- content_text <class 'str'>
    - the "best" representation of full text from the available formats. XML, HTML, Plain text and PDF in that order of cleanliness. 
---
---
## Other Outputs
- **Medline Record Dictionaries**
    - these are stored as pickle objects for every row index in the dataframe. 
    - Medline dictionaries can be found at ```./output/medline/p/{index}.p```. 
    - You can use these dictionaries to reparse the metadata if there are fields you would like to include see possible fields [here](https://www.nlm.nih.gov/bsd/mms/medlineelements.html)
    - There is also a text version stored at ```./output/medline/txts/{index}.txt```
- **Crossref Record Dictionaries**
    - Similarly to Meline records, we also store crossref records as pickled dictionaries. 
    - These can be found at ```./output/crossref/p/{index}.p```
    - there are many fields (dictionary keys) that you can use to parse the crossred record. 
    - find our more about the crossref REST API [here](https://api.crossref.org/swagger-ui/index.html) 
- **Raw File Formats**
    - We try our best to offer a clear representation of the text but sometimes needs will differ from this approach.
    - Sometimes a project requires diffrent processing so we provide the raw files for you to apply your own parser on
    - In the ```retrieved_df2``` each row has 1/0 values in columns for each format, HTML, XML, PDF, Plain and PMC_TGZ
    - If there is a 1 in the desired format you can find the path to the raw file.  
        - ```retrieve_df2[index,{format}_parsed_d['file_path']```. 
    - Alternatively you can bulk parse all the available formats from their directories e.g.```./output/formats/html/{index}.html```. 
    - Each file is linked back to the dataframe using the uniq hexidecimal index, this is the same index used in the medline pickle and crossref pickle.
---


## Important - Please Read!
 Published literature can be subject to copyright with restrictions on redistribution. Users need to be mindful of the data storage requirements and how the derived products are presented and shared. Many publishers provide guidance on use of content for redistribution and use in research.

## Extra resources
You can find the Cadmus website - https://biomedicalinformaticsgroup.github.io/cadmus/

You can find a [Colab Notebook](https://colab.research.google.com/drive/1n3SK3_3dUpnF4MdJLWQy7PSndIAE85hK?usp=sharing) to get you started.

## FAQ

Q: What influences the performance of Cadmus?

A: There are two factors that influence the performance of Cadmus. The first one that highly influences the retrieval rate is one’s subscriptions to journals. The second one is the date range. Usually, Cadmus performs better on newer publications. This reflects the increased use of text mining formats and document web indexing to help with finding a given document.

Q:Tika failed three times in a row, I can not parse PDF format. What can I do ?

A:You can go to the following [website](https://repo1.maven.org/maven2/org/apache/tika/tika-server/1.24/), download 'tika-server-1.24.jar' and start it yourself.

Q:I ran two times the same query, the number of potential publications changed. Why?

A:If the number of potential publication changed by a lot please let us know [here](https://github.com/biomedicalinformaticsgroup/cadmus/issues), tell us about the query, the previous number and the new number.
If you noticed a small difference, most likely the APIs the system is using were busy and your request did not receive an answer this time. Give it some time and try to run again the same query using the extra parameter full_search = 'light' to update your result by looking again at the rows where the system did not find a content.

Q:I ran the same query as someone else and I got different retrieval result. Why?

A:The system is influenced by subscriptions beyond the api key. Maybe you do not have the same subsriptions as your colleague, if you run the system on a university computer you are likley to get a higher retrieval due to IP address whitelisting. Different univerisities will have different subscriptions and thus retrieval rates.

Q:Can I redistribute the data?

A:Published literature is subject to copyright and restrictions on redistribution. Users need to be mindful of the data storage requirements and how the derived products are presented and shared. Some pulishers will allow 100 character chunks to be redistributed without issue, others will not. Each time you use published data, you should provide a list of DOIs to users so that they can visit the original papers.  Derivitive data is treated diffrently, if you have processed the raw data and created something new (and the licesinging allows it) then you should be free to redistribute that in most cases. See [Creative commons licensing](https://creativecommons.org/licenses/by-nc-nd/3.0/us/legalcode) for more info.

Q:What's the difference between retrieved_df and retrieved_df2?

A:retrieved_df is a 'moving state' dataframe. Each time the system runs, it will store the information into retrieved_df at the row of interest.
retrieved_df2 is here to keep the information forever, once the system finished, retrieved_df2 will collect the newly retrieved records from retrieved_df to add them with previous run's retrieval.

Q:How can I remove Cadmus?

A: rm -rf cadmus

Q: I got the following error or a similar one: 'PermissionError: \[Errno\] 13 Permission denied: '/tmp/tika.log'', What can I do?

A: It seems that you are on a shared computer, you need to identify who is the owner of tika.log, using ls -l on the directory printed with your error. Once you know, ask one to change the permission so that you can read, write and execute tika.log as well. One way to do that is using the command 'chmod'.
