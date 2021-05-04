from urllib.parse import urlparse
# the other main place to look for pdf links is links with PDF in the 'span' assocaited with the links ('a' tags)
def explicit_pdf_links(soup, base_url):
    # we'll store all our pdf links in this list and return at the end
    pdf_link_list = []
     
    # looks for all the 'a' tags
    for link_tag in soup.find_all('a'):
        # When a PDF link is provided, there is almost always "PDF" in the span so lets start by looking at text assoc with the link.
        if ('pdf' or 'download this article') in link_tag.text.lower():
            # if found then get the url using the href value
            current_link = link_tag.get('href')
            # make sure its not none then complete for relative links
            if current_link:
                # check to see if its a relative link
                if current_link.startswith('/'):
                    if base_url is not None:
                        # we can build the link by parsing the request URL
                        parse_object = urlparse(base_url)
                        # we then build the full URL from all the parts (current link at the end)
                        current_link = f'{parse_object.scheme}://{parse_object.netloc}{current_link}'
                        pdf_link_list.append(current_link)
                    else:
                        # without a base to the URL the relative link is useless so we should ignore
                        pass
                # if the link starts with http then its already a full link and we can save it
                if current_link.startswith('http'):
                    pdf_link_list.append(current_link)
    # the previous approach should work for most htmls but i've come across  
    # some docs that embed the link within the span so we need to check the spans first
    if pdf_link_list == []:
        for link_tag in soup.find_all('span'):
            # The most common link has "Download PDF" in the span so lets start with that.
            if ('pdf' or 'download this article') in link_tag.text.lower():
                # the href is the actual link attribute
                a_tag = link_tag.find('a')
                if a_tag:
                    current_link = a_tag.get('href')
                    if current_link:
                        # check to see if its a relative link
                        if current_link.startswith('/'):
                            if base_url is not None:
                                # we can build the link by parsing the request URL
                                parse_object = urlparse(base_url)
                                # we then build the full URL from all the parts (current link at the end)
                                current_link = f'{parse_object.scheme}://{parse_object.netloc}{current_link}'
                                pdf_link_list.append(current_link)
                                                     
                        # if the link starts with http then its already a full link
                        if current_link.startswith('http'):
                            pdf_link_list.append(current_link)

            '''        for link_tag in soup.find_all('a',{'data-tooltip':'Download PDF'}):
            a_tag = link_tag.find('a')
            if a_tag:
                current_link = a_tag.get('href')
                if current_link:
                    # check to see if its a relative link
                    if current_link.startswith('/'):
                        if base_url is not None:
                            # we can build the link by parsing the request URL
                            parse_object = urlparse(base_url)
                            # we then build the full URL from all the parts (current link at the end)
                            if 'nejm' in parse_object.netloc:
                                current_link = f'{parse_object.scheme}://{parse_object.netloc}{current_link}'
                                pdf_link_list.append(current_link)'''

    return pdf_link_list