import numpy as np


class CalibrationGaloHandler():
    def __init__(self,coefLT,coefRT,coefLB,coefRB):
        self.__coefLT = coefLT
        self.__coefRT = coefLT
        self.__coefLB = coefLT
        self.__coefRB = coefLT
    def getCalibratedValueByGaloValue(self,countLT,countRT,countLB,countRB):
        return (countLT*self.__coefLT + countRT*self.__coefRT + countLB*self.__coefLB + countRB*self.__coefRB)/4
    def getLeftTop(self):
        return self.__coefLT
    def getRightTop(self):
        return self.__coefRT
    def getLeftBottom(self):
        return self.__coefLB
    def getRightBottom(self):
        return self.__coefRB