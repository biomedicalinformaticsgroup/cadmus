from cadmus.src.parsing.get_attrs import get_attrs

def html_to_parsed_text(soup):
    
    # i want to save the text portions to a holding list, adding new sections each time we think its useful or new.
    text = []
    # first we search the body for each division and save it as a list of tag objects
    if soup.find('body'):
        div_tags = soup.body.find_all(['div', 'article'])
        
        
        # The most common attribute used for marking a useful division is the "class" or "id" attribute so lets consider them.
        for tag in div_tags:
            if tag.name =='article':
                # if any of these criteria are met then we should look for paragraphs within the div tag
                paras = tag.find_all(['p', 'div', {'class':'html-p'},'div', {'class':'NLM_paragraph'}])
                for p in paras:
                    if p.attrs.get('class') == None\
                    or 'para' in p.attrs.get('class')\
                    or 'NLM_paragraph' in p.attrs.get('class')\
                    or 'html-p' in p.attrs.get('class'):
                        if p.text.strip() not in text:
                            text.append(p.text.strip())
                            
            else:
                # we can use the function above to get the values from the attributes for each tag
                attrs_list = get_attrs(tag)
                if attrs_list:
                    # now we have a list of attribute values to query for our common words
                    for value in attrs_list:
                        if (('article' in value) and ('body' in value))\
                        or (('article' in value) and ('fulltext' in value))\
                        or (('article' in value) and ('content' in value))\
                        or (("content" in value) and ('body' in value))\
                        or ('article-full-text' in value)\
                        or value == 'fulltext'\
                        or value == 'article'\
                        or value == 'fulltext-view'\
                        or value == 'html-body'\
                        or ('hlfld-fulltext' in value):
                            # if any of these criteria are met then we should look for paragraphs within the div tag
                            paras = tag.find_all(['p', 'div', {'class':'html-p'}, 'div', {'class':'NLM_paragraph'}])
                            for p in paras:
                                if p.attrs.get('class') == None\
                                or 'para' in p.attrs.get('class')\
                                or 'html-p' in p.attrs.get('class')\
                                or 'NLM_paragraph' in p.attrs.get('class'):
                                    if p.text.strip() not in text:
                                        text.append(p.text.strip())
                                        
                                       
        text = ' '.join(text)
        if text == '':
            text = []
            for tag in div_tags:
                # if any of these criteria are met or return no text then we should look for paragraphs within the generic div tag
                paras = tag.find_all('p')
                for p in paras:
                    if p.attrs.get('class') == None\
                    or 'para' in p.attrs.get('class')\
                    or 'NLM_paragraph' in p.attrs.get('class')\
                    or 'html-p' in p.attrs.get('class'):
                        if p.text.strip() not in text:
                            text.append(p.text.strip())
            text = ' '.join(text)
            if text == '':
                text = None
                           
        
    return text