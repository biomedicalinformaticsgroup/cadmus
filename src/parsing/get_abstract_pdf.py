def get_abstract_pdf(p_text):
    
    lower = 0 
    upper = 0 
    ab = ''
    
    p_text = p_text.split()

    for i in range(len(p_text)):
        if lower == 0 and p_text[i].lower() == 'abstract':
            lower = i
        elif upper == 0 and p_text[i].lower() == 'introduction':
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
