import numpy as np
import math

def cropRect(rect, cropTop, cropBottom, cropLeft, cropRight):
    '''
    지정된 픽셀로 사각형을 잘라냄.
    입력값과 출력값은 둘 다 튜플형태임 (x, y, w, h)
    '''

    # 튜플 풀기
    x, y, w, h = rect

    # 지정값으로 자르기
    x += cropLeft
    y += cropTop
    w -= (cropLeft + cropRight)
    h -= (cropTop + cropBottom)

    # 다시 묶기
    return (x, y, w, h)

def padRect(rect, padTop, padBottom, padLeft, padRight, bounds, clipExcess = True):
    '''
    사각형을 지정값에 따라 각 면을 패딩.
    특정 경계 안에 속하도록 확인
    
    입력값 등은 모두 (x, y, w, h)형태
    '''
    # 튜플 풀기
    x, y, w, h = rect

    # 패딩 주기
    x -= padLeft
    y -= padTop
    w += (padLeft + padRight)
    h += (padTop + padBottom)

    # 오버/언더플로 여부 확인 및 중앙의 위치 보정을 위해 이동
    if clipExcess == True:
        
        # 언더플로 클립
        x = max(0, x)
        y = max(0, y)

        # 오버플로 클립
        overflowY = max(0, (y+h) - bounds[0])
        overflowX = max(0, (x+w) - bounds[1])
        h -= overflowY
        w -= overflowX

    else:
        # 언더플로만큼 보상해주기
        underflowX = max(0, 0-x)
        underflowY = max(0, 0-y)
        x += underflowX
        y += underflowY

        # 오버플로만큼 보상해주기
        overflowY = max(0, (y + h) - bounds[0])
        overflowX = max(0, (x + w) - bounds[1])
        x -= overflowX
        w += overflowX
        y -= overflowY
        h += overflowY

        # 이렇게 해줘도 계속 모자란다면 답이없음
        x, y, w, h = padRect((x, y, w, h), 0, 0, 0, 0, bounds, True)

    return (x, y, w, h)


def cropRectEqually(rect, cropping):
    '''
    모든 면을 지정값으로 크롭
    입출력값은 모두 (x, y, w, h)
    '''
    return cropRect(rect, cropping, cropping, cropping, cropping)
    

def padRectEqually(rect, padding, bounds, clipExcess = True):
    '''
    사각형의 모든 면에 패딩 적용
    지정범위에 들도록 확인.
    
    모든 값은 (x, y, w, h) 형태임
    '''
    return padRect(rect, padding, padding, padding, padding, bounds, clipExcess)


def squareAspect(rect):
    '''
    필요에 따라 높이와 너비를 잘라 정사각형으로 만들기
    모든 형태는 (x, y, w, h)
    '''

    # 어떤 면이 크롭될지 결정
    x, y, w, h = rect
    if w > h:
        cropX = (w - h) // 2
        return cropRect(rect, 0, 0, cropX, cropX)
    elif w < h:
        cropY = (h - w) // 2
        return cropRect(rect, cropY, cropY, 0, 0)

    # 아니면 이미 정사각형임
    return rect


def fitToSize(rect, targetWidth, targetHeight, bounds):
    '''
    목표 크기에 따라 사각형을 크롭 또는 패딩하고, 지정된 범위에 있는지 확인
    
    모든 형태는 (x, y, w, h)
    '''

    # 현재 크기와 타겟 사이즈의 차이 확인
    x, y, w, h = rect
    diffX = w - targetWidth
    diffY = h - targetHeight

    # 너비를 크롭할지, 패딩할지 선택
    if diffX > 0:
        cropLeft = math.floor(diffX / 2)
        cropRight = diffX - cropLeft
        x, y, w, h = cropRect((x, y, w, h), 0, 0, cropLeft, cropRight)
    elif diffX < 0:
        padLeft = math.floor(abs(diffX) / 2)
        padRight = abs(diffX) - padLeft
        x, y, w, h = padRect((x, y, w, h), 0, 0, padLeft, padRight, bounds, False)

    # 높이를 크롭할지, 패딩할지 선택
    if diffY > 0:
        cropTop = math.floor(diffY / 2)
        cropBottom = diffY - cropTop
        x, y, w, h = cropRect((x, y, w, h), cropTop, cropBottom, 0, 0)
    elif diffY < 0:
        padTop = math.floor(abs(diffY) / 2)
        padBottom = abs(diffY) - padTop
        x, y, w, h = padRect((x, y, w, h), padTop, padBottom, 0, 0, bounds, False)
    
    return (x, y, w, h)