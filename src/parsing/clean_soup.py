def clean_soup(soup):
    # here is a list of tags that i want to remove before i extract the text
    # these include links, scripts, supplemnetal tags, references
    tag_remove_list = ['a', 'script', 'sup', 'xref']
    # find all the tags matching any name in the list
    tags = soup.find_all(tag_remove_list)
    # loop through each tag and apply the decompose function to remove them from the soup
    for tag in tags:
        tag.decompose()
    return soup