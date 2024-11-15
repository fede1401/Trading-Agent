
import os

"""
for path, direct, files in os.walk('../marketData'):
    print(path)
    print(direct)
    print(files)
    
    if 'CSCO.csv' in files:
            print('CSCO.csv found')
"""  

files = os.listdir('../marketData')
print(files)
if 'CSCO.csv' in files:
    print('CSCO.csv found')