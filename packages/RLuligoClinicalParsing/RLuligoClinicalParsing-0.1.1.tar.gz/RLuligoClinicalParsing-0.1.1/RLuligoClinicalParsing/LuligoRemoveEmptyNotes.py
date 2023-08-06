import pandas as pd

def LuligoRemoveEmptyNotes(df):
    rows = df[df['line_num'].isna()].index
    df.drop(rows, inplace=True)
    return df