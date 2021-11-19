def clean_soup(soup):
    # NB we aim to provide a clean version of the text but the original file is always retained for bespoke parsing.
    # eg you may wish to keep the tables and figures or author data.
    
    # here is a list of tags that i want to remove before i extract the text
    # these include links, scripts, supplemnetal tags, references
    tag_remove_list = ['a',
                       'button',
                       'script',
                       'xref',
                       'table',
                       'label,
                       'figure',
                       'figcaption',
                       'sup',
                       'surname',
                       'names',
                       'given-names',
                       'tbody',
                       'footer',
                       'license',
                       'ack',
                       'cite',
                       'thead',
                       'tfoot',
                       'comment',
                       'img',
                       'link',
                       'ol',
                       'ul',
                       'li'
                      ]
    # buttons often have some useless text, but occasionally the whole doc is hidden behind a button.
    # we'll only get rid of it if it doesn't hold too many words
    button_tags = soup.find_all('button')
    for tag in button_tags:
        if tag.parent:
            if len(tag.parent.get_text().split()) < 200:
                tag.parent.decompose()
    
    # get rid of the "share" info
    shares = soup.find_all("div", class_="share-access hidden")
    for tag in shares:
        tag.decompose()
    shares = soup.find_all("div", id_="share_Pop")
    for tag in shares:
        tag.decompose() 
    shares = soup.find_all("div", class_="shareable")
    for tag in shares:
        tag.decompose()
    # these tags were trickier to remove, 
    # author data is plentiful and not part of the content really   
    # the abstract should not be parsed here, we want control of whether to add it or not - we parse it using the get_abstract funct
    # we also remove acknowledgements, footnotes and correspondence details and licensing details.
    for tag in soup.find_all(['div', 'section']):
        attrs = get_attrs(tag)
        for val in attrs:
            if 'author' in val \
            or 'abstract' in val \
            or 'correspondence' in val \
            or 'ack' in val \
            or 'footnote' in val \
            or 'fn' in val \
            or 'license' in val:
                tag.decompose()
    
    # find all the tags matching any name in the remove list detailed above
    tags = soup.find_all(tag_remove_list)
    # loop through each tag and apply the decompose function to remove them from the soup
    for tag in tags:
        tag.decompose()
    return soup
