def limit_body(p_text):
    #loading the content ad a list
    p_text = p_text.split()
    lower = 0 
    upper = len(p_text)
    #first we identify the body as the all content 
    first_introduction = False
    first_background = False
    for i in range(len(p_text)):
        if lower == 0 and p_text[i].lower() == 'abstract':
            lower = i
        #we try to start the content from the introduction
        elif p_text[i].lower() == 'introduction' and i < (len(p_text)/2) and first_introduction == False:
            lower = i
            first_introduction = True
            first_background = True
        elif p_text[i].lower() == 'background' and i < (len(p_text)/2) and first_background == False:
            lower = i
            first_background = True 
        #we want to finish the content before the references
        elif p_text[i].lower() == 'references':
            upper = i
    #we limit the content to the interval we identified
    p_text = p_text[lower:upper]
    p_text = ' '.join([str(elem) for elem in p_text])
    
    return p_text