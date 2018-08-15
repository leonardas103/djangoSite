import math
import multiprocessing as mp
import os
import time
import numpy as np
from joblib import Parallel, delayed
import tiling

timing = []

def shift_seq(image, dx, dy):
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


def shift_worker(queue, image, dx, dy):
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

def shift_process(imageTiles, dx, dy):
	queues = [mp.Queue() for i in range(num_cores)]
	jobs = [mp.Process(target=shift_worker, args=[queues[i], imageTiles[i], dx, dy]) for i in range(num_cores)]
	
	for job in jobs: job.start()
	ret = [queue.get() for queue in queues]
	for job in jobs: job.join()
	
	return ret

def shiftParallel_row(image, dx, dy):
	overlap = max(abs(dx),abs(dy))
	tiles = tiling.split_square(image, overlap, num_cores)
	shifted = shift_process(tiles, dx, dy)
	ret = tiling.merge_square(image, shifted, overlap, num_cores)
	return ret

def shiftParallel_sq(image, dx, dy):
	overlap = max(abs(dx),abs(dy))
	tiles = tiling.split_square(image, overlap, num_cores)
	shifted = shift_process(tiles, dx, dy)
	ret = tiling.merge_square(image, shifted, overlap, num_cores)
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


def time_function(func, images, dx, dy):
	results = []
	num_tests = 2
	for img in images:
		times = []
		for _ in range(num_tests):
			t0 = time.time() 
			tmp = eval(func)(img, dx, dy)
			times.append(time.time()-t0)
		average = np.mean(times)*1000
		results.append(tmp)
		timing.append(func+'['+str(len(img))+']:' +str(average) )
	timing.append('--------------')
	return results

# num_cores = mp.cpu_count()
num_cores = 4

def main():
	images = []
	images.append(np.matrix(np.random.randint(0,255, size=(1024, 1024))))
	images.append(np.matrix(np.random.randint(0,255, size=(2048, 2048))))
	images.append(np.matrix(np.random.randint(0,255, size=(4096, 4096))))

	dx, dy = 123, 123
	A = time_function('shift_seq', images, dx, dy)
	B = time_function('shiftParallel_sq', images, dx, dy)
	C = time_function('shiftParallel_row', images, dx, dy)
	D = time_function('two_step_shift', images, dx, dy)
	

	for i in timing:
		print(i)
	# for i,_ in enumerate(A):
	# 	print(len(A[i]),": A == B:", np.isclose(A[i], B[i]).all())
	# 	print(len(A[i]),": A == C:", np.isclose(A[i], C[i]).all())
	# 	print(len(A[i]),": A == D:", np.isclose(A[i], D[i]).all())



if __name__ == '__main__':
	# freeze_support()
	main()