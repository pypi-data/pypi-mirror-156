'''
mcreep.io
-----------
Input/output functions for package mdbase.    
'''

import sys
import pandas as pd

def read_single_database(EPAR, excel_file, sheet_name):
    
    # Read file to numpy array and try to catch possible errors/exceptions
    try:
        df = pd.read_excel(
            excel_file, sheet_name, skiprows=9)
    except OSError as err:
        # Something went wrong...
        print('OSError:', err)
        sys.exit()
    # Return pd.DataFrame
    return(df)

def read_multiple_databases(EPAR, excel_files, sheet_names):
    df = pd.DataFrame()
    for file in excel_files:
        for sheet in sheet_names:
            temp = read_single_database(EPAR, file, sheet)
            df = pd.concat(df, temp)
    return(df)
