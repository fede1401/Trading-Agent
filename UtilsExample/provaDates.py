import sys
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent')
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/db')

from db import insertDataDB, connectDB
from datetime import datetime, time, timedelta


# Connessione al database
cur, conn = connectDB.connect_nasdaq()

cur.execute(f"SELECT time_value_it FROM nasdaq_actions order by time_value_it;")
result = {res[0] for res in cur.fetchall()}

cur.execute(f"SELECT time_value_it FROM nyse_actions order by time_value_it;")
result1 = {res1[0] for res1 in cur.fetchall()}


cur.execute(f"SELECT time_value_it FROM larg_comp_eu_actions order by time_value_it;")
result2 = {res2[0] for res2 in cur.fetchall()}

print(len(result))
print(len(result1))
print(len(result2))

arr1 = []
arr2 = []
arr3 = []

for d in result:
    if d not in result1:
        arr1.append(d.strftime('%Y-%m-%d %H:%M:%S'))
    if d not in result2:
        arr1.append(d.strftime('%Y-%m-%d %H:%M:%S'))
        
#print(arr1)
print()

for d in result1:
    if d not in result:
        arr2.append(d.strftime('%Y-%m-%d %H:%M:%S'))
    if d not in result2:
        arr2.append(d.strftime('%Y-%m-%d %H:%M:%S'))

#print(arr2)
print()


for d in result2:
    if d not in result:
        arr3.append(d.strftime('%Y-%m-%d %H:%M:%S'))
    if d not in result1:
        arr3.append(d.strftime('%Y-%m-%d %H:%M:%S'))
        
#print(arr3)
print()
print()


for el in arr2:
    if el[0:3] >= '1975':
        print(el)
        
print()
print()

        
for el in arr3:
    if el[0:3] >= '2000':
        print(el)