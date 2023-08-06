from tabulate import tabulate
import pandas as pd 

def tabulator(path,data_type: str,columns: list[str]):

    dtype_list = ['xlsx','csv']
    
    if data_type == dtype_list[0]:
        data = pd.read_excel(path)
        print(tabulate(data,headers=columns))

    if data_type == dtype_list[-1]:
        data = pd.read_csv(path)
        print(tabulate(data,headers=columns))