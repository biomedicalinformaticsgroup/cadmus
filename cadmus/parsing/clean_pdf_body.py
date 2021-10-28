from cadmus.parsing.remove_link import remove_link
import re
import unicodedata

def clean_pdf_body(p_text):
    #check if the content is not none
    if p_text != None:
        p_text = unicodedata.normalize("NFKD", p_text)
        #replace different type of characters by another characters (space or no space to reconstruct word)
        p_text = p_text.replace('\n',' ')
        p_text = p_text.replace('\t','')
        p_text = p_text.replace('- ','')
        p_text = p_text.replace(' -','')
        p_text = p_text.replace('�','')
        p_text = p_text.replace('å','')
        p_text = p_text.replace('┸','')
        p_text = p_text.replace('❒','')
        p_text = p_text.replace('┻','')
        p_text = p_text.replace('►','')
        p_text = p_text.replace('❖','')
        p_text = p_text.replace('et al.','')
        p_text = p_text.replace('et al','')
        p_text = p_text.replace('▀','')
        p_text = p_text.replace('file:///','')
        #remove the link present in the text
        p_text = remove_link(p_text)
        p_text = p_text.replace('https://','')
        p_text = p_text.replace('http://','')
        p_text = p_text.replace('doi:','')
        p_text = p_text.replace('ftp:','')
        # remove the email adresses of the text
        email_detection = re.compile('\w+@\w+\.[a-z]{3}')
        result = re.findall(email_detection, p_text)
        for i in range(len(result)):
            p_text = p_text.replace(result[i],'')
        # remove the reference citation i.e [1] from he text
        regex = re.compile("\[([^A-Za-z]+)\]")
        result = re.findall(regex, p_text)
        for i in range(len(result)):
            p_text = p_text.replace('['+result[i]+']','')
        #remove the word if 7 words in a row are less than 4 characters. A reason for that was the result of tika when parsing a table
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
        #remove the index of the words that fall into the previous comment 
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

    p_text = p_text.replace('  ',' ')
            
    return p_text
