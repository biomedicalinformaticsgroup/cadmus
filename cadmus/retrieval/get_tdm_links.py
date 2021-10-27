def get_tdm_links(link_list):
    tdm_links = []
    
    # sometimes the link list is a none value and needs to be skipped
    if link_list == None:
        return link_list
    else:
        # otherwise work through each dictionary
        for link_dict in link_list:
            # check the intendeed application
            if (link_dict.get('intended-application') == 'text-mining')\
            or (link_dict.get('intended-application') == 'syndication')\
            or (link_dict.get('intended-application') == 'unspecified'):
                tdm_links.append(link_dict.get('URL'))
    if tdm_links == []:
        tdm_links = None
    else:
        tdm_links = list(set(tdm_links))
    return tdm_links