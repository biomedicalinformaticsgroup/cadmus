[![DOI:10.1101/2021.01.08.425887](http://img.shields.io/badge/DOI-10.1101/2025.08.29.671515-BE2536.svg)](https://doi.org/10.64898/2026.05.16.725623)
[![DOI](https://zenodo.org/badge/364367629.svg)](https://zenodo.org/badge/latestdoi/364367629)
[![PARADIGM](https://img.shields.io/badge/used_by:_%F0%9F%A7%AC_PARADIGM-ADD8E6)](https://paradigmgenomics.org/)
[![CoDiet](https://img.shields.io/badge/used_by:_%F0%9F%8D%8E_CoDiet-5AA764)](https://www.codiet.eu)

# ✍️📜 Cadmus
This project aims to build an automated full-text retrieval system for the generation of large biomedical corpora from published literature for research purposes.
Cadmus has been developed for use in non-commercial research. Use out with this remit is not recommended, nor is the intended purpose.

---

## 📚 Table of Contents
- [✍️📜 Cadmus](#️-cadmus)
  - [📚 Table of Contents](#-table-of-contents)
  - [📋 Requirements](#-requirements)
  - [⚙️ Installation](#️-installation)
  - [🚀 Get started](#-get-started)
  - [🔬 Storage and loading results](#-storage-and-loading-results)
  - [🔎 Output details](#-output-details)
  - [🗂️ Other Outputs](#️-other-outputs)
  - [🌍 Extra resources](#-extra-resources)
  - [⚠️ Important - Please Read!](#️-important---please-read)
  - [📝 Citing](#-citing)
  - [❓ FAQ](#-faq)
  - [👥 Code Contributors](#-code-contributors)
  - [📦 Version History](#-version-history)
    - [Version 0.3.16](#version-0316)
    - [Version 0.3.15](#version-0315)
    - [Version 0.3.14](#version-0314)
    - [Version 0.3.13](#version-0313)
    - [Version 0.3.12](#version-0312)
    - [Version 0.3.11](#version-0311)
    - [Version 0.3.10](#version-0310)
    - [Version 0.3.9](#version-039)
    - [Version 0.3.8](#version-038)
    - [Version 0.3.7](#version-037)

---

## 📋 Requirements

In order to run the code, you need a few things:

You need to have Java 7+ only if you are running older versions that required Tika; current Cadmus uses PyMuPDF for local PDF parsing.

You need to git clone the project and install it.

An API key from NCBI (this is used to search PubMed for articles using a search string or list of PubMed IDs; you can find more information [here](https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/)).

*Cadmus uses PyMuPDF (`pymupdf`) for local PDF parsing. No external Tika server is required.*

**Recommended requirements:**

An API key from Wiley, this key will allow you to get access to the OA and publications you or your institution has the right to access from Wiley. You can find more information [here](https://onlinelibrary.wiley.com/library-info/resources/text-and-datamining)

An API key from Elsevier, this key will allow you to get access to the OA and publications you or your institution has the right to access from Elsevier. You can find more information [here](https://dev.elsevier.com/)
Cadmus now stores data as Parquet files and uses DuckDB for efficient querying and MERGE-based upserts. For best results on macOS we recommend a conda-based Python environment.

Minimum runtime requirements:
- Python 3.8+ (3.11 tested)
- `pymupdf` (PyMuPDF) for local PDF parsing
- `duckdb` (recommended via conda)
- `pyarrow` for Parquet I/O

You will also need an NCBI API key to query PubMed (see https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/).

Optional but recommended API keys for higher retrieval rates:
- Wiley API key
- Elsevier API key (Elsevier/Scopus)

Note: Cadmus no longer requires Java or a Tika server — PDF parsing is performed with PyMuPDF.

---

## ⚙️ Installation
We recommend creating an isolated conda environment (particularly on macOS where DuckDB wheels are simplest via conda).

Using conda (recommended):

```bash
git clone https://github.com/biomedicalinformaticsgroup/cadmus.git
cd cadmus
conda create -n cadmus python=3.11 -y
conda activate cadmus
# install duckdb and other binary deps via conda
conda install -c conda-forge duckdb pyarrow -y
pip install -r requirements.txt
pip install -e .
```

Or using pip inside an existing environment:

```bash
git clone https://github.com/biomedicalinformaticsgroup/cadmus.git
cd cadmus
pip install -r requirements.txt
pip install -e .
```

---

## 🚀 Get started

The format we are using for the search term(s) is the same as the one for [PubMed](https://pubmed.ncbi.nlm.nih.gov/). You can first try your search term(s) on PubMed and then use the same search term(s) as input for cadmus `bioscraping`.

In order to create your corpora, you are going to use the function called `bioscraping`. The function is taking the following required parameters:

1. A PubMed query string or a Python list of PubMed IDs
2. An email address
3. Your NCBI_API_KEY
   
The function can also receive optional parameters.

1. wiley_api_key parameter allows Wiley to identify which publications you or your institution have the right to access. It will give you access to the OA publications that you would not get access to without the key. **RECOMMENDED**
2. elsevier_api_key parameter allows Elsevier to identify which publications you or your institution have the right to access. It will give you access to the OA publications that you would not normally have access to without the key. **RECOMMENDED**
3. The "start" parameter tells the function at which service we were before failure (e.g. crossref, doi, PubMed Central API, ...).
4. The "idx" parameter tells the function what is the last saved row index (article).

Start and idx are designed to be used when restarting cadmus after a program failure. When Cadmus is running, there is a repeated output feed at the top of the live output.  This line will show you the stage and index that your output dataframe was last saved in case of failure for whatever reason. By using these optional parameters, the program will pick off where it left off, saving you from starting the process from the beginning again.

5. "full_search", in case you want to check if a document became available since the last time you tried. "full_search" has three predefined values:

    - The default value is 'None'; the function only looks for the new articles since the last run.
    - 'light', the function looks for the new articles since the last run and retried the row where we did not get any format.
    - 'heavy', the function looks for the new articles since the last run and retried the row where it did not retrieve at least one tagged version (i.e. HTML or XML) in combination with the PDF format.  

6. The "keep_abstract" parameter has the default value 'True' and can be changed to 'False'. When set to 'True', our parsing will load any format from the beginning of the document. If changes to 'False', our parsing is trying to identify the abstract from any format and starts to extract the text after it. We are offering the option of removing the abstract, but we can not guarantee that our approach is more reliable for doing so. In case you would like to apply your own parsing method for removing the abstract, feel free to load any file saved during the retrieval available in the output folder: 
```"output/formats/{format}s/{index}.{suffix}.zip"```.  

You can now run `bioscraping` with the following example:

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

---

## 🔬 Storage and loading results

Cadmus persists metadata and parsed outputs into Parquet tables under `./storage/parquet/` and exposes DuckDB for queries and upserts. Core tables include: `articles`, `projects`, `file_artifacts`, `parsed_texts`, and `full_text_links`.

Quick example — use the `Storage` adapter to read the `articles` table:

```python
from cadmus.storage import Storage
s = Storage(root='./storage', duckdb_path='./storage/cadmus.duckdb')
s.init_tables()
df = s.query("SELECT * FROM articles LIMIT 10")
```

You can still access the raw parsed files under `./output/formats/{format}s/` (zipped text files), but using the `Storage` adapter and DuckDB is the recommended workflow for deduplication and efficient queries.

---

## 🔎 Output details

**retrieved_df**

The Metadata output is a pandas dataframe saved as a zip containing a JSON file.  
This is stored in the directory ```"./ouput/retrieved_df/retrieved_df2.json.zip"```. 
The dataframe columns are:
- pmid <class 'int64'>
    - PubMed ID. If you prefer to change the data type of PMIDs to <class 'str'>, you can use the following example: `metadata_retrieved_df.pmid = metadata_retrieved_df.pmid.astype(str)`
- pmcid <class 'float'>
    - PubMed Central ID.
- title <class 'str'>
- abstract <class 'str'>
  - Abstract (from PubMed metadata). 
- mesh <class 'list'>
  -  MeSH (Medical Subject Headings) provided by Medline.
- keywords <class 'list'>
  - This field contains largely non-MeSH subject terms that describe the content of an article. Beginning in January 2013, the author-supplied keywords.
- authors <class 'list'>
- journal <class 'str'>
- pub_type <class 'list'>
    - Publication type (from PubMed metadata).
- pub_date <class 'str'>
    - Publication date (from PubMed metadata).  
- doi <class 'str'>
- issn <class 'str'>
- crossref <class 'numpy.int64'>
    - 1/0 for the presence of a crossref record when searching on doi. 
- full_text_links <class 'dict'>
    - dict_keys:
        - 'cr_tdm' (list of crossref tdm links),
        - 'html_parse' (list of links parsed from HTML files),
        - 'pubmed_links' (list of links from "linkout" section on PubMed page, not including PMC).
- licenses <class 'list'>
- pdf <class 'numpy.int64'>
    - (1/0) for successful download of the PDF version. 
- xml <class 'numpy.int64'>
    - (1/0) for successful download of the XML version.
- html <class 'numpy.int64'>
    - (1/0) for successful download of the HTML version.
- plain <class 'numpy.int64'>
    - (1/0) for successful download of the plain text version. 
- pmc_tgz <class 'numpy.int64'>
    - (1/0) for successful download of PubMed Central Tar g-zip. 
- xml_parse_d <class 'dict'>
- html_parse_d <class 'dict'>
- pdf_parse_d <class 'dict'>
- plain_parse_d <class 'dict'>
    - **all parse_d have the same structure in the dictionary**
    - dict_keys:
        - 'file_path' (string representation of the path to the raw file saved at ```"output/formats/{format}s/{index}.{suffix}.zip"```),
        - 'size' (file size - bytes),
        - 'wc' (rough word count based on string.split() for the content text (int)),
        - 'wc_abs' (rough word count based on string.split() for the abstract (int)),
        - 'url' (the URL used to retrieve the file),
        - 'body_unique_score' 
            - Score based on the union and difference in words between the abstract and parsed text. The higher the score, the more original content in the full text, max = 1, min = 0.
        - 'ab_sim_score'
            - Score based on the count of words in the intersection between the abstract and parsed text, divided by the total union of unique words in the abstract and parsed text; the higher the score, the more similar the abstract is to the parsed text, max = 1, min = 0.
- content_text <class 'int'>
    - 0 if not retrieved, 1 otherwise.

The 'core' data and content text from the retrieved publications are stored in ```"./ouput/retrieved_parsed_files"```.
- In this directory, you can find 5 sub-directories: content_text, pdfs, htmls, xmls, and txts. Each format sub-directories contain the content of the files saved as a zip containing a txt file. 
- The content_text sub-directory, ```"./ouput/retrieved_parsed_files/content_text/*.txt.zip"```, contains the "best" representation of full text from the available formats. XML, HTML, Plain text, and PDF in that order of cleanliness. It is the place where the output is saved.

---

## 🗂️ Other Outputs
- **Medline Record Dictionaries**
    - These are stored as zip files containing a JSON file for every row index in the dataframe. 
    - Medline dictionaries can be found at ```./output/medline/json/{index}.json.zip```. 
    - You can use these dictionaries to reparse the metadata if there are fields you would like to include, see possible fields [here](https://www.nlm.nih.gov/bsd/mms/medlineelements.html).
    - There is also a text version stored at ```./output/medline/txts/medline_output.txt.zip```.
    - The edirect module and configuration files are stored in this directory following the 10,000 PMIDs limitation from the API.
- **Crossref Record Dictionaries**
    - Similarly to Meline records, we also store crossref records as zip files containing JSON dictionaries. 
    - These can be found at ```./output/crossref/json/{index}.json.zip```.
    - There are many fields (dictionary keys) that you can use to parse the crossref record. 
    - Find out more about the crossref REST API [here](https://api.crossref.org/swagger-ui/index.html).
- **Raw File Formats**
    - We try our best to offer a clear representation of the text, but sometimes needs will differ from this approach.
    - Sometimes a project requires different processing, so we provide the raw files for you to apply your own parser to.
    - In the ```retrieved_df2```, each row has 1/0 values in columns for each format, HTML, XML, PDF, Plain, and PMC_TGZ.
    - If there is a 1 in the desired format, you can find the path to the raw file:  
        - ```retrieve_df2[index,{format}_parsed_d['file_path']]```. 
    - Alternatively, you can bulk parse all the available formats from their directories, e.g.```./output/formats/html/{index}.html.zip```. 
    - Each zip file is linked back to the dataframe using the unique hexadecimal index, which is the same index used in the Medline JSON and crossref JSON.
- **esearch_results Record Dictionaries**
    - The directory keeps track of all the successful queries made for that output as a zip file containing a JSON dictionary. They are saved under ```./output/esearch_results/YYYY_MM_DD_HH_MM_SS.json.zip```.
    - The dictionary contains 4 keys:
      - date: date of the run with the format YYYY_MM_DD_HH_MM_SS.
      - search_term: the search terms or PMIDs you entered for that run.
      - total_count: number of new PMID candidates.
      - pmids: the list of PMIDs identified.

---

## 🌍 Extra resources

| Type | Resource |
|:-----:|:---:|
| Paper | [![DOI:10.1101/2021.01.08.425887](http://img.shields.io/badge/DOI-10.1101.2025.08.29.671515-BE2536.svg)](https://doi.org/10.64898/2026.05.16.725623) |
| Get started! | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1-ACwvyWLihroeV1lJcL7S1VyCiCIA4Ja?usp=sharing) [![Open in GitHub](https://img.shields.io/badge/GitHub-Open_in_GitHub-181717?logo=github)](https://github.com/omicsNLP/example_notebooks/blob/main/cadmus/Cadmus_Notebook_example_Colab_V3_16.ipynb) |
| Our cadmus Methods Extraction | [![Open in GitHub](https://img.shields.io/badge/GitHub-cadmus_methods_extraction-181717?logo=github)](https://github.com/biomedicalinformaticsgroup/cadmus_methods_extraction) |
| Our UMLS annotation pipeline | [![Open in GitHub](https://img.shields.io/badge/GitHub-ParallelPyMetaMap-181717?logo=github)](https://github.com/biomedicalinformaticsgroup/ParallelPyMetaMap) |
| Our PubMed abstract collection | [![Open in GitHub](https://img.shields.io/badge/GitHub-pm_abs_extr-181717?logo=github)](https://github.com/biomedicalinformaticsgroup/pm_abs_extr) |
| Our OA PMC full-text collection | [![Open in GitHub](https://img.shields.io/badge/GitHub-oa_pmc_extr-181717?logo=github)](https://github.com/biomedicalinformaticsgroup/oa_pmc_extr) |

</div>

---

## ⚠️ Important - Please Read!
Published literature can be subject to copyright with restrictions on redistribution. Users need to be mindful of the data storage requirements and how the derived products are presented and shared. Many publishers provide guidance on the use of content for redistribution and use in research.

---

## 📝 Citing

If you find this repository useful, please consider giving a star ⭐ and citation 📝:

```bibtex
@article {Campbell2026.05.16.725623,
	author = {Campbell, Jamie and Lain, Antoine D and Simpson, T Ian},
	title = {cadmus: a robust pipeline for scalable retrieval of full-text biomedical literature},
	elocation-id = {2026.05.16.725623},
	year = {2026},
	doi = {10.64898/2026.05.16.725623},
	publisher = {Cold Spring Harbor Laboratory},
	URL = {https://www.biorxiv.org/content/early/2026/05/19/2026.05.16.725623},
	eprint = {https://www.biorxiv.org/content/early/2026/05/19/2026.05.16.725623.full.pdf},
	journal = {bioRxiv}
}
```

---

## ❓ FAQ

Q: What influences the performance of Cadmus?

A: There are two factors that influence the performance of Cadmus. The first one that highly influences the retrieval rate is one’s subscriptions to journals. The second one is the date range. Usually, Cadmus performs better on newer publications. This reflects the increased use of text mining formats and document web indexing to help with finding a given document.


Q: PDF parsing fails. What can I do?

A: Cadmus uses PyMuPDF for PDF parsing. Ensure `pymupdf` is installed in your environment (e.g. `pip install pymupdf` or `conda install -c conda-forge pymupdf`). If parsing still fails, check the PDF for corruption or try extracting pages with an external tool.

Q: I ran the same query twice, and the number of potential publications changed. Why?

A: If the number of potential publications changed a lot, please let us know [here](https://github.com/biomedicalinformaticsgroup/cadmus/issues), tell us about the query, the previous number, and the new number.
If you noticed a small difference, most likely the APIs the system is using were busy, and your request did not receive an answer this time. Give it some time and try to run the same query again using the extra parameter full_search = 'light' to update your result by looking again at the rows where the system did not find content.

Q: I ran the same query as someone else, and I got a different retrieval result. Why?

A: The system is influenced by subscriptions beyond the API key. Maybe you do not have the same subscriptions as your colleague. If you run the system on a university computer, you are likely to get a higher retrieval due to IP address whitelisting. Different universities will have different subscriptions and thus retrieval rates.

Q: Can I redistribute the data?

A: Published literature is subject to copyright and restrictions on redistribution. Users need to be mindful of the data storage requirements and how the derived products are presented and shared. Some publishers will allow 100-character chunks to be redistributed without issue; others will not. Each time you use published data, you should provide a list of DOIs to users so that they can visit the original papers.  Derivative data is treated differently. If you have processed the raw data and created something new (and the licensing allows it), then you should be free to redistribute that in most cases. See [Creative Commons licensing](https://creativecommons.org/licenses/by-nc-nd/3.0/us/legalcode) for more info.

Q: What's the difference between retrieved_df and retrieved_df2?

A: retrieved_df is a 'moving state' dataframe. Each time the system runs, it will store the information in retrieved_df at the row of interest.
retrieved_df2 is here to keep the information forever. Once the system is finished, retrieved_df2 will collect the newly retrieved records from retrieved_df to add them to the previous run's retrieval.

Q: How can I remove Cadmus?

A: 'pip uninstall cadmus' to remove from Python and 'rm -rf cadmus' in bash to remove it from the directory.


Q: I got a permission error related to PDF parsing logs. What can I do?

A: Ensure the user running Cadmus has write permission to the temp/log directories. Fix permissions with `chmod` or run Cadmus under an account that can write to `/tmp` or the configured log path.

---

## 👥 Code Contributors

<p align="center">
  <kbd>
    <a href="https://github.com/jamcam11">
      <img src="https://drive.google.com/uc?id=1XUSKj3LC2fRdNksUbDjAyUCwG6xcFjck" width="90" height="90" style="border-radius:50%;">
    </a><br>
    👉 <strong><a href="https://github.com/jamcam11" style="text-decoration:none; color:inherit;">Jamie</a></strong>
  </kbd>
  &nbsp;&nbsp;
  <kbd>
    <a href="https://github.com/Antoinelfr">
      <img src="https://drive.google.com/uc?id=1FH6XRJuam6eMuCzwWXBAIdDacIw8PFiu" width="90" height="90" style="border-radius:50%;">
    </a><br>
    👉 <strong><a href="https://github.com/Antoinelfr" style="text-decoration:none; color:inherit;">Antoine</a></strong>
  </kbd>
  &nbsp;&nbsp;
  <kbd>
    <a href="https://github.com/tisimpson">
      <img src="https://drive.google.com/uc?id=17RNcUtafryCq8sbUhaDLiRwo_KpMCAfh" width="90" height="90" style="border-radius:50%;">
    </a><br>
    👉 <strong><a href="https://github.com/tisimpson" style="text-decoration:none; color:inherit;">Ian</a></strong>
  </kbd>
</p>

---

## 📦 Version History

### Version 0.3.16
-> Corrected typos across the README and in-code comments.

-> Removed `from cadmus import display_export_path`, now added directly to the environment.

-> Improved code structure and formatting for better readability and maintainability.

-> Enhanced and reorganised the README for clarity.

-> Fixed issues related to the pip build process. 

### Version 0.3.15
-> Add the parameters 'colab1' and 'colab2' to be able to run an example Notebook on Google Colab and bypass the restriction on running the pipeline function on the bash system from the terminal.

-> Fixing parsed_to_df function.

### Version 0.3.14
-> Add the keyword field from the Medline file to the result.

-> Fixed data type, when reading the Medline file, in case of add_mesh.

-> Fixed code where 1 article was missing if using a list of PMIDs as an update.

### Version 0.3.13
-> Since Crossref retired the API key feature, Elsevier and Wiley identify the author of the publication request. wiley_api_key and elsevier_api_key optional parameters have been added as input parameters. These are not mandatory parameters, but they greatly increase the retrieval rate as they give access to Wiley and Elsevier publications, respectively. 

### Version 0.3.12
-> Applied some changes in clean_up_dir.py.

-> Removed the 'click_through_api_key' mandatory parameter since Crossref is retiring this feature.

### Version 0.3.11
-> Fixed a typo in parse_link_retrieval.py.

-> Applied some changes in clean_up_dir.py.

### Version 0.3.10
-> Add a fixed version to the request library from the setup file to work with our code.

### Version 0.3.9
-> Fixed code according to the new script for Edirect retrieval.

-> Fixed typos in the README.

-> Remove the limitation to the minimum file size of the retrieved_df2.

-> Fixed code error of duplicate pmids (this was not impacting previous results, but added an extra unnecessary row when using the update parameter).

### Version 0.3.8
-> For disk storage purposes, we now zip all the files retrieved/generated from cadmus in order to be less consuming.

-> We propose more restart options in case of failure.

-> We updated the clean directory function. Sometimes the .tgz files downloaded had .tmp as an extension.

### Version 0.3.7
-> Moved away from pickle objects to convert to JSON files. The previous output will be automatically changed to the new format at the beginning of the next run.

-> PMID type changed from str to int64.

-> PUB_DATE moved from datetime.time to str.

-> Return of the esearch_results files. The files are saved under the format YYYY_MM_DD_HH_MM_SS.json. They contain a dictionary with the date the query was run, the query, the number of PMIDs cadmus will look for, and the list of the newly identified PMIDs.

-> Update the cleanup function to remove unnecessary files.

---
