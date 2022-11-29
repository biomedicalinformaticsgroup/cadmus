def limit_body(p_text, keep_abstract):
    #loading the content as a list
    p_text = p_text.split()
    lower = 0 
    upper = len(p_text)
    #first we identify the body as the all content i.e start at 0 until the last element 
    first_introduction = False
    first_background = False
    strict_upper = False
    # we check if the input ask to remove the asbtract or no
    if keep_abstract == False:
        # we are only looking at the abstract for the first half of the text
        for i in range(len(p_text), int(round((len(p_text)/2)))):
            if lower == 0 and p_text[i].lower() == 'abstract':
                lower = i
            #we try to start the content from the introduction
            elif p_text[i].lower() == 'introduction' and first_introduction == False:
                lower = i
                first_introduction = True
                first_background = True
            elif p_text[i].lower() == 'background' and first_background == False:
                lower = i
                first_background = True
        # we want to finish the content before the references
        # looking at the second half of the text
        for i in range(int(round((len(p_text)/2))), len(p_text)):
            if strict_upper == False:
                if p_text[i].lower() == 'acknowledgement' or p_text[i].lower() == 'acknowledgements':
                    upper = i
                    strict_upper = True
                    break
                if p_text[i].lower() == 'references' or p_text[i].lower() == 'funding':
                    upper = i
                if i < len(p_text) - 2:
                    if p_text[i].lower() == 'conflict' and  p_text[i+2].lower() == 'interest':
                        upper = i
                        strict_upper = True
                        break
            else:
                pass
    # if we are keeping the abstract we are only looking at the second half to stop before the references
    if keep_abstract == True:
        for i in range(int(round((len(p_text)/2))), len(p_text)):
            if strict_upper == False:
                if p_text[i].lower() == 'acknowledgement' or p_text[i].lower() == 'acknowledgements':
                    upper = i
                    strict_upper = True
                    break
                if p_text[i].lower() == 'references' or p_text[i].lower() == 'funding':
                    upper = i
                if i < len(p_text) - 2:
                    if p_text[i].lower() == 'conflict' and  p_text[i+2].lower() == 'interest':
                        upper = i
                        strict_upper = True
                        break
            else:
                pass
    #we limit the content to the interval we identified
    if keep_abstract == False:
        p_text = p_text[lower:upper]
    elif keep_abstract == True:
        p_text = p_text[:upper]
    p_text = ' '.join([str(elem) for elem in p_text])
    
    return p_text