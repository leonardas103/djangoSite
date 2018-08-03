import math
import multiprocessing as mp
import os
import time
import numpy as np
from timeit import timeit

def time_split_merge():
    image = np.matrix(np.random.randint(0,255, size=(5000, 5000)))
    t0 = time.time()
    tile_row = np.array_split(image, num_cores, axis=0)
    result = np.vstack(tile_row)
    tile_col = np.array_split(image, num_cores, axis=1)
    result2 = np.hstack(tile_col)
    t2 = (time.time()-t0)*1000
    print('time split merge:', t2)

def shiftImage(image, dx, dy):
	shift = np.roll(image, dx, axis=1)
	shift = np.roll(shift, dy, axis=0)
	return shift

def time_shift(image):
    t0 = time.time()
    result = shiftImage(image, 13, -7) 
    t2 = (time.time()-t0)*1000
    print('time shift:', t2)

def func(args):
    a,b,c = args
    print('func called:',a,b,c)
    return np.roll(a,b,c)
    
def testPool():
    arr = [[1,2,3], [4,5,6], [7,8,9]]
    args = zip(arr, [2,2,2], [0,0,0])
    with mp.Pool(num_cores) as p:
        result = p.map(func, args)
        print(result)

num_cores = mp.cpu_count()

if __name__ == '__main__':
    image = np.matrix(np.random.randint(0,255, size=(10000, 10000)))
    # time_split_merge()
    # time_shift(image)
    testPool()