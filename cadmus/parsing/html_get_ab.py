def html_get_ab(soup):
    # set the defaul abstract value to None. 
    ab = ''
    #Using the tags to identify the abstract from an html page
    h_tags = soup.find_all(['h2','h3'])
    for tag in h_tags:
        if tag.text.strip().lower() == 'abstract':
            parent = tag.parent
            ab = parent.get_text(separator = u' ')
            ab = ' '.join(ab.split())
            return ab
    if ab == '':
        ab = soup.find('div',{'class':'abstract-group'})
        if ab:
            ab = ab.get_text(separator = u' ').strip()
            return ab
    if ab == '':
        ab = soup.find('div',{'id':'abstract'})
        if ab:
            ab = ab.get_text(separator = u' ')
            return ab
    if ab == '':
        ab = soup.find('meta',{'name':'citation_abstract'})
        if ab:
            ab = ab['content'].strip()
            return ab
    if ab == '':
        ab = soup.find('meta',{'name':'Description'})
        if ab:
            ab = ab['content'].strip()        

    return ab