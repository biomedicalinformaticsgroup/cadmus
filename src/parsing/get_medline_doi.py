import re

def get_medline_doi(record):
    # the record we refer to is a bio.medline.record, effectively a python dictionary
    # getting a doi is valuable and we need to try a bit harder to find one
    doi = None
    # look and see if the LID field is present in the record                        
    LID = record.get('LID')
    if LID:
        # iterate through the LID looking for 'doi'
        for val in LID:
            if 'doi' in val:
                # split the string to get rid of ' [doi]' and keep the plain doi string
                doi = val.split()[0]
    # if that didn't work then look in the AID Field and do the same
    if doi == None:
        AID = record.get("AID")
        if AID:
            for val in AID:
                if 'doi' in val:
                    doi = val.split()[0]
    # sometimes the doi is only present in the SO section and needs to be parsed out of the citation
    if doi == None:
        SO = record.get('SO')
        if SO:
            if 'doi' in SO:
                # now we need to remove all the surround text and full stop from the end   
                # use regular expression to locate the "doi: xkkxjwkdjdfksfd" section and cut it out as a string
                doi = re.findall(r'doi: \S+', SO)
                # remove 'doi' from the string
                doi = doi[0].replace('doi: ', '')
                # check to see if there is a full stop at the end of the string (doi's dont end in full stops)
                if doi[-1] == '.':
                    doi = doi[:-1] 
    # now save whatever we got back, otherwise save the default None            
    return doi