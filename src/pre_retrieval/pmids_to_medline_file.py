from Bio import Entrez, Medline
import time

def pmids_to_medline_file(date_name, pmid_list, email, api_key): 
    
    # this function uses a list of pmids to return medline files from NCBI using epost and efetch
    # the output is a file to parse using medline parser
    
    # The PMID list may be provided directly or it may have be retrieved by using a pubmed search. 
    # if the pubmed search was used then the date_name can be parsed from the results_d in the previous function
    # other wise, the PMID list has be provided from another source and we can need to make a new date_name
    
    # set the entrez variable set up for the group/project
    Entrez.email = email
    Entrez.tool = "genepopi_search_developer"
    Entrez.api_key = api_key    


    # post a joined list of the new pmids to the NCBI history server and save the search results.
    # NCBI's history server allows you to post once and then iteratively retrieve records without reposting
    # it also works better than sending a long URL (full of the pmids) which risks breaking

    # to do this we need to record the webenv and query_key to use in out e-fetch request
    
    # remove all duplicate pmids
    new_pmids = list(set(pmid_list))
    search_results = Entrez.read(Entrez.epost(db="pubmed", id=",".join(new_pmids)))

    web_env = search_results['WebEnv']
    query_key = search_results['QueryKey']

    # if the total count is greated than the max retieval then we will need to retrieve in batches.
    t_count = len(new_pmids)
    # 500 is the max batch size
    batch_size = 500

    # set the file name to store the medline records, i am using the date searched but you can change the name variable above to whatever you like
    out_handle = open(f"./output/medline/txts/{date_name}.txt", "w")

    # now lets use an efetch loop to retrieve medline records from our pmid list 
    # the start will be set by jumping from 0 to the final counts, in increments of the batch size
    for start in range(0,t_count,batch_size):
        # set the end number of retieval to be the smallest out of the total or start plus batch number of 
        end = min(t_count, start+batch_size)
        # give some feedback on the process
        print(f"Going to download record {start+1} to {end} out of {t_count} for search: {date_name}")
        # occasional server errors should be expected, this try:except block will allow 3 attempts to download each batch
        attempt = 0
        while attempt <= 3:
            attempt += 1
            try:
                # send a request to efetch pubmed db in the medline format, setting the start and end record, according to the pmid post on the history server 
                fetch_handle = Entrez.efetch(db="pubmed",rettype="medline",
                                             retmode="text",retstart=start,
                                             retmax=batch_size,
                                             webenv=web_env,
                                             query_key=query_key)
                attempt = 4
            # the except block will occur when there has been an error
            except:
                pass
        # the data read in from the respons is then written to the outhandle until the loop is complete and the handle is then closed.
        data = fetch_handle.read()
        fetch_handle.close()
        out_handle.write(data)
    out_handle.close()
    return f"./output/medline/txts/{date_name}.txt"