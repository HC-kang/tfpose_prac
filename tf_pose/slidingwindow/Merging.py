from .SlidingWindow import generate
from .Batching import batchWindows
import numpy as np

def mergeWindows(data, dimOrder, maxWindowSize, overlapPercent, batchSize, transform, progressCallback = None):
    '''
    지정된 데이터셋에 맞는 윈도우를 생성하고, 각 윈도우에 지정된 트랜스폼을 적용함.
    윈도우가 겹치는 부분은 평균값으로 해결
    
    입력 데이터의 차원 순서와는 관계없이, 함수는 NumPy Array를 반환해야함
    [batch, height, width, resultChannels]

    callback이 제공된다면 윈도우의 각 배치가 적용되기 직전에 호출될것이고, 
    콜백은 현재의 배치 인덱스와 배치의 수를 인수로 받아야함.
    '''

    # 입력 데이터의 차원수 결정
    sourceWidth = data.shape[dimOrder.index('w')]
    sourceHeight = data.shape[dimOrder.index('h')]

    # 슬라이딩 윈도우를 만들고, 배치로 그룹화해주기
    windows = generate(data, dimOrder, maxWindowSize, overlapPercent)
    batches = batchWindows(windows, batchSize)

    # 첫 번째 배치에 tranform 적용 및 차원수 결정
    examplarResult = transform(data, batches[0])
    resultDimensions = examplarResult.shape[len(examplarResult.shape) - 1]

    # sum 과 counts 를 저장할 변수 만들어주기
    sums = np.zeros((sourceHeight, sourceWidth, resultDimensions), dtype = np.float)
    counts = np.zeros((sourceHeight, sourceWidth), dtype = np.uint32)

    # 각 배치에 대해 트랜스폼 적용
    for batchNum, batch in enumerate(batches):

        # 콜백이 지원된다면 불러주기
        if progressCallback != None:
            progressCallback(batchNum, len(batches))
        
        # 현재 배치에 트랜스폼 적용해주기
        batchResult = transform(data, batch)

        # 각 배치의 윈도우에 대해서 반복, sums matrix 업데이트
        for windowNum, window in enumerate(batch):

            # Create views into the larger matrices that correspond to the current window
            windowIndices = window.indices(False)
            sumsView = sums[windowIndices]
            countsView = counts[windowIndices]

            # 
            sumsView[:] += batchResult[windowNum]
            countsView[:] += 1

    # sum 과 counts로 평균값 계산해주기
    for dim in range(0, resultDimensions):
        sums[:, :, dim] /= counts

    # 평균값 리턴
    return sums