import math
import multiprocessing as mp
import os
import time
import numpy as np
from joblib import Parallel, delayed


def info(title):
	print('axis: %s pid: %s'% (title,os.getpid()) )

def shiftImage(image, dx, dy):
	shift = np.roll(image, dx, axis=1)
	shift = np.roll(shift, dy, axis=0)
	return shift


def shiftImageWorker(queue, image, shift, axis):
	queue.put(np.roll(image, shift, axis=axis))

def shiftImageHelper(imageTiles, shift, axis):
	queues = [mp.Queue() for i in range(num_cores)]
	jobs = [mp.Process(target=shiftImageWorker, args=[queues[i], imageTiles[i], shift, axis]) for i in range(num_cores)]
	
	for job in jobs: job.start()
	ret = [queue.get() for queue in queues]
	for job in jobs: job.join()
	
	if axis == 1:
		return np.vstack(ret)
	return np.hstack(ret)

def shiftImageWorker2(queue, image, shift, axis):
	queue.put(np.roll(image, shift, axis=axis))

def shiftImageHelper2(imageTiles, shift, axis):
	ret = Parallel(n_jobs=num_cores)(delayed(np.roll)(imageTiles[i], shift, axis) for i in range(num_cores))
	# print(ret)
	if axis == 1:
		return np.vstack(ret)
	return np.hstack(ret)

def shiftImageParallel2(image, dx, dy):
	if not dx == 0:
		tile_row = np.array_split(image, num_cores, axis=0)
		image = shiftImageHelper2(tile_row, dx, 1)
	if not dy == 0:
		tile_col = np.array_split(image, num_cores, axis=1)
		image = shiftImageHelper2(tile_col, dy, 0)
	return image

def shiftImageParallel(image, dx, dy):
	if not dx == 0:
		tile_row = np.array_split(image, num_cores, axis=0)
		image = shiftImageHelper(tile_row, dx, 1)
	if not dy == 0:
		tile_col = np.array_split(image, num_cores, axis=1)
		image = shiftImageHelper(tile_col, dy, 0)
	return image


num_cores = mp.cpu_count()

def main():
	image = []
	for i in range(1): 
		image.append(np.matrix(np.random.randint(0,255, size=(2000, 2000))))
	dx, dy = 13, -7

	t0 = time.time()
	for i in range(1):  
		A = shiftImage(image[i], dx, dy) 
	print('--------------')
	print('time1:', (time.time()-t0)*1000)

	

	t0 = time.time()
	for i in range(1):   
		C = shiftImageParallel(image[i], dx, dy)
	print('--------------')
	print('time2:', (time.time()-t0)*1000)

	t0 = time.time()
	for i in range(1):   
		B = shiftImageParallel2(image[i], dx, dy)
	print('--------------')
	print('time3:', (time.time()-t0)*1000)

	# print(image[0])
	# print('--------------')
	# print(A)
	# print('--------------')
	# print(B)

	print("A == B:", np.isclose(A, B).all())
	print("A == C:", np.isclose(A, C).all())

if __name__ == '__main__':
	# freeze_support()
	main()