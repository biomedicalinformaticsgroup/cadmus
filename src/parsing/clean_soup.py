
def clean_soup(soup):
    # here is a list of tags that i want to remove before i extract the text
    # these include links, scripts, supplemnetal tags, references
    tag_remove_list = ['a',
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
    # find all the tags matching any name in the list
    tags = soup.find_all(tag_remove_list)
    # loop through each tag and apply the decompose function to remove them from the soup
    for tag in tags:
        tag.decompose()
    return soup
