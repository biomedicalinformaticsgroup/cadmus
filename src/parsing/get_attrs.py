# This function is used in html parsing and flattens all the values in the attributes dictionary for each tag provided
def get_attrs(tag):
    # each tag can have a value attached to it but these can be hard to evaluate due to multiple levels
    # a flattened list of tag values is our target
    flat_vals = []
        
    # lets get the dictionary of attributes for each div_tag, if there are none then {} is returned
    attrs = tag.attrs
    # now the values for each item in the dictionary
    vals = attrs.values()
    # the issue lies in the fact that sometimes the value is a list of items and sometimes a single item
    # if its a list then we'll flatten it, otherwise just add it as a string (making all values lower case by default)
    for val in vals:
        if type(val) == list:
            flat_vals.extend([element.lower() for element in val])
        else:
            flat_vals.append(val.lower())
    
    return flat_vals
