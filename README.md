# Cadmus [![DOI](https://zenodo.org/badge/364367629.svg)](https://zenodo.org/badge/latestdoi/364367629)
This project aims to build an automated full-text retrieval system for the generation of large biomedical corpora from published literature for research purposes.
Cadmus has been developed for use in non-commercial research. Use out with this remit is not recommended nor is the intended purpose.

## Requirements

In order to run the code, you need a few things:

You need to have Java 7+.

You need to git clone the project and install it.

An API key from NCBI (this is used to search PubMed for articles using a search string or list of PubMed IDs, you can find more information [here](https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/)).

*In case you are running cadmus on a shared machine, you need to terminate all the tika instances present on the tmp directory if you are not the owner of the instances so cadmus can restart them for you.*

**Recommended requirements:**

An API key from Wiley, this key will allow you to get access to the OA and publications you or your institution have the right to access from Wiley. You can find more information [here](https://onlinelibrary.wiley.com/library-info/resources/text-and-datamining)

An API key from Elsevier, this key will allow you to get access to the OA and publications you or your institution have the right to access from Elsevier. You can find more information [here](https://dev.elsevier.com/)


## Installation
Cadmus has a number of dependencies on other Python packages, it is recommended to install it in an isolated environment.

`git clone https://github.com/biomedicalinformaticsgroup/cadmus.git`

`pip install ./cadmus`

## Get started

The format we are using for the search term(s) is the same as the one for [PubMed](https://pubmed.ncbi.nlm.nih.gov/). You can first try your search term(s) on PubMed and then use the same search term(s) as input for cadmus `bioscraping`.

In order to create your corpora you are going to use the function called `bioscraping`. The function is taking the following required parameters:

1. A PubMed query string or a Python list of PubMed IDs
2. An email address
3. Your NCBI_API_KEY
   
The function can also receive optional parameters.

1. wiley_api_key parameter allows Wiley to identify which publications you or your institution have the right to access. It will give you access to the OA publications that without the key you would not get access to. RECOMMENDED
2. elsevier_api_key parameter allows Elsevier to identify which publications you or your institution have the right to access. It will give you access to the OA publications that without the key you would not get access to. RECOMMENDED
3. The "start" parameter tells the function at which service we were before failure (e.g. crossref, doi, PubMed Central API. . .).
4. The "idx" parameter tells the function what is the last saved row index (article).

Start and idx are designed to use when restarting cadmus after a program failure. When Cadmus is running, there is a repeated output feed at the top of the live output.  This line will show you the stage and index that your output dataframe was last saved in case of failure for whatever reason. By using these optional parameters, the program will take off where it left off, saving you from starting the process from the beginning again.

5. "full_search", in case you want to check if a document became available since the last time you tried. "full_search" has three predefined values:

    - The default value is 'None', the function only looks for the new articles since the last run.
    - 'light', the function looks for the new articles since the last run and re-tried the row where we did not get any format.
    - 'heavy', the function looks for the new articles since the last run and re-tried the row where it did not retrieve at least one tagged version (i.e. html or xml) in combination with the pdf format.  

6. The "keep_abstract" parameter has the default value 'True' and can be changed to 'False'. When set to 'True', our parsing will load any format from the beginning of the document. If changes to 'False', our parsing is trying to identify the abstract from any format and starts to extract the text after it. We are offering the option of removing the abstract but we can not guarantee that our approach is the more reliable for doing so. In case you would like to apply your own parsing method for removing the abstract feel free to load any file saved during the retrieval available in the output folder: 
```"output/formats/{format}s/{index}.{suffix}.zip"```.  

You need to set the export path before every use so that cadmus is able to retrieve more than 10 000 records from NCBI. For that, we offer a function called `display_export_path`. You just need to call this function and copy past the result into your terminal before calling `bioscraping`. 

```python
from cadmus import display_export_path
display_export_path()
```

The result should look like:
```python
export PATH=${PATH}:YOUR_WORKING_DIRECTORY/output/medline/edirect
```

After copying and pasting the above export into your terminal you can now run `bioscraping` with the following example:

**Minimum requirements:**
```python
from cadmus import bioscraping
bioscraping(
    INPUT, #type str
    EMAIL, #type str
    NCBI_API_KEY #type str
    )
```
**Minimum recommended requirements:**
```python
from cadmus import bioscraping
bioscraping(
    INPUT, #type str
    EMAIL, #type str
    NCBI_API_KEY, #type str
    wiley_api_key = YOUR_WILEY_API_KEY, #type str
    elsevier_api_key = YOUR_ELSEVIER_API_KEY #type str
    )
```

## Load the result

The output from cadmus is a directory with the content text of each retrieved publication saved as a zip file containing a txt file, you can find the files here: ```"./ouput/retrieved_parsed_files/content_text/*.txt.zip"```. It also provides the metadata saved as a zip file containing a JSON file and a zip file containing a tsv file. In order to load the metadata you can use the following lines of code.

```python
import zipfile
import json
import pandas as pd
with zipfile.ZipFile("./output/retrieved_df/retrieved_df2.json.zip", "r") as z:
    for filename in z.namelist():
        with z.open(filename) as f:
            data = f.read()
            data = json.loads(data)


f.close()
z.close()
metadata_retrieved_df = pd.read_json(data, orient='index')
metadata_retrieved_df.pmid = metadata_retrieved_df.pmid.astype(str)
```

Here is a helper function you can call to generate a DataFrame with the same index as the one used for the metadata and the content text. The content text is the "best" representation of full text from the available formats. XML, HTML, Plain text, and PDF in that order of cleanliness. It is advised to keep the result somewhere else than in the output directory, as the DataFrame gets bigger the function takes more time to run. 

```python
from cadmus import parsed_to_df
retrieved_df = parsed_to_df(path = './output/retrieved_parsed_files/content_text/')
```

As default we assume the directory to the files is ```"./ouput/retrieved_parsed_files/content_text/``` please change the parameter 'path' otherwise.

---
## Output details

**retrieved_df**

The Metadata output is a pandas dataframe saved as a zip containing a JSON file.  
This is stored in the directory ```"./ouput/retrieved_df/retrieved_df2.json.zip"```. 
The dataframe columns are:
- pmid <class 'int64'>
    - PubMed id. If you prefer to change the data type of PMIDs to <class 'str'> you can use the following example: `metadata_retrieved_df.pmid = metadata_retrieved_df.pmid.astype(str)`
- pmcid <class 'float'>
    - PubMed Central id.
- title <class 'str'>
- abstract <class 'str'>
  - Abstract (from PubMed metadata). 
- mesh <class 'list'>
  -  MeSH (Medical Subject Headings) provided by Medline.
- keywords <class 'list'>
  - This field contains largely non-MeSH subject terms that describe the content of an article. Beginning in January 2013, author-supplied keywords.
- authors <class 'list'>
- journal <class 'str'>
- pub_type <class 'list'>
    - Publication type (from PubMed metadata).
- pub_date <class 'str'>
    - Publication date (from PubMed metadata).  
- doi <class 'str'>
- issn <class 'str'>
- crossref <class 'numpy.int64'>
    - 1/0 for the presence of crossref record when searching on doi. 
- full_text_links <class 'dict'>
    - dict_keys:
        - 'cr_tdm' (list of crossref tdm links),
        - 'html_parse' (list of links parsed from html files),
        - 'pubmed_links' (list of links from "linkout" section on PubMed page, not including PMC).
- licenses <class 'list'>
- pdf <class 'numpy.int64'>
    - (1/0) for successful download of the pdf version. 
- xml <class 'numpy.int64'>
    - (1/0) for successful download of the xml version.
- html <class 'numpy.int64'>
    - (1/0) for successful download of the html version.
- plain <class 'numpy.int64'>
    - (1/0) for successful download of the plain text version. 
- pmc_tgz <class 'numpy.int64'>
    - (1/0) for successful download of Pubmed Central Tar g-zip. 
- xml_parse_d <class 'dict'>
- html_parse_d <class 'dict'>
- pdf_parse_d <class 'dict'>
- plain_parse_d <class 'dict'>
    - **all parse_d have the same structure to the dictionary**
    - dict_keys:
        - 'file_path' (string representation of the path to the raw file saved at ```"output/formats/{format}s/{index}.{suffix}.zip"```),
        - 'size' (file size - bytes),
        - 'wc' (rough word count based on string.split() for the content text (int)),
        - 'wc_abs' (rough word count based on string.split() for the abstract (int)),
        - 'url' (the url used to retrieve the file),
        - 'body_unique_score' 
            - Score based on union and difference in words between the abstract and parsed text. The higher the score, the more original content in the full text, max = 1, min = 0.
        - 'ab_sim_score'
            - Score based on the count of words in the intersection between the abstract and parsed text, divided by the total union of unique words in the abstract and parsed text, the higher the score, the more similar the abstract is to the parsed text, max = 1, min = 0.
- content_text <class 'int'>
    - 0 if not retrieved 1 otherwise.

The 'core' data and content text from the retrieved publications are stored here:
- **retrieved_parsed_files**
    - In this directory, you can find 5 sub-directories: content_text, pdfs, htmls, xmls, txts. Each format sub-directories contains the content of the files saved as a zip containing a txt file. 
    - The content_text sub-directory, ```"./ouput/retrieved_parsed_files/content_text/*.txt.zip"```, contains the "best" representation of full text from the available formats. XML, HTML, Plain text, and PDF in that order of cleanliness. It is the place where the output is saved.
---

## Other Outputs
- **Medline Record Dictionaries**
    - These are stored as zip files containing a JSON file for every row index in the dataframe. 
    - Medline dictionaries can be found at ```./output/medline/json/{index}.json.zip```. 
    - You can use these dictionaries to reparse the metadata if there are fields you would like to include see possible fields [here](https://www.nlm.nih.gov/bsd/mms/medlineelements.html).
    - There is also a text version stored at ```./output/medline/txts/medline_output.txt.zip```.
    - The edirect module and configuration files are stored in this directory following the 10 000 PMIDs limitation from the API.
- **Crossref Record Dictionaries**
    - Similarly to Meline records, we also store crossref records as zip files containing JSON dictionaries. 
    - These can be found at ```./output/crossref/json/{index}.json.zip```.
    - There are many fields (dictionary keys) that you can use to parse the crossred record. 
    - Find out more about the crossref REST API [here](https://api.crossref.org/swagger-ui/index.html).
- **Raw File Formats**
    - We try our best to offer a clear representation of the text but sometimes needs will differ from this approach.
    - Sometimes a project requires different processing so we provide the raw files for you to apply your own parser on.
    - In the ```retrieved_df2``` each row has 1/0 values in columns for each format, HTML, XML, PDF, Plain, and PMC_TGZ.
    - If there is a 1 in the desired format you can find the path to the raw file:  
        - ```retrieve_df2[index,{format}_parsed_d['file_path']]```. 
    - Alternatively, you can bulk parse all the available formats from their directories e.g.```./output/formats/html/{index}.html.zip```. 
    - Each zip file is linked back to the dataframe using the unique hexadecimal index, this is the same index used in the Medline JSON and crossref JSON.
- **esearch_results Record Dictionaries**
    - The directory keeps track of all the successful queries made for that output as a zip file containing a JSON dictionary. They are saved under ```./output/esearch_results/YYYY_MM_DD_HH_MM_SS.json.zip```.
    - The dictionary contains 4 keys:
      - date: date of the run with the format YYYY_MM_DD_HH_MM_SS.
      - search_term: the search terms or PMIDs you entered for that run.
      - total_count: number of new PMID candidates.
      - pmids: the list of PMIDs identified.
---


## Important - Please Read!
 Published literature can be subject to copyright with restrictions on redistribution. Users need to be mindful of the data storage requirements and how the derived products are presented and shared. Many publishers provide guidance on the use of content for redistribution and use in research.

 ## Extra resources
You can find the Cadmus website at the following https://biomedicalinformaticsgroup.github.io/cadmus/

You can find a [Colab Notebook](https://colab.research.google.com/drive/1-ACwvyWLihroeV1lJcL7S1VyCiCIA4Ja?usp=sharing) to get you started. 

 <!--  Here is our library forthe Pubmed Central Open Access Corpus Generation

Here is our library for the Pubmed Abstract Corpus Generation --> 

## Citing

Please indicate which version of cadmus you used.

Jamie Campbell, Antoine Lain, & Ian Simpson. (2021). biomedicalinformaticsgroup/cadmus: First Release of Cadmus (v1.0.0). Zenodo. https://doi.org/10.5281/zenodo.5618052

## FAQ

Q: What influences the performance of Cadmus?

A: There are two factors that influence the performance of Cadmus. The first one that highly influences the retrieval rate is one’s subscriptions to journals. The second one is the date range. Usually, Cadmus performs better on newer publications. This reflects the increased use of text mining formats and document web indexing to help with finding a given document.

Q:Tika failed three times in a row, I can not parse PDF format. What can I do?

A:You can go to the following [website](https://repo1.maven.org/maven2/org/apache/tika/tika-server/1.24/), download 'tika-server-1.24.jar' and start it yourself.

Q:I ran two times the same query, and the number of potential publications changed. Why?

A:If the number of potential publications changed by a lot please let us know [here](https://github.com/biomedicalinformaticsgroup/cadmus/issues), tell us about the query, the previous number, and the new number.
If you noticed a small difference, most likely the APIs the system is using were busy and your request did not receive an answer this time. Give it some time and try to run again the same query using the extra parameter full_search = 'light' to update your result by looking again at the rows where the system did not find content.

Q:I ran the same query as someone else and I got a different retrieval result. Why?

A:The system is influenced by subscriptions beyond the API key. Maybe you do not have the same subscriptions as your colleague, if you run the system on a university computer you are likely to get a higher retrieval due to IP address whitelisting. Different universities will have different subscriptions and thus retrieval rates.

Q:Can I redistribute the data?

A:Published literature is subject to copyright and restrictions on redistribution. Users need to be mindful of the data storage requirements and how the derived products are presented and shared. Some publishers will allow 100-character chunks to be redistributed without issue, others will not. Each time you use published data, you should provide a list of DOIs to users so that they can visit the original papers.  Derivative data is treated differently, if you have processed the raw data and created something new (and the licensing allows it) then you should be free to redistribute that in most cases. See [Creative commons licensing](https://creativecommons.org/licenses/by-nc-nd/3.0/us/legalcode) for more info.

Q:What's the difference between retrieved_df and retrieved_df2?

A:retrieved_df is a 'moving state' dataframe. Each time the system runs, it will store the information in retrieved_df at the row of interest.
retrieved_df2 is here to keep the information forever, once the system is finished, retrieved_df2 will collect the newly retrieved records from retrieved_df to add them to the previous run's retrieval.

Q:How can I remove Cadmus?

A: 'pip uninstall cadmus' to remove from python and 'rm -rf cadmus' in bash to remove it from the directory.

Q: I got the following error or a similar one: 'PermissionError: \[Errno\] 13 Permission denied: '/tmp/tika.log'', What can I do?

A: It seems that you are on a shared computer, you need to identify who is the owner of tika.log, using ls -l on the directory printed with your error. Once you know, ask one to change the permission so that you can read, write and execute tika.log as well. One way to do that is using the command 'chmod'. You should also 'chmod' the following '/tmp/tika-server.log'

## Version

### Version 0.3.15
-> Add the parameters 'colab1' and 'colab2' to be able to run an example Notebook on Google Colab and bypass the restriction on runing the pipeline function on the bash system from the terminal.

-> Fixing parsed_to_df function.

### Version 0.3.14
-> Add the keyword field from the Medline file to the result.

-> Fixed data type, when reading the Medline file, in case of add_mesh.

-> Fixed code where 1 article was missing if using a list of PMIDs as an update.

### Version 0.3.13
-> Since Crossref retired the API key feature to let Elsevier and Wiley identified the author of the publication request. wiley_api_key and elsevier_api_key optional parameters have been added as input parameters. These are not mandatory parameters but increase greatly the retrieval rate as they give access to Wiley and Elsevier publications respectively. 

### Version 0.3.12
-> Applied some changes in clean_up_dir.py.

-> Removed the 'click_through_api_key' mandatory parameter since Crossref is retiring this feature.

### Version 0.3.11
-> Fixed a typo in parse_link_retrieval.py.

-> Applied some changes in clean_up_dir.py.

### Version 0.3.10
-> Add a fixed version to the request library from the setup file to work with our code.

### Version 0.3.9
-> Fixed code according to the new script for edrirect retrieval.

-> Fixed typos in the README.

-> Remove the limitation to the minimum file size of the retrieved_df2.

-> Fixed code error of duplicate pmids (this was not impacting previous results but added an extra unnecessary row when using the update parameter).

### Version 0.3.8
-> For disk storage purposes, we now zip all the files retrieved/generated from cadmus in order to be less consuming.

-> We propose more restart options in case of failure.

-> We updated the clean directory function. Sometimes the tgz files downloaded had .tmp as an extension.

### Version 0.3.7
-> Moved away from pickle objects to convert to JSON files. The previous output will be automatically changed to the new format at the beginning of the next run.

-> PMID type changed from str to int64.

-> PUB_DATE moved from datetime.time to str.

-> Return of the esearch_results files. The files are saved under the format YYYY_MM_DD_HH_MM_SS.json. They contain a dictionary with the date the query was run, the query, the number of PMIDs cadmus will look for, and the list of the newly identified PMIDs.

-> Update the clean up function to remove unnecessary files.
