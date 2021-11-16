import bs4
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings("ignore")
# This function takes the requests response for each PMID sent to pubmed.
# We then parse out each link from the linkout section.

def pubmed_linkout_parse(index, retrieval_df, response):
    
    # the main output is the link list parsed out of the hmtl
    link_list = []
    # read the hmtl into a beautiful soup object
    soup = BeautifulSoup(response.text, 'html')
    
    # lets check the linkout section of the soup object for any 'a' (link) tags
    linkout_links = soup.find_all('a',{'data-ga-action':'Full Text Sources'})
    if linkout_links:
        # if there are any links, parse out the URL and add it to our link list for this index
        for link in linkout_links:
            url = link.get('href')
            if url is not None:
                # we don't want any PMC articles due to copyright issues, or the clinical key links because they are useless.
                if 'clinicalkey' in url or 'pmc' in url:
                    pass
                else:
                    link_list.append(url)
            else:
                # no links, move on
                pass
    else:
        # no linkout links
        pass
    
    # now lets do the same for the html body links which have a slightly different attribute 
    body_links = soup.find_all('a',{'data-ga-category':'full_text'})
    if body_links:
        for link in body_links:
            url = link.get('href')
            if url is not None:
                # we don't want any PMC articles due to copyright issues, or the clinical key links because they are useless.
                if 'clinicalkey' in url or 'pmc' in url:
                    pass
                else:
                    link_list.append(url)
            else:
                # no links, move on
                pass
    else:
        # no body links, move on
        pass
        
    # now remove any duplicate links
    link_list = list(set(link_list))
    # in case of two strings keep only the first one
    for i in range(len(link_list)):
        if len(link_list[i].split()) > 1:
            link_list[i] = link_list[i].split()[0]

    # now lets add the link list to our dictionary of full text links for the appropriate article.
    full_text_link_d = retrieval_df.loc[index, 'full_text_links']
    full_text_link_d.update({'pubmed_links':link_list})
    retrieval_df.at[index, 'full_text_links'] = full_text_link_d


    return retrieval_df