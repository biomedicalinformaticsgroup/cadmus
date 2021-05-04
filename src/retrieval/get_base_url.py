from urllib.parse import urlparse
# getting a base URL

# to work with some of the links we need to build full links/URL from relative links.
# in order to do this we need to establish the base url to add as a prefix for the relative links

# the input for our function is a html soup object
def get_base_url(soup):   
    # set the url as none to begin with
    url = None
    
    # there are a series of tags that might house the base url, 
    # i have found a few, shown below, but there may be more to add if this is not good enough.
    
    # start by looking for all the meta tags with the specific attribute, if present, extract the content of the tag
    tag = soup.find('meta', {'name':'citation_public_url'})
    if tag:
        url = tag.attrs.get('content')
        if url == None:
            # when that doesn't work then try another attribute
            tag = soup.find('meta', {'name':'citation_full_html_url'})
            if tag:
                url = tag.attrs.get('content')
                if url == None:
                    # when that doesn't work then try another attribute
                    tag = soup.find('meta', {'property':"og:url"})
                    if tag:
                        url = tag.attrs.get('content')
                        if url == None:
                            # when that doesn't work then try another attribute
                            tag = soup.find('link', {'rel':"canonical"})
                            if tag:
                                url = tag.attrs.get('content')
    
    # if we have one of the URLs above we can parse it and extract the base URL
    if url != None:
        parse_object = urlparse(url)
        base_url = f'{parse_object.scheme}://{parse_object.netloc}'
        return base_url
    else:
        # default return will be a None value
        return url