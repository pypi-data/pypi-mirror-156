## CSV DB CLASS

A python package for easy python database usage through CSVs.

Usage:


```
>>> from csvdbclass import csvDB
>>> data = csvDB("data")
>>> data.show()
data
Empty DataFrame
Columns: []
Index: []
>>> data.db = pandas.DataFrame({
...     "Name" : ['joe', 'joe2', 'joe3']
... })
>>> data.show()
data
   Name
0   joe
1  joe2
2  joe3
```