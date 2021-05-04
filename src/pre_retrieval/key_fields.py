import bs4
from bs4 import BeautifulSoup
import datetime
import pandas as pd

def key_fields(crossref_dict, doi_list, pmid_doi, pmcid, is_list):
    # now we want to parse out the critical data for the crossref records

    # we'll store the output in a parse dictionary
    parse_d = {}
    
    pmid = str()
    pmcid_loop = str()
    # we'll loop through the crossref_dict
    for index, r_dict in crossref_dict.items():        
            message = r_dict['message']
            
            
            #lets start parsing out the key variables we want from the metadata
            doi = message.get('DOI')
            # once we have the doi we can cross check that against the lists of pmids and pmcids from the NCBI id converter to fill in those ids.
            if doi.lower() in [x.lower() for x in doi_list]:
                for i in range(len(doi_list)):
                    if doi.lower() == doi_list[i].lower():
                        doi = doi_list[i]
                        pmid = pmid_doi[i]
                        pmcid_loop = pmcid[i]
                    else:
                        pass
            else:
                pmid = None
                pmcid_loop = None
                
            #lets start parsing out the key variables we want from the metadata                
            licenses = message.get('license')
            # now the full text links
            links = message.get('link')
            
            # we use the is_list variable to say whether we are using the list of dois to generate missing metadata
            # when false we can skip this stage and just take the licenses and full text links
            # when true we can try to populate more fields from the crossref metadata
            if is_list == True:
                pub_type = message.get('type')
                title = message.get('title')[0]
                issn= message.get("ISSN")


                # abstracts are presesented as xml and can need a simple bit of cleaning
                abstract = message.get('abstract')
                if abstract:
                    soup = BeautifulSoup(abstract)
                    abstract = soup.get_text(' ')

                # author lists need to be unpacked    
                author = message.get('author')
                # use list comprehension on the author dictionary to parse out the names
                author_list = [f"{author_dict.get('family')}, {author_dict.get('given')}" for author_dict in author]
                # the journal will be absent for these preprints so we can set it to biorxiv
                journal = message.get('container-title')

                # the pubdate is dependent on when it was uploaded
                date = message.get('created')
                y,m,d = date['date-parts'][0]
                # convert the date into a datetime object
                date = datetime.date(int(y),int(m),int(d))
                # now add each record to the parse d
                parse_d.update({index:{'doi':doi,
                                       'pmid':pmid,
                                       'pmcid': pmcid_loop,
                                       'issn':issn,
                                       'pub_type':pub_type,
                                       'title':title,
                                       'abstract':abstract,
                                       'journal':journal,
                                       'authors':author_list,
                                       'pub_date':date,
                                       'licenses': licenses,
                                       'links':links}})
            else:
                parse_d.update({index:{'doi':doi,
                                       'pmcid': pmcid_loop, # ? needed
                                       'licenses': licenses,
                                       'links':links}})

    # finally we'll store the parse dictionary as our crossref metadata master dataframe
    cr_df = pd.DataFrame.from_dict(parse_d, orient = 'index')
    return cr_df