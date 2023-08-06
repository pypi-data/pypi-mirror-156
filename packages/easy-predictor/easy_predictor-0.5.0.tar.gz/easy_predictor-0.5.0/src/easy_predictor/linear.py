from sklearn.linear_model import LinearRegression
import pandas as pd 

def predict(data: str,data_type: str,x: str, y: str,value: int):

    ERROR_LIST = {
        'null_value': "'value' Input can't be null",
        'null_dataset': "'data' can't be null"
    }

    value_list = [value]

    if data == None:
        print(ERROR_LIST['null_dataset'])
    else:
        if data_type == 'xlsx':
            if len(value_list) != 0:
                data = pd.read_excel(data)

                train = data[[x]].values
                predict_value = data[[y]].values
                
                lr = LinearRegression()
                lr.fit(train,predict_value) 
                print(lr.predict([[value]]))
            else:
                print(ERROR_LIST['null_value'])

        elif data_type == 'csv':   
            if len(value_list) != 0:
                data = pd.read_csv(data)

                train = data[[x]].values
                predict_value = data[[y]].values
                
                lr = LinearRegression()
                lr.fit(train,predict_value) 
                print(lr.predict([[value]]))
            else:
                print(ERROR_LIST['null_value'])