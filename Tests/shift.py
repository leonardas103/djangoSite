import math
import multiprocessing as mp
import os
import time
import numpy as np
from joblib import Parallel, delayed
import tiling

timing = []

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


def shiftImageWorker(queue, image, dx, dy):
	shift = np.roll(image, dx, axis=1)
	shift = np.roll(shift, dy, axis=0)

	if dx > 0:
		shift[:,0:dx] = 0
	elif dx < 0:
		shift[:,dx:] = 0

	if dy > 0:
		shift[0:dy,:] = 0
	elif dy < 0:
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
	tiles = tiling.split_easy_sq(image, overlap, num_cores)
	shifted = shiftImageHelper(tiles, dx, dy)
	ret = tiling.merge_easy_sq(image, shifted, overlap, num_cores)
	return ret

def two_step_shift_worker(queue, image, shift, axis):
	queue.put(np.roll(image, shift, axis=axis))

def two_step_shift_helper(imageTiles, shift, axis):
	queues = [mp.Queue() for i in range(num_cores)]
	jobs = [mp.Process(target=two_step_shift_worker, args=[queues[i], imageTiles[i], shift, axis]) for i in range(num_cores)]
	
	for job in jobs: job.start()
	ret = [queue.get() for queue in queues]
	for job in jobs: job.join()
	
	return ret

def two_step_shift(image, dx, dy):
	tile_row = np.array_split(image, num_cores, axis=0)
	tile_row = two_step_shift_helper(tile_row, dx, 1)
	image = np.vstack(tile_row)

	tile_col = np.array_split(image, num_cores, axis=1)
	tile_col = two_step_shift_helper(tile_col, dy, 0)
	image = np.hstack(tile_col)

	if dx > 0:
		image[:,0:dx] = 0
	elif dx < 0:
		image[:,dx:] = 0

	if dy > 0:
		image[0:dy,:] = 0
	elif dy < 0:
		image[dy:,:] = 0

	return image

# num_cores = mp.cpu_count()
num_cores = 4

def main():
	images,A,B,C = [],[],[],[]
	images.append(np.matrix(np.random.randint(0,255, size=(1000, 1000))))
	# images.append(np.matrix(np.random.randint(0,255, size=(2000, 2000))))
	# images.append(np.matrix(np.random.randint(0,255, size=(3000, 3000))))

	dx, dy = -7, 1

	for img in images:
		t0 = time.time()
		A.append(shiftImage(img, dx, dy))
		timing.append('seq['+str(len(img))+']:' +str((time.time()-t0)*1000))
	timing.append('--------------')

	for img in images:
		t0 = time.time()
		B.append(shiftImageParallel(img, dx, dy))
		timing.append('B_par['+str(len(img))+']:' +str((time.time()-t0)*1000))
	timing.append('--------------')

	for img in images:
		t0 = time.time()
		C.append(two_step_shift(img, dx, dy))
		timing.append('C_2step['+str(len(img))+']:' +str((time.time()-t0)*1000))
	timing.append('--------------')

	for i in timing:
		print(i)
	for i,_ in enumerate(A):
		print(len(A[i]),": A == B:", np.isclose(A[i], B[i]).all())
		print(len(A[i]),": A == C:", np.isclose(A[i], C[i]).all())



if __name__ == '__main__':
	# freeze_support()
	main()