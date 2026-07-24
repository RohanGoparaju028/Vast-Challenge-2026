import pandas as pd 
import json 

def preprocessing(f):
    with open(f) as file:
        data = json.load(file)
    df_round = pd.json_normalize(data['rounds'])
    communications = []
    for round in data['rounds']:
        for msg in round.get('communications',[]):
            msg['hour'] = round['hour']
            communications.append(msg)
    df_communication = pd.json_normalize(communications )
    df = df_communication.merge(df_round,on="hour",how='left')
    return df 