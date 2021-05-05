from cadmus.src.parsing.clean_plain import clean_plain

def structured_plain_text(p_text, abs_text):
    #as we extracted more txt file we identify patterns from some of teh txt files. Some followed a structure where we finda way to limit the body and extract the abstract
    lower = 0
    upper = len(p_text.split()) - 1
    limit = upper
    #at first the interval is equal to the size of the input
    #trying to identify if the bastract is present in the content to remove it
    for i in range(int(len(p_text.split())/2)): 
        if p_text.split()[i] == abs_text.split()[0]:
            if p_text.split()[(i+len(abs_text.split()))-1] == abs_text.split()[-1]:
                lower = i+len(abs_text.split())
    #remove the abstract from the tag ## abstract
    if p_text.lower().count('## abstract') == 1:
        count = 0
        boll = False
        i = 0
        while boll == False:
            if p_text.split()[i] == '*' or p_text.split()[i] == '**':
                lower = i + 2
            if p_text.split()[i] == '##':
                count += 1
                if count == 2:
                    if lower == 0:
                        lower = i + 1
                    boll = True
            if i == limit:
                boll = True
            i += 1
    #find the references to limit the body until the reference
    while upper > int(len(p_text.split())/2):
        if p_text.split()[upper].lower() == 'references':
            break
        upper -= 1
        
    if lower != 0 and upper != int(len(p_text.split())/2):
        if len(p_text.split()[lower:upper]) < 10:
            if 'for publication' in ' '.join(p_text.split()[lower:upper]).lower():
                p_text = ' '.join(p_text.split()[:upper])
        else:
            p_text = ' '.join(p_text.split()[lower:upper])
    elif lower == 0 and upper != int(len(p_text.split())/2):
        p_text = ' '.join(p_text.split()[:upper])
    elif lower != 0 and upper == int(len(p_text.split())/2):
        if len(p_text.split()[lower:]) < 10:
            if 'for publication' in ' '.join(p_text.split()[lower:]).lower():
                p_text = ' '.join(p_text.split())
        else:
            p_text = ' '.join(p_text.split()[lower:])
    else:
        p_text = p_text
        
    return clean_plain(p_text)