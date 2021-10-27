import string
import random

# this block of code holds the functions used to evaluate the similarity and difference between the abstract and full text 
# to make this fast and simple we preprocess the input text and randomly sample a set number of tokens (1000 if possible)
def text_prep(input_text):
    # now there are a series of steps to select the random tokens
    # and remove unwanted characters from each abstract and body
    if type(input_text) == list:
        return []
    elif (input_text == None) or (input_text != input_text) or (len(input_text.split()) < 10):
        return []
    else:    
        # create an exclusion set of characters, keeping just the letter characters 
        excl = string.punctuation
        for i in range(10):
            excl+=str(i)
            
        # we'll sample 1000 tokens first
        tokens = list(set(random.choices(input_text.split(), k = 1000)))
        tokens = ' '.join(tokens)
        # make all characters lower case and remove non ascii
        tokens = ''.join([char.lower() for char in tokens if char not in excl])
        # resplit it in to tokens
        clean_tokens = tokens.split()
        
        return set(clean_tokens)