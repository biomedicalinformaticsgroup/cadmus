def redirect_check(soup):
    title = soup.find('title')
    if title:
        result = title.text == 'Redirecting'
    else:
        result = False
    return result