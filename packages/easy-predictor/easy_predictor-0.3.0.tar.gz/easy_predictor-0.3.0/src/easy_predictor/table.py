from tabulate import tabulate
import pandas as pd 

def tabulator(path,data_type: str,columns: list[str]):

    dtype_list = ['xlsx','csv']
    
    if data_type not in dtype_list:
        print('Unknown dtype:',data_type)
    else:
        if data_type == dtype_list[0]:
            data = pd.read_excel(path)
            print(tabulate(data,headers=columns))

        if data_type == dtype_list[-1]:
            data = pd.read_csv(path)
            print(tabulate(data,headers=columns))

###########################

# from tabulate import tabulate
# import pandas as pd 

# def tabulator(path,columns: list[str]):
#     data = pd.read_excel(path)
#     for i in range(len(columns)):
#         print(tabulate(data,headers=[columns[i]]))

# dataset = "C:\\users\\USER\\Documents\\dataset_file\\scores_pred.xlsx"
# x = "Hour Study"
# y = "Scores"
# #tabulator(dataset,[x,y])