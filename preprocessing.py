import pandas as pd 
import json 

def preprocessing(f):
    with open(f) as file:
        data = json.load(file)
    df = pd.json_normalize(data['rounds'])
    print(df.columns)