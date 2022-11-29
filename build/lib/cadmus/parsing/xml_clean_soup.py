def xml_clean_soup(soup):
    # here is a list of tags that i want to remove before i extract the text
    # these include links, scripts, supplemnetal tags, references, tables, authors
    tag_remove_list = ['ref-list',
                       'supplementary-material',
                       'bibliography',
                       'tex-math',
                       'inline-formula',
                       'table',
                       'tbody',
                       'table-wrap',
                       'ack',
                       'fig',
                       'table-wrap-foot',
                       'surname',
                       'given-names',
                       'name',
                       'xref',
                       'element-citation',
                       'sup',
                       'td',
                       'tr',
                       'string-name',
                       'familyname',
                       'givennames',
                       'mixed-citation',
                       'author',
                       'aff',
                       'ext-link',
                       'link',
                       'pub-id',
                       'year',
                       'issue',
                       'th',
                       'floats-group',
                       'back',
                       'front',
                       'licensep',
                       'license',
                       'permissions',
                       'article-meta',
                       'url',
                       'uri',
                       'label',
                       'person-group'
                      ]
    # find all the tags matching any name in the list
    tags = soup.find_all(tag_remove_list)
    # loop through each tag and apply the decompose function to remove them from the soup
    for tag in tags:
        tag.decompose()
    return soup