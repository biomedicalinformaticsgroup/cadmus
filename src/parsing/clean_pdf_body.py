from cadmus.src.parsing.remove_link import remove_link
import re

def clean_pdf_body(p_text):
    if p_text != None:
        #txt_work_on = txt_work_on.lower()
        p_text = p_text.replace('\n',' ')
        p_text = p_text.replace('\t','')
        p_text = p_text.replace('- ','')
        p_text = p_text.replace(' -','')
        p_text = p_text.replace('�','')
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

        p_text = p_text.split()
        list_to_remove = []
        for i in range(len(p_text) - 7):
            if len(p_text[i]) < 4:
                if len(p_text[i+1]) < 4:
                    if len(p_text[i+2]) < 4:
                        if len(p_text[i+3]) < 4:
                            if len(p_text[i+4]) < 4:
                                if len(p_text[i+5]) < 4:
                                    if len(p_text[i+6]) < 4:
                                        if len(p_text[i+7]) < 4:
                                            list_to_remove.append(i)
                                        else:
                                            for j in range(i,i+7):
                                                list_to_remove.append(j)
                                    else:
                                        pass
                                else:
                                    pass
                            else:
                                pass
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
            else:
                pass
        l1 = []
        for i in range(len(p_text)):
            l1.append(i)
        l3 = [x for x in l1 if x not in list_to_remove]
        p_text_clean = []
        for i in range(len(p_text)):
            if i in l3:
                p_text_clean.append(p_text[i])
        p_text = ' '.join(p_text_clean)

    else:
        pass
            
    return p_text
