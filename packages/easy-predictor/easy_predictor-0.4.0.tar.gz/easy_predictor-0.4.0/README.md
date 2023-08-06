# Easy Predictor 

Perform regression/classification prediction on small Excel dataset in one line!

# Side Note

Currently only two columns are allowed be use on the prediction (Independent & Dependent variable).

## Instruction

1. Linear Regression Prediction

```python
from easy_predictor import linear 

dataset = "path_to_excel_file"
linear.predict(dataset,dataset_type: 'xlsx','csv',column_x,column_y,value: int)
```
2. Text Classification Prediction

```python
from easy_predictor import classification

dataset = "path_to_excel_file"
classification.predict(dataset,dataset_type: 'xlsx','csv',column_x,column_y,value: str)
```

3. Visualize Data

```python
from easy_predictor import table

dataset = "path_to_excel_file"
table.tabulator(dataset,dataset_type: 'xlsx','csv',columns=list[str])
```

## Latest Update 0.2.0

```
CSV (Comma Seperated Values) File supported
```
## Latest Update 0.3.0

```
New 'table' Function To Visualize Data In Tabular Form
```

## Latest Update 0.4.0

```
ImportError: cannot import name 'table' from 'easy_predictor'. Bug
fixed
```