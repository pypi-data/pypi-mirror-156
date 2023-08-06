from sklearn.linear_model import LinearRegression
import pandas as pd 

def predict(data: str,data_type: str, input_col: list[str],value: list[int],output_col: str):

    ERROR_LIST = {
        'null_value': "'value' Input can't be null",
        'null_dataset': "'data' can't be null"
    }

    value_list = [value]

    if data_type == 'xlsx':
        if len(value_list) != 0:
            data = pd.read_excel(data)

            column_x = data[input_col].values
            column_y = data[[output_col]].values
            
            lr = LinearRegression()
            lr.fit(column_x,column_y) 
            print(lr.predict([value]))
        else:
            print(ERROR_LIST['null_value'])

    if data_type == 'csv':   
        if len(value_list) != 0:
            data = pd.read_csv(data)

            column_x = data[input_col].values
            column_y = data[[output_col]].values
            
            lr = LinearRegression()
            lr.fit(column_x,column_y) 
            print(lr.predict([value]))
        else:
            print(ERROR_LIST['null_value'])