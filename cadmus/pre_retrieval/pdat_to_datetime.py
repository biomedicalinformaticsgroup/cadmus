from dateutil import parser
 # could be improved to deal with other date fromats (if len(date.split()) == 3 then use year, month, day as input for datetime object)
 
def pdat_to_datetime(pdat_string): 
    try:
        date = parser.parse(pdat_string).date()
    except:
        date = pdat_string
    return date