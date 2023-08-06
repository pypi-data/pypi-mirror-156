"""
Copyright © 2022 by Lance Edward Darragh. All rights reserved. This software may be used, but not reproduced or distributed, for free. This software may not be reproduced or distributed without the author's written consent. To obtain consent, contact the author at ForDataScience@gmx.com.
"""
import numpy as np
import pandas as pd
from numpy import sqrt as sqrt

def categorical_prediction_coefficient_matrix(data, weighted = False):
    """
    This function returns a correlation matrix with the categorical prediction coefficient values. 
    data is the input dataset as a pandas DataFrame.
    weighted can be either True or False (default). If False, the nonweighted prediction coefficient will be returned. If True, the weighted prediction coefficient will be returned.
    """
    if type(data) != type(pd.DataFrame(None)):
        print('Currently, only pandas DataFrames are supported inputs. Other data types will be supported in a future release. For now, please convert your input to a pandas DataFrame and try again.')
        return

    def variation(row):
        expected_value = 1/len(df_contingency.columns)
        sum_of_squares = 0
        for value in row.index.to_list():
            sum_of_squares += (row[value] - expected_value)**2
        return sqrt(sum_of_squares)/sqrt((len(df_contingency.columns) - 1)/len(df_contingency.columns))
    
    columns = [x for x in data.columns.to_list() if data[x].dtype in ['O', 'object', 'bool', 'datetime64', 'timedelta64']]
    if len(columns) == 0:
        print('No supported data types detected. Please convert all data types to \'O\', \'object\', \'bool\', \'datetime64\', or \'timedelta64\' and try again.')
        return
    elif len(columns) == 1:
        print('Only one supported data types detected. Please convert all data types to \'O\', \'object\', \'bool\', \'datetime64\', or \'timedelta64\' and try again.')
        return
    df_results = pd.DataFrame(None, index = columns, columns = columns)
    for col1 in columns:
        for col2 in columns:
            df_contingency = pd.crosstab(data[col1], columns = data[col2]).replace(np.NaN, 0)
            weights = df_contingency.sum(axis = 1)
            df_contingency = df_contingency.div(weights, axis = 0)
            if weighted == False:
                omega = df_contingency.apply(variation, axis = 1).mean()
            elif weighted == True:
                if col1 != col2:
                    omega = (df_contingency.apply(variation, axis = 1)*(weights/weights.max())).mean()
                else:
                    omega = 'NA'
            df_results.loc[col1, col2] = omega

    return df_results
