def get_abstract_pdf(p_text):
    #creating the variable to identify the abstract
    lower = 0 
    upper = 0 
    ab = ''
    
    p_text = p_text.split()

    for i in range(len(p_text)):
        #changing the lower bound when the word abstract is present
        if lower == 0 and p_text[i].lower() == 'abstract':
            lower = i
        #the upper interval once we find the word introduction to delimit the bastract
        elif upper == 0 and p_text[i].lower() == 'introduction':
            upper = i
        #identify the abstract
        elif (lower != 0 or p_text[0].lower() == 'abstract') and upper != 0:
            ab = p_text[lower:upper]
            ab = ' '.join([str(elem) for elem in ab])
            break
            #we stop once we passed half of the text
        elif i > len(p_text)/2:
            break
        else:
            pass
    
    return ab
