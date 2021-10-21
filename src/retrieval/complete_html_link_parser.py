from cadmus.src.retrieval.get_base_url import get_base_url
from cadmus.src.retrieval.html_link_from_meta import html_link_from_meta
from cadmus.src.retrieval.pdf_links_from_meta import pdf_links_from_meta
from cadmus.src.retrieval.explicit_pdf_links import explicit_pdf_links
from cadmus.src.retrieval.links_from_a_tags import links_from_a_tags
import bs4
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings("ignore")

# now draw together all the parsing functions above and apply to any html response
def complete_html_link_parser(response):
        link_list = []
    
        soup = BeautifulSoup(response.text, 'html')

        base_url = get_base_url(soup)
        # parsing html links from the html meta tags
        html_links = html_link_from_meta(soup)
        if html_links != []:
                link_list.extend(html_links)
        
        link_list.extend(pdf_links_from_meta(soup))
        link_list.extend(explicit_pdf_links(soup, base_url))
        link_list.extend(links_from_a_tags(soup, base_url))


        link_list = list(set(link_list))

        for i in range(len(link_list)):
                if len(link_list[i].split()) > 1:
                        link_list[i] = link_list[i].split()[0]
        
        return link_list