import re

def remove_link(p_text):
    # remove URLs from the text
    url_pattern = r'((http|ftp|https|doi|HTTP|FTP|HTTPS|DOI):\/\/)?[\w\-_]+(\.[\w\-_]+)+([\w\-\.,()@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?'
    return re.sub(url_pattern, '', p_text)