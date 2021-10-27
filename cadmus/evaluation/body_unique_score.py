# now another function to determine score considering if the body has many unique terms
from cadmus.parsing.text_prep import text_prep
import numpy as np

# the higher the score, the greater the differnce between a random selection of abstract and full text tokens
def body_unique_score(text, ab):
    
    # firstly process the input text and tokenize up to 1000 tokens per input
    text_tokens = text_prep(text)
    ab_tokens = text_prep(ab)
    
    # if the text is empty then the unique score is 0
    if text_tokens == []:
        bu_score = 0  
    # if the abstract is empty then any retrieved text is useful and we set the score to 1
    elif ab_tokens == []:
        bu_score = 1
    
    else:
        # union is the combined unique terms
        union = len(text_tokens.union(ab_tokens))
        # bod diff is the number of tokens found only in the full text
        bod_diff = len(text_tokens.difference(ab_tokens))
        
        bu_score = np.round(bod_diff/union, 2)

    return bu_score