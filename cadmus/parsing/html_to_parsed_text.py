from cadmus.parsing.get_attrs import get_attrs

import re
import unicodedata

def html_to_parsed_text(soup):
    # i want to save the text portions to a holding list, adding new sections each time we think its useful or new.
    text = ''
    # first we search the body for each division  or article tage and save it as a list of tag object

    # first we look for the cleanest tags.
    for name in ['article', 'ifp:body', 'articledata']:
        if soup.find(name):
            tag = soup.find(name)
            paras = tag.find_all(['p',
                                  'h1',
                                  'h2',
                                  'h3',
                                  'div', {'class':'html-p'},
                                  'div', {'class':'NLM_paragraph'},
                                  'div', {'class':'NLM_p'},
                                  'div', {'class':'NLM_p last'}
                                 ])
            for p in paras:
                if p.text.lower() == 'references' \
                    or p.text.lower() == 'supplementary material' \
                    or p.text.lower() == 'acknowledgments':
                    break
                elif len(p.text.split()) > 1000:
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
                        if p.get_text(" ", strip = True) not in text:
                            text += p.get_text(" ", strip = True)
            return text
            
            
    # if we don't find a clean tag we can look through all the tags and check the attributes
    if text == '':
        # print('no main tag found')
        # create a list of tags based on the most useful tag names
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
                    or (('article' in value) and ('content' in value))\
                    or (("content" in value) and ('body' in value))\
                    or (('article' in value) and ('row' in value))\
                    or ('article-full-text' in value)\
                    or value == 'fulltext'\
                    or value == 'pagefulltext'\
                    or value == 'page-body'\
                    or value == 'article'\
                    or value == 'fulltext-view'\
                    or value == 'html-body'\
                    or value == 'body-text'\
                    or ('hlfld-fulltext' in value):
                        
                        paras = tag.find_all(['p',
                                              'h2',
                                              'h3',
                                              'div', {'class':'html-p'},
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
                            elif len(p.text.split()) > 1000:
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
                                    if p.get_text(" ", strip = True) not in text:
                                        text += p.get_text(" ", strip = True)
        if text != '':
            return text
                
    if text == '':
        #print('workin on basic tag trawl')
        # the next step will be extracting the text from our tags 
        # if any of these criteria are met then we should look for text holding tags
        paras = soup.body.find_all(['p',
                                    'h2',
                                    'h3',
                                    'div', {'class':'html-p'},
                                    'div', {'class':'NLM_paragraph'},
                                    'div', {'class':'NLM_p'},
                                    'div', {'class':'NLM_p last'}
                                   ])
        for p in paras:
            if p.text.lower() == 'references' \
                or p.text.lower() == 'supplementary material' \
                or p.text.lower() == 'acknowledgments':
                break
            elif len(p.text.split()) > 1000:
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
                    if p.get_text(" ", strip = True) not in text:
                        text += p.get_text(" ", strip = True)

    # finally we want to check remove the [, , , ] from stripping out references etc
    text = re.sub('\[[, ]*\]', '', text)
    # remove any of the unicode characeters and \n chars
    text = unicodedata.normalize("NFKD", text).replace('\n', '')

    return text
