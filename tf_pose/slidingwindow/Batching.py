import numpy as np

def batchWindows(windows, batchSize):
    '''
    윈도우 리스트를 배치 시리즈로 나누기
    '''
    return np.array_split(np.array(windows), len(windows) // batchSize)
