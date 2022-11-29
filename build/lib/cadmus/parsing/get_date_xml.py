def get_date_xml(soup):
    # set the defaul abstract value to None. 
    new_date = None
    # This list can be the options to look for abstract tags
        # check for the tag's presence and then try and extrac the text.
    search_result = soup.find('accepted')
    if search_result:
        print(search_result)
        new_date = search_result.get_text(separator = u'-')
        # if text is extracted then no need to try the other options.
    return new_date