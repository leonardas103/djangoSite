import math
import multiprocessing as mp
import os
import time
import numpy as np
from joblib import Parallel, delayed


def info(title):
	print('axis: %s pid: %s'% (title,os.getpid()) )

def shiftImage(image, dx, dy):
	height, width = np.shape(image)
	shift = np.roll(image, dx, axis=1)
	shift = np.roll(shift, dy, axis=0)
	if dx > 0:
		shift[:,0:dx] = 0
	elif dx < 0:
		shift[:,width+dx:width] = 0
	if dy > 0:
		shift[0:dy,:] = 0
	elif dy < 0:
		shift[height+dy:height,:] = 0
	return shift

def shiftImageHelper_joblib(imageTiles, shift, axis):
	ret = Parallel(n_jobs=num_cores)(delayed(np.roll)(imageTiles[i], shift, axis) for i in range(num_cores))

	if axis == 1:
		return np.vstack(ret)
	return np.hstack(ret)

def shiftImageParallel_joblib(image, dx, dy):
	if not dx == 0:
		tile_row = np.array_split(image, num_cores, axis=0)
		image = shiftImageHelper_joblib(tile_row, dx, 1)
	if not dy == 0:
		tile_col = np.array_split(image, num_cores, axis=1)
		image = shiftImageHelper_joblib(tile_col, dy, 0)
	return image

def shiftImageWorker(queue, image, dx, dy):
	shift = np.roll(image, dx, axis=1)
	shift = np.roll(shift, dy, axis=0)
	if dx > 0:
		shift[:,0:dx] = 0
	else:
		shift[:,dx:] = 0

	if dy > 0:
		shift[0:dy,:] = 0
	else:
		shift[dy:,:] = 0
	queue.put(shift)

def shiftImageHelper(imageTiles, dx, dy):
	queues = [mp.Queue() for i in range(num_cores)]
	jobs = [mp.Process(target=shiftImageWorker, args=[queues[i], imageTiles[i], dx, dy]) for i in range(num_cores)]
	
	for job in jobs: job.start()
	ret = [queue.get() for queue in queues]
	for job in jobs: job.join()
	
	return ret


def shiftImageParallel(image, dx, dy):
	overlap = max(abs(dx),abs(dy))
	tiles = split(image, overlap)
	shifted = shiftImageHelper(tiles, dx, dy)
	ret = merge(image, shifted, overlap)
	return ret

def split(image, overlap):
    height, width = np.shape(image)
    tiles = []
    step = int(np.ceil(width/(num_cores//2)))
    tile_num = 0
    for i, row in enumerate([0, height//2]): 
        for j, col in enumerate(range(0, width, step)):
            if(col+step >= width): #last col
                last_tile = image[row:row+height//2+2*overlap:,col:width]
                if(row == height//2):
                    last_tile = image[row:height:,col:width]
                if len(last_tile) > overlap:
                    tiles.append(last_tile)
                    tile_num += 1 
            else:
                tiles.append(image[row:row+height//2+2*overlap:,col:col+step+2*overlap])
                tile_num += 1 
            # print('step:%s overlap:%s i:%s col:%s #cols:%s' % (step, overlap, i ,col, range(0, len(image), step)))
            # print(tiles[tile_num-1])
    return tiles

def merge(image, tiles, overlap):
    height, width = np.shape(image)
    result = np.empty_like(image)
    step = int(np.ceil(width/(num_cores//2)))
    tile_num = 0
    for i, _ in enumerate([0, height//2]): 
        for j, col in enumerate(range(0, width, step)):
            if (i == 0):
                if(j==0):
                    result[0:overlap+height//2, 0:step+overlap] = tiles[tile_num][0:height//2 + overlap, 0:step+overlap]
                else:
                    result[0:overlap+height//2, col+overlap:col+step+overlap] = tiles[tile_num][0:height//2 + overlap, overlap:step+overlap]
            else:
                if(j==0):
                    result[overlap+height//2:height, col:col+step+overlap] = tiles[tile_num][overlap:height//2 + overlap, 0:step+overlap]
                else:        
                    result[overlap+height//2:height, col+overlap:col+step+overlap] = tiles[tile_num][overlap:height//2 + overlap, overlap:step+overlap]
            tile_num += 1
    return result


num_cores = mp.cpu_count()

def main():
	image = []
	for i in range(1): 
		image.append(np.matrix(np.random.randint(0,255, size=(20000, 20000))))
	dx, dy = 10, 12

	t0 = time.time()
	for i in range(1):  
		A = shiftImage(image[i], dx, dy) 
	print('--------------')
	print('time1:', (time.time()-t0)*1000)

	

	t0 = time.time()
	for i in range(1):   
		B = shiftImageParallel(image[i], dx, dy)
	print('--------------')
	print('time2:', (time.time()-t0)*1000)

	# t0 = time.time()
	# for i in range(1):   
	# 	C = shiftImageParallel_joblib(image[i], dx, dy)
	# print('--------------')
	# print('time3:', (time.time()-t0)*1000)

	# print(image[0])
	# print('--------------')
	# print('A:\n',A)
	# print('--------------')
	# print('B\n',B)
	# print('--------------')
	# print('C\n',C)

	# print("A == B:", np.isclose(A, B).all())
	# print("A == C:", np.isclose(A, C).all())

if __name__ == '__main__':
	# freeze_support()
	main()