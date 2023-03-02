import re
import pickle
import json
import os.path

def correct_date_format(retrieval_df):
    for index, row in retrieval_df.iterrows():
        #trying to find if the current date follow the format yyyy-mm-dd
        date = retrieval_df.loc[index, 'pub_date']
        date = str(date)
        regex = re.compile('^[\d]{4}-[\d]{2}-[\d]{2}$')
        result_date = re.findall(regex, date)
        if result_date != []:
            pass
        else:
            #if the date does not follow yyyy-mm-dd open the crossref file to find the date field we collected during the metadata retrieval
            crossref_ouptut_path = f'./output/crossref/p/'
            if os.path.exists(f"{crossref_ouptut_path}{index}.p") == True:
                f = open(f'{crossref_ouptut_path}{index}.json')
                crossref_file = json.load(f)
                f.close()
                new_date = crossref_file['message'].get('issued')            
                if new_date != None: 
                    #cheking that the field is composed of 3 parts year month day
                    if len(crossref_file['message']['issued'].get('date-parts')[0]) == 3:
                        #adding the 0 when needed to get the yyyy-mm-dd
                        if crossref_file['message']['issued'].get('date-parts')[0][1] > 9 and crossref_file['message']['issued'].get('date-parts')[0][2] > 9:
                            new_date = str(str(crossref_file['message']['issued'].get('date-parts')[0][0]) + '-' + str(crossref_file['message']['issued'].get('date-parts')[0][1]) + '-' + str(crossref_file['message']['issued'].get('date-parts')[0][2]))
                        elif crossref_file['message']['issued'].get('date-parts')[0][1] < 10 and crossref_file['message']['issued'].get('date-parts')[0][2] > 9:
                            new_date = str(str(crossref_file['message']['issued'].get('date-parts')[0][0]) + '-0' + str(crossref_file['message']['issued'].get('date-parts')[0][1]) + '-' + str(crossref_file['message']['issued'].get('date-parts')[0][2]))
                        elif crossref_file['message']['issued'].get('date-parts')[0][1] > 9 and crossref_file['message']['issued'].get('date-parts')[0][2] < 10:
                            new_date = str(str(crossref_file['message']['issued'].get('date-parts')[0][0]) + '-' + str(crossref_file['message']['issued'].get('date-parts')[0][1]) + '-0' + str(crossref_file['message']['issued'].get('date-parts')[0][2]))
                        else:
                            new_date = str(str(crossref_file['message']['issued'].get('date-parts')[0][0]) + '-0' + str(crossref_file['message']['issued'].get('date-parts')[0][1]) + '-0' + str(crossref_file['message']['issued'].get('date-parts')[0][2]))
                        #changing the date to the new format we found
                        retrieval_df.loc[index, 'pub_date'] = new_date
                    else:
                        pass
                else:
                    pass         
                #other tag we can find the date instead of publication date  
                new_date = crossref_file['message'].get('created')
                if new_date != None: 
                    if len(crossref_file['message']['created'].get('date-parts')[0]) == 3:
                        if crossref_file['message']['created'].get('date-parts')[0][1] > 9 and crossref_file['message']['created'].get('date-parts')[0][2] > 9:
                            new_date = str(str(crossref_file['message']['created'].get('date-parts')[0][0]) + '-' + str(crossref_file['message']['created'].get('date-parts')[0][1]) + '-' + str(crossref_file['message']['created'].get('date-parts')[0][2]))
                        elif crossref_file['message']['created'].get('date-parts')[0][1] < 10 and crossref_file['message']['created'].get('date-parts')[0][2] > 9:
                            new_date = str(str(crossref_file['message']['created'].get('date-parts')[0][0]) + '-0' + str(crossref_file['message']['created'].get('date-parts')[0][1]) + '-' + str(crossref_file['message']['created'].get('date-parts')[0][2]))
                        elif crossref_file['message']['created'].get('date-parts')[0][1] > 9 and crossref_file['message']['created'].get('date-parts')[0][2] < 10:
                            new_date = str(str(crossref_file['message']['created'].get('date-parts')[0][0]) + '-' + str(crossref_file['message']['created'].get('date-parts')[0][1]) + '-0' + str(crossref_file['message']['created'].get('date-parts')[0][2]))
                        else:
                            new_date = str(str(crossref_file['message']['created'].get('date-parts')[0][0]) + '-0' + str(crossref_file['message']['created'].get('date-parts')[0][1]) + '-0' + str(crossref_file['message']['created'].get('date-parts')[0][2]))
                        retrieval_df.loc[index, 'pub_date'] = new_date
                    else:
                        pass
                else:
                    pass
            else:
                pass
    return retrieval_df

