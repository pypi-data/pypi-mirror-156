import csv
from dataclasses import dataclass
from datetime import date
import numpy as np

@dataclass
class Data():
    matrix:np.ndarray
    timeSlice:float
    delay:float
    id:str
    dateRec:str

def readCSV(fileName):
    resultArray = np.zeros(shape=(1024,40))
    delay:float
    timeSlice:float
    with open(fileName, 'r', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';')#, quotechar='')
        next(spamreader)
        rowDescription = next(spamreader)
        id = rowDescription[0]
        dateRec = rowDescription[1]
        timeSlice = float(rowDescription[2]) * 0.000001
        delay = rowDescription[3]
        i=0
        for row in spamreader:
            j=0
            for cell in row:
                if cell == "": 
                    continue
                resultArray[i][j] = float(cell)
                j=j+1
            i=i+1
    return Data(resultArray,float(timeSlice),float(delay),id,dateRec)
            
if __name__ == "__main__":
    readCSV("D:\Document\eclipse-workspace2\data\TICRaw_1_2021-12-22 21_28_52.csv")