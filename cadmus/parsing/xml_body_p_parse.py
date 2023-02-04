def xml_body_p_parse(soup, abstract, keep_abstract):
    # we'll save each paragraph to a holding list then join at the end
    p_text = []
    # keeping the abstract at the begining depending on the input
    if keep_abstract == True:
        if abstract != '' and abstract != None and abstract == abstract:
            p_text.append(abstract)
    else:
        pass
    # search the soup object for body tag
    body = soup.find('body')
    # if a body tag is found then find the main article tags
    if body:
        main = body.find_all(['article','component','main'])
        if main:
            # work though each of these tags if present and look for p tags
            for tag in main:
                ps = tag.find_all('p')
                if ps:
                    # for every p tag, extract the plain text, stripping the whitespace and making one long string
                    p_text.extend([p.text.strip() for p in ps if p.text.strip() not in p_text])
            # join each p element with a space 
            p_text = ' '.join(map(str,p_text))
        else:
            # when there is no body tag then the XML is not useful.
            print('No Body, looks like a False Positive XML or Abstract Only')
            p_text = ''
    else:
        # when there is no body tag then the XML is not useful.
        print('No Body, looks like a False Positive XML or Abstract Only')
        p_text = ''
    # ensure the p_text is a simplified string format even if the parsing fails    
    if p_text == [] or p_text == '' or p_text == ' ':
        p_text = ''
    return p_text