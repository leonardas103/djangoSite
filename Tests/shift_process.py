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

def shiftImageWorker(queue, image, shift, axis, id):
	# info(axis)
	result = np.roll(image, shift, axis=axis)
	queue.put((result,id))
	# print('placed in queue')

def shiftImageHelper(imageTiles, shift, axis):
	jobs, rets = [], []
	# ctx = mp.get_context('spawn')
	queue = mp.Queue()
	# queue = ctx.Queue()

	for i in range(num_cores):
		p = mp.Process(target=shiftImageWorker, args=(queue, imageTiles[i], shift, axis, i))
		jobs.append(p)
		p.start()
	# print('Threads started')
	for p in jobs:
		result, id = queue.get()
		rets.insert(id, result)
	for p in jobs:
		p.join() #thread stuck waiting?
		# print('thread joined main')
	# print('All Threads finished')
	if axis == 1:
		return np.vstack(rets)
	return np.hstack(rets)

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
	# dx = int(round(2*np.cos(math.pi/8)))
	# dy = int(round(-2*np.sin(math.pi/8)))
	dx, dy = 20, -20

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

	# print(image[0])
	# print('--------------')
	# print(A)
	# print('--------------')
	# print(B)

	print("A == B:", np.isclose(A, B).all())

if __name__ == '__main__':
	# freeze_support()
	main()