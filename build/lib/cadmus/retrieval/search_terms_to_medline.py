from cadmus.retrieval.edirect import pipeline
# we can use the search terms provided to query pubmed using edirect esearch.
# This will provide us with a text file of papers in medline format
def search_terms_to_medline(query_string):
    print(f'searching pubmed for : {query_string}')
    # send the query string by esearch then retrieve by efetch in medline format
    search_results = pipeline((f'esearch -db pubmed -query "{query_string}" | efetch -format medline'))
    with open('./output/medline/txts/medline_output.txt', 'w') as file:
        file.write(search_results)
    print('Medline Records retrieved and saved')
