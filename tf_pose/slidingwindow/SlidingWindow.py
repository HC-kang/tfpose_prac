import math

class DimOrder(object):
    """
    데이터셋의 차원수를 나타냅디ㅏ
    """
    ChannelHeightWidth = ['c', 'h', 'w']
    HeightWIdthChannel = ['h', 'w', 'c']


class SlidingWindow(object):
    """
    큰 데이터셋을 들여다 볼 창의 크기를 설정합니다.
    """

    def __init__(self, x, y, w, h, dimOrder, transform = None):
        """
        세부적인 차원과 transform을 위한 창을 만듭니다.
        """
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.dimOrder = dimOrder
        self.transform = transform

    def apply(self, matrix):
        """
        입력된 행렬을 잘라내고 창과 연관된 tranform을 적용합니다.
        """
        view = matrix[self.indices()]
        return self.transform(view) if self.transform != None else view

    def getRect(self):
        '''
        Returns the window bounds as a tuple of x,y,w,h
        '''
        return (self.x, self.y, self.w, self.h)

    def setRect(self, rect):
        '''
        sets the window bounds from a tupel of x,y,w,h
        '''
        self.x, self.y, self.w, self.h = rect

    def indices(self, includeChannel = True):
        '''
        retrieve the indices for this window as a tuple of slices
        '''
        if self.dimOrder == DimOrder.HeightWIdthChannel:

            # [self.y:self.y + self.h + 1, self.x:self.x + self.w + 1] 과 같음
            return(
                slice(self.y, self.y+self.h),
                slice(self.x, self.x+self.w)
            )
        
        elif self.dimOrder == DimOrder.ChannelHeightWidth:

            if includeChannel is True:

            # [:, self.y:self.y + self.h + 1, self.x:self.x + self.w + 1] 과 같음
                return (
                    slice(None, None),
                    slice(self.y, self.y + self.h),
                    slice(self.x, self.x + self.w)
                )

            else:

                # [self.y:self.y + self.h + 1, self.x:self.x + self.w + 1] 과 같음
                return(
                    slice(self.y, self.y+self.h),
                    slice(self.x, self.x+self.w)
                )

        else:
            raise Exception('Unsupported order of dimensions: ' + str(self.dimOrder))

    
    def __str__(self):
        return '(' + str(self.x) + ',' + str(self.y) + ',' + str(self.w) + ',' + str(self.h) + ')'

    def __repr__(self):
        return self.__str__()


def generate(data, dimOrder, maxWindowSizeW, maxWindowSizeH, overlapPercent, transforms = []):
    '''
    특정 데이터셋을 위한 슬라이딩 윈도우를 생성합니다.
    '''

    # 입력 데이터의 차원을 결정합니다.
    width = data.shape[dimOrder.index('w')]
    height = data.shape[dimOrder.index('h')]

    # 윈도우 생성
    return generateForSize(width, height, dimOrder, maxWindowSizeW, maxWindowSizeH, overlapPercent, transforms)

def generateForSize(width, height, dimOrder, maxWindowSizeW, maxWindowSizeH, overlapPercent, transforms = []):
    '''
    특정 차원과 순서에 맞는 데이터를 위한 슬라이딩 윈도우들을 생성합니다.
    '''

    # 만약 입력 데이터가 윈도우 사이즈보다 작은 경우, 윈도우 사이즈를 입력데이터에 맞춤.
    windowSizeX = min(maxWindowSizeW, width)
    windowSizeY = min(maxWindowSizeH, height)

    # 윈도우의 오버랩과 스텝사이즈 계산
    windowOverlapX = int(math.floor(windowSizeX * overlapPercent))
    windowOverlapY = int(math.floor(windowSizeY * overlapPercent))
    stepSizeX = windowSizeX - windowOverlapX
    stepSizeY = windowSizeY - windowOverlapY

    # 입력데이터를 덮기 위해 필요한 윈도우의 수 결정
    lastX = width - windowSizeX
    lastY = height - windowSizeY
    xOffsets = list(range(0, lastX + 1, stepSizeX))
    yOffsets = list(range(0, lastY + 1, stepSizeY))

    # 입력 데이터의 차원이 정확히 스텝사이즈의 배수가 아니라면, 열과 행에 하나씩 추가적으로 윈도우가 필요함.
    if len(xOffsets) == 0 or xOffsets[-1] != lastX:
        xOffsets.append(lastX)
    if len(yOffsets) == 0 or yOffsets[-1] != lastY:
        yOffsets.append(lastY)

    # 윈도우 리스트 생성
    windows = []
    for xOffset in xOffsets:
        for yOffset in yOffsets:
            for transform in [None] + transforms:
                windows.append(SlidingWindow(
                    x = xOffset,
                    y = yOffset,
                    w = windowSizeX,
                    h = windowSizeY,
                    dimOrder = dimOrder,
                    transform = transform
                ))

    return windows