from cadmus.parsing.get_attrs import get_attrs

def html_to_parsed_text(soup, abstract, keep_abstract):
    # i want to save the text portions to a holding list, adding new sections each time we think its useful or new.
    text = ''
    # first we search the body for each division  or article tage and save it as a list of tag object

    # first we look for the cleanest tags (closest to the body of the article.
    for name in ['article', 'ifp:body', 'articledata']:
        if soup.find(name):
            tag = soup.find(name)
            # within these main tags we want to find the text contating tags
            paras = tag.find_all(['p',
                                  'h1',
                                  'h2',
                                  'h3',
                                  'div', {'class':'html-p'},
                                  'div', {'role':'paragraph'},
                                  'div', {'class':'NLM_paragraph'},
                                  'div', {'class':'NLM_p'},
                                  'div', {'class':'NLM_p last'}
                                 ])
            # work though each text tag and stop the process if we come across end of doc headings
            for p in paras:
                if p.text.lower() == 'references' \
                    or p.text.lower() == 'supplementary material' \
                    or p.text.lower() == 'acknowledgments':
                    break
                # if the tag.text has enormous lump of text best to avoid it, we should be able to get cleaner text by getting targeted smaller paragraphs 
                elif len(p.text.split()) > 1500:
                    pass
                
                else:
                    attrs = get_attrs(p)
                    if attrs == [] \
                    or 'para' in attrs \
                    or 'html-p' in attrs \
                    or 'nlm_paragraph' in attrs \
                    or 'nlm_p' in attrs \
                    or 'nlm_p last' in attrs \
                    or 'mb15' in attrs \
                    or 'mb0' in attrs \
                    or 'article-section-content' in attrs \
                    or 'articleparagraph' in attrs:
                        # when criteria met, parse out the text, sentence by sentence.
                        # if the sent has been seen before, don't add it
                        ptext = p.get_text(" ", strip = True)
                        for sent in ptext.split(". "):
                            if sent not in text:
                                text = text + " " + sent + "."
                    # this allows text found under an "id" attribute tag, i didn't really want to use it but it is very common for some publishers and the text remains pretty clean
                    if p.attrs.get('id') != None:
                        # strip out the trailing whitespace, join with a space
                        ptext = p.get_text(" ", strip = True)
                        # split roughly into sentences 
                        for sent in ptext.split(". "):
                            if sent not in text:
                                text = text + " " + sent + "."
            if text != '':
                if keep_abstract == True:
                    text = str(abstract) + str(' ') + str(text)
                else:
                    pass
                return text
            
    # if we don't find a clean tag we can look through all the tags and check the attributes
    if text == '':
        # print('no main tag found')
        # create a list of tags based on the most useful tag names
        if soup.body != None:
            div_tag = soup.body.find_all(['div', 'section'])
            # now we have a tag target approach - this tries to identify common tags that hold the neatest representation of the text
            for tag in div_tag:
                # use our function to get a flat list of attributest to query
                attrs_list = get_attrs(tag)
                # sometimes its empty so check it is not None
                if attrs_list:
                    # now we have a list of attribute values to query for our common words
                    parse = False
                    for value in attrs_list:
                        if (('article' in value) and ('body' in value))\
                        or (('article' in value) and ('fulltext' in value))\
                        or (('journal' in value) and ('fulltext' in value))\
                        or (('article' in value) and ('content' in value))\
                        or (("content" in value) and ('body' in value))\
                        or (('article' in value) and ('row' in value))\
                        or ('article-full-text' in value)\
                        or value == 'fulltext'\
                        or value == 'pagefulltext'\
                        or value == 'page-body'\
                        or value == 'article'\
                        or value == 'fulltext-view'\
                        or value == 'journalfulltext'\
                        or value == 'html-body'\
                        or value == 'body-text'\
                        or ('hlfld-fulltext' in value):
                            
                            paras = tag.find_all(['p',
                                                'h2',
                                                'h3',
                                                'div', {'class':'html-p'},
                                                'div', {'role':'paragraph'},
                                                'div', {'class':'NLM_paragraph'},
                                                'div', {'class':'NLM_p'},
                                                'div', {'class':'NLM_p last'}
                                                ])
                            for p in paras:
                                #print(p.attrs)
                                if p.text.lower() == 'references' \
                                    or p.text.lower() == 'supplementary material' \
                                    or p.text.lower() == 'acknowledgments':
                                    #print('stopping due to section break')
                                    break
                                elif len(p.text.split()) > 1500:
                                    #print("skipping due to size")
                                    pass
                                else:
                                    attrs = get_attrs(p)
                                    if attrs == [] \
                                    or 'para' in attrs \
                                    or 'html-p' in attrs \
                                    or 'nlm_paragraph' in attrs \
                                    or 'nlm_p' in attrs \
                                    or 'nlm_p last' in attrs \
                                    or 'mb15' in attrs \
                                    or 'mb0' in attrs \
                                    or 'article-section-content' in attrs \
                                    or 'articleparagraph' in attrs:
                                        ptext = p.get_text(" ", strip = True)
                                        for sent in ptext.split(". "):
                                            if sent not in text:
                                                text = text + " " + sent + "."
                                if p.attrs.get('id') != None:
                                    ptext = p.get_text(" ", strip = True)
                                    for sent in ptext.split(". "):
                                        if sent not in text:
                                            text = text + " " + sent + "."
            if text != '':
                if keep_abstract == True:
                    text = str(abstract) + str(' ') + str(text)
                else:
                    pass
                return text
                
    if text == '':
        #print('workin on basic tag trawl')
        # sometimes you cant find any specific tags but you might get a decent clean text from just scraping all the text tags we used above
        if soup.body != None:
            paras = soup.body.find_all(['p',
                                        'h2',
                                        'h3',
                                        'div', {'class':'html-p'},
                                        'div', {'class':'NLM_paragraph'},
                                        'div', {'role':'paragraph'},
                                        'div', {'class':'NLM_p'},
                                        'div', {'class':'NLM_p last'}
                                    ])
            for p in paras:
                if p.text.lower() == 'references' \
                    or p.text.lower() == 'supplementary material' \
                    or p.text.lower() == 'acknowledgments':
                    break
                elif len(p.text.split()) > 1500:
                    pass
                else:
                    attrs = get_attrs(p)
                    if attrs == [] \
                    or 'para' in attrs \
                    or 'html-p' in attrs \
                    or 'nlm_paragraph' in attrs \
                    or 'nlm_p' in attrs \
                    or 'mb15' in attrs \
                    or 'mb0' in attrs \
                    or 'article-section-content' in attrs \
                    or 'articleparagraph' in attrs:
                        ptext = p.get_text(" ", strip = True)
                        for sent in ptext.split(". "):
                            if sent not in text:
                                text = text + " " + sent + "."
                    elif p.attrs.get('id') != None:
                        ptext = p.get_text(" ", strip = True)
                    for sent in ptext.split(". "):
                        if sent not in text:
                            text = text + " " + sent + "."
    if text != '':
        if keep_abstract == True:
            text = str(abstract) + str(' ') + str(text)
        else:
            pass
    return text
