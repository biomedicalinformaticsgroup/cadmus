import bs4
from bs4 import BeautifulSoup
 # a brief function for when there is no content type in the headers
def doctype(soup):
    items = [item for item in soup.contents if isinstance(item, bs4.Doctype)]
    return items[0] if items else None