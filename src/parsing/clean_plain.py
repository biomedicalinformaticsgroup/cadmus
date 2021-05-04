from cadmus.src.parsing.remove_link import remove_link
import re

def clean_plain(p_text):   
    if p_text != None:
        p_text = p_text.replace('\n',' ')
        p_text = p_text.replace('\t','')
        p_text = p_text.replace('- ','')
        p_text = p_text.replace(' -','')
        p_text = p_text.replace('�','')
        p_text = p_text.replace('*','')
        p_text = p_text.replace('  ',' ')
        p_text = p_text.replace('##',' ')
        p_text = remove_link(p_text)
        p_text = p_text.replace('https://','')
        p_text = p_text.replace('http://','')
        p_text = p_text.replace('doi:','')
        p_text = p_text.replace('ftp:','')
        
        email_detection = re.compile('\w+@\w+\.[a-z]{3}')
        result = re.findall(email_detection, p_text)
        for i in range(len(result)):
            p_text = p_text.replace(result[i],'')
        
        regex = re.compile("\[([^A-Za-z]+)\]")
        result = re.findall(regex, p_text)
        for i in range(len(result)):
            p_text = p_text.replace('['+result[i]+']','')
            
        if len(p_text.split('.')) > 5:
            p_text = p_text.split('.')

            p_text_list_len = []
            for i in range(len(p_text)):
                p_text_list_len.append(len(p_text[i].split()))
                
            to_exclude = []
            for i in range(len(p_text_list_len)):
                if p_text_list_len[i] > 100:
                    to_exclude.append(i)
            l1 = []
            for j in range(len(p_text_list_len)):
                        l1.append(j)
            l3 = [x for x in l1 if x not in to_exclude]
            p_text_clean = []
            for j in range(len(l1)):
                if j in l3:
                    p_text_clean.append(p_text[j])
            p_text = '.'.join(p_text_clean)
        else:
            pass

    else:
        pass
            
    return p_text