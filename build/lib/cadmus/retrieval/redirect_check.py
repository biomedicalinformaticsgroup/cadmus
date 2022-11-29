def redirect_check(soup):
    # this function is to identify redirection link
    title = soup.find('title')
    if title:
        result = title.text == 'Redirecting'
    else:
        result = False
    return result