from cadmus.parsing.text_prep import text_prep
import numpy as np

def abstract_similarity_score(text, ab):
    # the abstract similarity score gives you the percentage of words from the abstract found in the full text
    # the higher the number, the more likely the full text contains the abstract  
    
    # firstly process the input text and tokenize up to 1000 tokens per input
    text_tokens = text_prep(text)
    ab_tokens = text_prep(ab)
    # when either input is missing then we have a score of 0
    if (text_tokens == []) or (ab_tokens ==[]):
        as_score = 0.0
    else:
        # union is the count of all unique term the two sets
        union = len(text_tokens.union(ab_tokens))
        # intersect is the shared tokens
        intersect = len(text_tokens.intersection(ab_tokens))
        # calculate the score rounded to two dp
        as_score = np.round(intersect/union, 2)

    return as_score