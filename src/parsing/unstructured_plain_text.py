from cadmus.src.parsing.clean_plain import clean_plain

def unstructured_plain_text(p_text):
    
    if p_text.lower().count('##') > 2:
        lower = 0 
        upper = len(p_text.split()) - 1
        if p_text.lower().count('## references') == 2:
            count = 0
            for i in range(len(p_text.split())):
                if p_text.split()[i] == '##' and count < 2:
                    lower = i+1
                    count += 1
        while upper > int(len(p_text.split())/2):
            if p_text.split()[upper].lower() == 'references':
                break
            upper -= 1
        if lower != 0 and upper != int(len(p_text.split())/2):
            p_text = ' '.join(p_text.split()[lower:upper])
        elif lower == 0 and upper != int(len(p_text.split())/2):
            p_text = ' '.join(p_text.split()[:upper])
        elif lower != 0 and upper == int(len(p_text.split())/2):
            p_text = ' '.join(p_text.split()[lower:])
        else:
            p_text = p_text
            
    elif p_text.lower().count('to the editor') > 0:
        lower = 0
        upper = len(p_text.split()) - 1
        while upper > 0:
            if p_text.split()[upper].lower() == 'references':
                break
            upper -= 1
        if upper == 0:
            upper = len(p_text.split()) - 1
        p_text = ' '.join(p_text.split()[:upper])
        for i in range(len(p_text.split())):
            if 'to' in p_text.split()[i].lower():
                if i < int(len(p_text.split()) - 2):
                    if 'editor' in p_text.split()[i+2].lower():
                        lower = i + 3
        p_text = ' '.join(p_text.split()[lower:upper])     
            
    else:
        lower = 0 
        upper = len(p_text.split()) - 1
        while upper > int(len(p_text.split())/2):
            if p_text.split()[upper].lower() == 'references':
                break
            upper -= 1
        if upper == int(len(p_text.split())/2):
            upper = len(p_text.split()) - 1
        p_text = ' '.join(p_text.split()[:upper])
        key_present = False
        for i in range(len(p_text.split())):
            if 'introduction' in p_text.lower().split()[i] or 'abstract' in p_text.lower().split()[i] or 'letters' in p_text.lower().split()[i] or 'correspondence' in p_text.lower().split()[i] or 'editorial' in p_text.lower().split()[i]:
                lower = i
                key_present = True
                break
            elif 'https' in p_text.lower().split()[i] and key_present == False:
                lower = i + 1
        p_text = ' '.join(p_text.split()[lower:upper])
    return(clean_plain(p_text))