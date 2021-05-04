def get_abstract_txt(p_text):
    lower = 0 
    upper = 0 
    ab = ''
    
    if p_text.lower().count('## abstract') == 1:
        p_text = p_text.split()
        for i in range(len(p_text)):
            if lower == 0 and p_text[i].lower() == '##' and p_text[i+1].lower() == 'abstract':
                lower = i+1
            elif upper == 0 and p_text[i].lower() == '*' and i > lower:
                upper = i
            elif upper == 0 and p_text[i].lower() == '##' and i > lower:
                upper = i
            elif (lower != 0 or p_text[0].lower() == 'abstract') and upper != 0:
                ab = p_text[lower:upper]
                ab = ' '.join([str(elem) for elem in ab])
                break
            elif i > len(p_text)/2:
                break
            else:
                pass

    return ab