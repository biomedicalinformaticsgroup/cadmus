def evaluation_funct(parse_dict):
    # the 'result' variable is here to identify if the text we are evaluating is the text we are looking for or something else
    result = None
    
    # collecting the information necessary to evaluate the text
    size = parse_dict['size']
    wc = parse_dict['wc']
    abstract = parse_dict['wc_abs']
    
    bu_score = parse_dict['body_unique_score']
    ab_score = parse_dict['ab_sim_score']
    
    # lets get the FPs
    # these are the small files 
    if (size <10000):
        result = 'FP'

    # now we'll look at the word count
    # now lets look for the fails due to no text
    elif wc <= 100:
        result = 'FP'

    # now we can use the body unique and abstract similarity score to classify the rest
    if ab_score != None and ab_score != 0.0:
        if ab_score <= 0.3:
            result = 'TP'
    
    # now we can use the body unique and abstract similarity score to classify the rest
    if bu_score >= 0.6 and ab_score != 0.0:
        result = 'TP' 

    # everything else should be possible with the text and abstract evaluation scores.
    # if the abstract is missing then we need to just accept the full text extracted 
    # so long as its of a decent length
    elif (abstract < 50) and (wc > 100):
        result = 'TP'
    
    else:
        result = 'AB'
    
    parse_dict.update({'evaluation':result}) 
    
    return parse_dict