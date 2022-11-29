# explicit full text HTML links

# sometimes the full text html link is present in the doc metadata
# input is a soup object
def html_link_from_meta(soup):
    # were looking for all html links
    html_link_list = []
    # check for all the meta tags
    meta_tags = soup.find_all('meta')
    
    if meta_tags:
        for meta in meta_tags:
            # check the name of the meta tag
            if meta.has_attr('name'):
                # there may be more options to add to this list but this is a start
                if ('citation_fulltext_html_url' in meta['name']) or ('citation_full_html_url' in meta['name']):
                   # sometimes there is a tag with the right name but not content so lets check that and save the content if present.
                    if meta.has_attr('content'):
                        html_link_list.append(meta['content'])
    return html_link_list