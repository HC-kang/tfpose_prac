import math, mmap, tempfile
import numpy as np
import psutil

def _requiredSize(shape, dtype):
    '''
    형태와 종류에 따라 저장하기 위해 필요한 넘파이 배열의 용량을 결정
    '''
    return math.floor(np.prod(np.asarray(shape, dtype=np.uint64)) * np.dtype(dtype).itemsize)


class TempfileBackedArray(np.ndarray):
    '''
    a numpy ndarray that uses a memory-mapped temp fies as its backing
    '''

    def __new__(subtype, shape, dtype = float, buffer = None, offset = 0, strides = None, order = None, info = None):
        
        # array를 보관하기 위한 용량 결정
        numBytes = _requiredSize(shape, dtype)

        # temp 파일을 만들고 리사이즈 후 메모리에 맵핑
        tempFile = tempfile.TemporaryFile()
        tempFile.truncate(numBytes)
        buf = mmap.mmap(tempFile.fileno(), numBytes, access = mmap.ACCESS_WRITE)

        # Create the ndarray with the memory map as the underlying buffer
        obj = super(TempfileBackedArray, subtype).__new__(subtype, shape, dtype, buf, 0, None, order)
        
        # Attach the file reference to the ndarray object
        obj._file = tempFile
        return obj

    def __array_finalize__(self, obj):
        if obj is None: return
        self._file = getattr(obj, '_file', None)


def arrayFactory(shape, dtype = float):
    '''
    특정 형태와 데이터타입에 맞는 ndarray를 생성하고, 충분한 공간이 있다면 이를 메모리에 저장하고, 아니면 memory-mapped tempfile로 제공
    '''

    # array의 용량 결정
    requiredBytes = _requiredSize(shape, dtype)

    # 충분한 공간이 있는지 확인
    vmem = psutil.virtual_memory()
    if vmem.available > requiredBytes:
        return np.ndarray(shape = shape, dtype = dtype)
    else:
        return TempfileBackedArray(shape = shape, dtype = dtype)

def zerosFactory(shape, dtype = float):
    '''
    arrayFactory로 배열을 만들고 0으로 채워주기 // 왜 따로 분리했지..?
    '''
    arr = arrayFactory(shape = shape, dtype = dtype)
    arr.fill(0)
    return arr

def arrayCast(source, dtype):
    '''
    특정 형태와 데이터타입에 맞는 ndarray를 생성하고, 충분한 공간이 있다면 이를 메모리에 저장하고, 아니면 memory-mapped tempfile로 제공
    '''

    # 필요한 용량 확인
    requiredBytes = _requiredSize(source.shape, dtype)

    # 충분한 공간이 있는지 확인
    vmem = psutil.virtual_memory()
    if vmem.available > requiredBytes:
        return source.astype(dtype, subok = False) # subok??
    else:
        dest = arrayFactory(source.shape, dtype)
        np.copyto(dest, source, casting='unsafe')
        return dest

def determineMaxWindowSize(dtype, limit = None):
    '''
    데이터타입과 가용한 메모리에 따라 가용한 최대의 윈도우 사이즈를 설정
    
    만약 limit가 설정되면, 시스템에서 허용하는 가장 작은 값으로 반환됨
    '''
    vmem = psutil.virtual_memory()
    maxSize = math.floor(math.sqrt(vmem.available / np.dtype(dtype).itemsize))
    if limit is None or limit >= maxSize:
        return maxSize
    else:
        return limit
        