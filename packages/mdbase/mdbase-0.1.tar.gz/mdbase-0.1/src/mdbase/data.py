'''
mdbase.data
-----------
Additional manipulations with data in the input database.
'''

import numpy as np

def add_normalized_OI(df):
    LengthInVivo = replace_non_numeric_values(df.LengthInVivo)
    OI_ave_W = replace_non_numeric_values(df.OI_ave_W)
    OI_max_W = replace_non_numeric_values(df.OI_max_W)
    OI_ave_U = replace_non_numeric_values(df.OI_ave_U)
    OI_max_U = replace_non_numeric_values(df.OI_max_U)
    OI_ave = replace_non_numeric_values(df.OI_ave)
    OI_max = replace_non_numeric_values(df.OI_max)
    df['OI_ave_W_n'] = OI_ave_W / LengthInVivo
    df['OI_max_W_n'] = OI_max_W / LengthInVivo
    df['OI_ave_U_n'] = OI_ave_U / LengthInVivo
    df['OI_max_U_n'] = OI_max_U / LengthInVivo
    df['OI_ave_n']   = OI_ave  / LengthInVivo
    df['OI_max_n']   = OI_max   / LengthInVivo
    return(df)

def sub_database_with_nonzero_values(df, properties):
    ds = df[properties]
    ds = ds.dropna()
    return(ds)

def replace_non_numeric_values(df):
    ds = df.replace(['?','x','n'],[np.nan, np.nan, np.nan])
    ds = ds.replace(0.0, np.nan)
    return(ds)

def exclude_too_early_explants(df, minimum_in_vivo=0.1):
    ds = df[df.FinalEvaluation != 'new_liner']
    ds = ds[ds.LengthInVivo >= minimum_in_vivo]
    return(ds)

def exclude_too_high_oxidations(df, OI_limit = 3):
    ds = df[df.OI_max < OI_limit]
    return(ds)