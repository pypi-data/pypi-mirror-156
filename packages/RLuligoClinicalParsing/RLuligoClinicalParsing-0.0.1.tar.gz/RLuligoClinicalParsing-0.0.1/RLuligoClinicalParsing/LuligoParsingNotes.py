import pandas as pd
import re
#import RLuligoClinicalParsing.constants as constants

def LuligoParsingNotes(csvfile, fsep, tdelimiter):
    sep = '\u0000' #constants.SEP
    df = pd.read_csv(csvfile, sep=sep , encoding='utf8',  header=None, names=['text']  )
    if(fsep == '|'):
        df = df.text.replace(to_replace=f'{tdelimiter}\|{tdelimiter}', regex=True, value=sep)
    else:
        df = df.text.replace(to_replace=f'{tdelimiter}{fsep}{tdelimiter}', regex=True, value=sep) 
    df = df.to_frame()
    
    #adding more pattern cases (replace nested pipes in Text)
    patern = '((?<![\\])[|])'
    df = df.text.replace(to_replace=r'((?<![\\])['+fsep+'])', regex=True, value=f'\{fsep}')
    df = df.to_frame()
    
    #removes first and last text identifiers
    pattern = f'^{ tdelimiter}|{tdelimiter}$',
    df = df.text.replace(to_replace=pattern, regex=True, value='')
    df = df.to_frame()
    
    
    
    #################################SET HEADERS AND FIELDS
    
    df = df.text.str.split(pat=sep,expand=True)
    new_header = df.iloc[0] #grab the first row for the header
    df = df[1:] #take the data less the header row
    df.columns = new_header #set the header row as the df header
    
    return df