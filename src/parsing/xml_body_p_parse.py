def xml_body_p_parse(soup):
    # search the soup object for body tag
    body = soup.find('body')
    # if a body tag is found then get a list of all the 'paragraph' tags
    if body:
        ps = body.find_all('p')
        # for every p tag, extract the plain text, stripping the whitespace and making one long string
        p_text = ' '.join([p.text.strip() for p in ps])
    else:
        # when there is no body tag then the XML is not useful.
        print('No Body, looks like a False Positive XML or Abstract Only')
        p_text = None
    return p_text