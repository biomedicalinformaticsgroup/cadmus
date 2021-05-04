from urllib.parse import urlparse
import re
# generic link parsing from the body of HTML

def links_from_a_tags(soup, base_url):
    link_list = []
    # build a compiled regex 
    regex = re.compile(r"/content/.*/pdf/|/content/.*/doi/|full-text|full.pdf|advance-article|articles-pdf")
    
    # looks for all the 'a' tags
    for link_tag in soup.find_all('a'):
        # get the actual link from the 'a' tag
        current_link = link_tag.get('href')

        # if there is a link
        if current_link:
            # look for any of the regex patterns within the link
            if regex.search(current_link):
                # if there is a match make sure the link is complete before we add it to the return list
                if current_link.startswith('/'):
                    if base_url is not None:
                        # we can derive the root of the link from the request URL
                        parse_object = urlparse(base_url)
                        # we then build the full URL from all the parts (current link at the end)
                        current_link = f'{parse_object.scheme}://{parse_object.netloc}{current_link}'
                        # add to the return list
                        link_list.append(current_link)
                # if the link starts with http then its already a full link
                elif current_link.startswith('http'):
                    link_list.append(current_link)
            
    return link_list