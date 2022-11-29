from cadmus.parsing.remove_link import remove_link
import re
import unicodedata

def clean_plain(p_text):  
    #checking that the text is not none i.e. there is text to clean
    if p_text != None:
        # removing unicode from text
        p_text = unicodedata.normalize("NFKD", p_text)
        # replacing characters by space or none
        # following a study of OOV from previous search we identify a list of strings of character to remove or replace
        p_text = p_text.replace('\n',' ')
        p_text = p_text.replace('\t','')
        p_text = p_text.replace('- ','')
        p_text = p_text.replace(' -','')
        p_text = p_text.replace('�','')
        p_text = p_text.replace('*','')
        p_text = p_text.replace('##',' ')
        p_text = p_text.replace('et al.','')
        p_text = p_text.replace('et al','')
        p_text = p_text.replace('<mrow>','')
        p_text = p_text.replace('</mrow>','')
        p_text = p_text.replace('<mml>','')
        p_text = p_text.replace('</mml>','')
        p_text = p_text.replace('<mi>','')
        p_text = p_text.replace('</mi>','')
        p_text = p_text.replace('IMAGE-HIGH-RES','')
        p_text = p_text.replace('IMAGE-WEB-PDF','')
        p_text = p_text.replace('<mo>','')
        p_text = p_text.replace('</mo>','')
        p_text = p_text.replace('IMAGE-THUMBNAIL','')
        p_text = p_text.replace('IMAGE-DOWNSAMPLED','')
        p_text = p_text.replace('<msub>','')
        p_text = p_text.replace('</msub>','')
        p_text = p_text.replace('AAM-PDF','')
        p_text = p_text.replace('InterviewRevised','Interview Revised')
        p_text = p_text.replace('file:///','')
        p_text = remove_link(p_text)
        p_text = p_text.replace('https://','')
        p_text = p_text.replace('http://','')
        p_text = p_text.replace('doi:','')
        p_text = p_text.replace('ftp:','')
        #remove the emails from the text with a domain name of 3 like .com
        email_detection = re.compile('\w+@\w+\.[a-z]{3}')
        result = re.findall(email_detection, p_text)
        for i in range(len(result)):
            p_text = p_text.replace(result[i],'')
        #remove the emails from the text with a domain name of 2 like country domain
        email_detection = re.compile('\w+@\w+\.[a-z]{2}')
        result = re.findall(email_detection, p_text)
        for i in range(len(result)):
            p_text = p_text.replace(result[i],'')
        #remove the reference citation i.e [1]
        regex = re.compile("\[([^A-Za-z]+)\]")
        result = re.findall(regex, p_text)
        for i in range(len(result)):
            p_text = p_text.replace('['+result[i]+']','')
        #entering into the loop if the all content has more than 5 sentences
        if len(p_text.split('.')) > 5:
            p_text = p_text.split('.')

            p_text_list_len = []
            for i in range(len(p_text)):
                p_text_list_len.append(len(p_text[i].split()))
            #exclude the sentences that are longer than 100 words, most likely the metadata
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
    # removing artefact of citation and double space
    p_text = re.sub('\[[, ]*\]', ' ', p_text)
    p_text = re.sub('\[(, )*\]', ' ', p_text)
    p_text = p_text.replace('  ',' ')
            
    return p_text