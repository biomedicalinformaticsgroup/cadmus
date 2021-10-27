# explicit full text PDF links

# sometimes there are pdf links in the metatags
def pdf_links_from_meta(soup):
    pdf_link_list = []
    
    meta_tags = soup.find_all('meta')
    if meta_tags:
        for meta in meta_tags:
            # check the name of the meta tag
            if meta.has_attr('name'):
                # now lets look for pdfs
                if ('citation_pdf_url' in meta['name']):
                    # sometimes there is a tag with the right name but not content so lets check that and save the content if present.
                    if meta.has_attr('content'):
                        pdf_link_list.append(meta['content'])
    return pdf_link_list