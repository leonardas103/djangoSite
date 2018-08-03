import math
import multiprocessing as mp
import os
import time
import numpy as np


def info(title):
	print('axis: %s pid: %s'% (title,os.getpid()) )

def shiftImage(image, dx, dy):
	shift = np.roll(image, dx, axis=1)
	shift = np.roll(shift, dy, axis=0)
	return shift

def shiftImageWorker(args):
	# info(axis)
	image, shift, axis = args
	return np.roll(image, shift, axis=axis)

def shiftImageHelper(imageTiles, shift, axis):
	# print([res.get(timeout=1) for res in results])
	args = zip(imageTiles, [shift]*num_cores, [axis]*num_cores)
	with mp.Pool(processes=num_cores) as p:
		result = p.map(shiftImageWorker, args)
	if axis == 1:
		return np.vstack(result)
	return np.hstack(result)

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
	num_images = 1
	dx, dy = 13, -7

	for i in range(num_images): 
		image.append(np.matrix(np.random.randint(0,255, size=(10000, 10000))))

	t0 = time.time()
	for i in range(num_images):  
		A = shiftImage(image[i], dx, dy) 
	print('time1:', (time.time()-t0)*1000)

	t0 = time.time()
	for i in range(num_images):   
		B = shiftImageParallel(image[i], dx, dy)
	print('time2:', (time.time()-t0)*1000)
	print('dx, dy:',dx,dy)

	# print(image[0])
	# print('--------------')
	# print(A)
	# print('--------------')
	# print(B)

	print("A == B:", np.isclose(A, B).all())

if __name__ == '__main__':
	# freeze_support()
	main()