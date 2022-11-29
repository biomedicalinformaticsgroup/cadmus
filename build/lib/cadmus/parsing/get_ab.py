def get_ab(soup):
    # set the defaul abstract value to None. 
    ab = None
    # This list can be the options to look for abstract tags
    for tag in ['abstract','<dc:description>','<prism:description>']:
        # check for the tag's presence and then try and extrac the text.
        search_result = soup.find(tag)
        if search_result:
            ab = search_result.get_text(separator = u' ')
            # if text is extracted then no need to try the other options.
            break
    return ab