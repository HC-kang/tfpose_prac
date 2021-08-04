from .ArrayUtils import *
import numpy as np
import math

def generateDistanceMatrix(width, height):
    '''
    각 점에서 중앙까지의 거리를 지정하는 행렬을 생성함.
    '''

    # 정확히 윈도우의 중앙 좌표를 결정
    originX = width / 2
    originY = height / 2

    # 거리 행렬을 생성
    distances = zerosFactory((height, width), dtype = np.float)
    for index, val in np.ndenumerate(distances):
        y, x = index
        distances[(y, x)] = math.sqrt(math.pow(x - originX, 2) + math.pow(y - originY, 2))
    
    return distances