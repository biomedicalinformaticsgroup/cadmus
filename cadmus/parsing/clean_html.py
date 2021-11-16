from cadmus.parsing.remove_link import remove_link
import re
import unicodedata

def clean_html(p_text):
    #check if the content is not none i.e. there is text to clean
    if p_text != None:
        
        # we want to check and remove the [, , , ] that were made while stripping out references etc
        p_text = re.sub('\[[, ]*\]', ' ', p_text)
        p_text = re.sub('\[(, )*\]', ' ', p_text)
        
        # remove any of the unicode characeters and \n chars
        p_text = unicodedata.normalize("NFKD", p_text)
        
        # during a OOV study we identified the strings of character that we want to remove in order to offer a cleaner text as output
        # removing the links from the text
        p_text = remove_link(p_text)
        p_text = p_text.replace('https://','')
        p_text = p_text.replace('http://','')
        p_text = p_text.replace('doi:','')
        p_text = p_text.replace('ftp:','')
        p_text = p_text.replace('\n', '')
        p_text = p_text.replace('\t', '')
        # removing the publishing citing
        p_text = p_text.replace('et al.','')
        p_text = p_text.replace('et al','')
        # remove the email adresses of the text
        email_detection = re.compile('\w+@\w+\.[a-z]{3}')
        result = re.findall(email_detection, p_text)
        for i in range(len(result)):
            p_text = p_text.replace(result[i],'')
        p_text = p_text.replace('  ',' ')          
    return p_text