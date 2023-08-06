import os
import re

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]



def readListFilesInFolder(path:str):
    listFilesRaw = os.listdir(path)
    #listFiles = sorted(listFilesRaw)#, key=len)
    listFiles = listFilesRaw
    listFiles.sort(key=natural_keys)
    resultList = list()
    
    for file in listFiles:
        if (
            (file[-1] == 'v') &
            (file[-2] == 's') &
            (file[-3] == 'c') &
            (file[-4] == '.')):
            resultList.append(file)
    return resultList


if __name__ == "__main__":
    print(readListFilesInFolder("D:\Document\eclipse-workspace2\data"))