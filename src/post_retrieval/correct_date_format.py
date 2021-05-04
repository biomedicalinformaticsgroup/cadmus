import re
import pickle
import os.path

def correct_date_format(retrieval_df):
    for index, row in retrieval_df.iterrows():
        date = retrieval_df.loc[index, 'pub_date']
        date = str(date)
        regex = re.compile('^[\d]{4}-[\d]{2}-[\d]{2}$')
        result_date = re.findall(regex, date)
        if result_date != []:
            pass
        else:
            crossref_ouptut_path = f'./output/crossref/p/'
            if os.path.exists(f"{crossref_ouptut_path}{index}.p") == True:
                crossref_file = pickle.load(open(f"{crossref_ouptut_path}{index}.p", "rb"))
                new_date = crossref_file['message'].get('issued')            
                if new_date != None: 
                    if len(crossref_file['message']['issued'].get('date-parts')[0]) == 3:
                        if crossref_file['message']['issued'].get('date-parts')[0][1] > 9 and crossref_file['message']['issued'].get('date-parts')[0][2] > 9:
                            new_date = str(str(crossref_file['message']['issued'].get('date-parts')[0][0]) + '-' + str(crossref_file['message']['issued'].get('date-parts')[0][1]) + '-' + str(crossref_file['message']['issued'].get('date-parts')[0][2]))
                        elif crossref_file['message']['issued'].get('date-parts')[0][1] < 10 and crossref_file['message']['issued'].get('date-parts')[0][2] > 9:
                            new_date = str(str(crossref_file['message']['issued'].get('date-parts')[0][0]) + '-0' + str(crossref_file['message']['issued'].get('date-parts')[0][1]) + '-' + str(crossref_file['message']['issued'].get('date-parts')[0][2]))
                        elif crossref_file['message']['issued'].get('date-parts')[0][1] > 9 and crossref_file['message']['issued'].get('date-parts')[0][2] < 10:
                            new_date = str(str(crossref_file['message']['issued'].get('date-parts')[0][0]) + '-' + str(crossref_file['message']['issued'].get('date-parts')[0][1]) + '-0' + str(crossref_file['message']['issued'].get('date-parts')[0][2]))
                        else:
                            new_date = str(str(crossref_file['message']['issued'].get('date-parts')[0][0]) + '-0' + str(crossref_file['message']['issued'].get('date-parts')[0][1]) + '-0' + str(crossref_file['message']['issued'].get('date-parts')[0][2]))
                        retrieval_df.loc[index, 'pub_date'] = new_date
                    else:
                        pass
                else:
                    pass           
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
                #if retrieval_df.loc[index, 'pdf'] == 1:
                    #retrieval_df.loc[index, 'pub_date'] = new_date
    return retrieval_df

