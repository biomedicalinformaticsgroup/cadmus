from cadmus.parsing.remove_link import remove_link
import re
import unicodedata



def clean_html(p_text):
    #check if the content is not none
    if p_text != None:
        
        # we want to check remove the [, , , ] that were made when we stripping out references etc
        p_text = re.sub('\[[, ]*\]', ' ', text)
        p_text = re.sub('\[(, )*\]', ' ', text)
        
        # remove any of the unicode characeters and \n chars
        p_text = unicodedata.normalize("NFKD", text)
        
        p_text = remove_link(p_text)
        p_text = p_text.replace('https://','')
        p_text = p_text.replace('http://','')
        p_text = p_text.replace('doi:','')
        p_text = p_text.replace('ftp:','')
        p_text = p_text.replace('\n', '')
        p_text = p_text.replace('\t', '')
        # remove the email adresses of the text
        email_detection = re.compile('\w+@\w+\.[a-z]{3}')
        result = re.findall(email_detection, p_text)
        for i in range(len(result)):
            p_text = p_text.replace(result[i],'')
        p_text = p_text.replace('  ',' ')          
    return p_text