import sys

from datetime import datetime
import csv

#import torch  # PyTorch per calcoli su GPU (se applicabile)
import logging

import os
from pathlib import Path

# Trova dinamicamente la cartella Trading-Agent (cartella principale) e la aggiunge al path
current_path = Path(__file__).resolve()
while current_path.name != 'Trading-Agent':
    if current_path == current_path.parent:  # Se raggiungiamo la root senza trovare Trading-Agent
        raise RuntimeError("Errore: Impossibile trovare la cartella Trading-Agent!")
    current_path = current_path.parent

# Aggiunge la root al sys.path solo se non è già presente
if str(current_path) not in sys.path:
    sys.path.append(str(current_path))

from manage_module import get_path_specify, project_root

# Ora possiamo importare `config`
get_path_specify(["db", "symbols", "workHistorical", "utils"])

# Importa i moduli personalizzati
from database import connectDB
from manage_module import get_path_specify, market_data_path, project_root
import traceback
from utils import generateiRandomDates2

import matplotlib.pyplot as plt
import numpy as np

#xpoints = np.array([1, 8])
#ypoints = np.array([3, 10])

#plt.plot(xpoints, ypoints)
#plt.show()


def get_data_from_db():
    # Connetti al database
    cur, conn = connectDB.connect_nasdaq()
    
    cur.execute(f"SELECT agent, roi, notes from middleProfit;")
    rows = cur.fetchall()
    #print(rows)
    conn.close()
    return rows

def seePlotFromData(data):
    xPoints = []
    yPoints = []
    i = 0
    legend = []
    for row in data:
        i += 1
        legend.append(f'{i}: {row[0]}: {row[2]}\n')
        xPoints.append(i)
        yPoints.append(row[1])
    #print(xPoints)
    #print(yPoints)
    print(legend)
    plt.plot(xPoints, yPoints)
    plt.show()
    #print(legend)
        
        

dataResult = get_data_from_db()
seePlotFromData(dataResult)


    
    