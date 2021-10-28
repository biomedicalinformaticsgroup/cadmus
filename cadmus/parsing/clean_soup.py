def clean_soup(soup):
    # here is a list of tags that i want to remove before i extract the text
    # these include links, scripts, supplemnetal tags, references
    tag_remove_list = ['a',
                       'button',
                       'script',
                       'xref',
                       'table',
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
    
    button_tags = soup.find_all('button')
    for tag in button_tags:
        if tag.parent:
            tag.parent.decompose()
    shares = soup.find_all("div", class_="share-access hidden")
    for tag in shares:
        tag.decompose()
    shares = soup.find_all("div", id_="share_Pop")
    for tag in shares:
        tag.decompose() 
    shares = soup.find_all("div", class_="shareable")
    for tag in shares:
        tag.decompose()    
    # find all the tags matching any name in the list
    tags = soup.find_all(tag_remove_list)
    # loop through each tag and apply the decompose function to remove them from the soup
    for tag in tags:
        tag.decompose()
    return soup
