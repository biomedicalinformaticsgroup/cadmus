from fuzzywuzzy import process
from dateutil import parser
import re
import datetime

def pdat_to_datetime(date):
    if type(date) != str:
        return date
    else:
        # set the defaul value to 
        # this is a matching dictionary with numeric representation of dates
        fuzzy_d = {'jan':'01','feb':'02','mar':'03','apr':'04','may':'05','jun':'06','jul':'07',
              'aug':'08','sep':'09','oct':'10','nov':'11','dec':'12','win':'02','sum':'08',
              'spr':'05','aut':'11','fal':'11'}
        
        # first lets replace the exact season names with their numeric value
        # we are using the last month of the season to defensively consider embargos on access
        date = date.lower().replace('winter', '02')
        date = date.lower().replace('summer', '08')
        date = date.lower().replace('spring', '05')
        date = date.lower().replace('autumn', '11')
        date = date.lower().replace('fall', '11')
    
        # sometimes we have spelling mistakes. 
        # lets simplify any remaining alphabetic tokens to the first 3 numbers 

        # regex find all examples of alpha words at least 3 letters long
        matches = re.findall('[a-z]{3,15}', date)
        # iterate through each match and replace the string with the first 3 characters
        for match in matches:
            # check for any spelling mistake
            # provide the options from our fuzzy_d above
            options = list(fuzzy_d.keys())
            # use fuzzywuzzy to pick the closest match for our You can also select the string with the highest matching percentage
            best = process.extractOne(match,options)
            # these should be three letter words. if we are one letter out then the ration will be 67%
            # lets check for a value of at least 67%

            if best[1] >= 60:
                # replace the string with the representative number
                date = date.replace(match, fuzzy_d[best[0]])
        try:
            dt = parser.parse(" ".join(date.split('-'))).date()
            return dt
        except:
            try:
                # now try parse the date using the simplified text
                dt = parser.parse(date).date()
                return df
            except:
                # try to parse the date when the date is split by - or /
                try:
                    # dt = parser.parse(" ".join(date.split('-'))).date()
                    dt = parser.parse(date.split('-')[0]).date()
                    return dt
                except:
                    try:
                        # dt = parser.parse(" ".join(date.split('/'))).date()
                        dt = parser.parse(date.split('/')[0]).date()
                        return dt
                    except:
                        return date
                       
    return date
