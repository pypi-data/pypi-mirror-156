from easy_predictor import table

dataset = "C:\\users\\USER\\DOcuments\\Dataset_file\\scores_pred.xlsx"
x = "Hour Study"
y = "Scores"
table.tabulator(dataset,'xlsx',[x,y])