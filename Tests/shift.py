import multiprocessing as mp
import numpy as np
import math
import time
import os

def info(title):
	print('axis: ', title)
	print('parent process:', os.getppid())
	print('process id:', os.getpid())

def shiftImage(image, dx, dy):
	shift = np.roll(image, dx, axis=1)
	shift = np.roll(shift, dy, axis=0)
	return shift

def shiftImageWorker(queue, image, shift, axis):
	# info(axis)
	result = np.roll(image, shift, axis=axis)
	queue.put(result)

def shiftImageParallel(image, dx, dy):
	tile_row = np.array_split(image, num_cores, axis=0)
	t0 = time.time()
	jobs, rets = [], []
	queue = mp.Queue()
	for i in range(num_cores):
		p = mp.Process(target=shiftImageWorker, args=(queue, tile_row[i], dx, 1))
		jobs.append(p)
		p.start()
	print('time2 to make threads:', (time.time()-t0)*1000)
	for proc in jobs:
		rets.append(queue.get())
		proc.join()
	
	t0 = time.time()
	image = np.vstack(rets) #order not ganantee
	tile_col = np.array_split(image, num_cores, axis=1)
	print('time2 joinSplit:', (time.time()-t0)*1000)
	jobs, rets = [], []
	queue = mp.Queue()
	for i in range(num_cores):
		p2 = mp.Process(target=shiftImageWorker, args=(queue, tile_col[i], dy, 0))
		jobs.append(p)
		p2.start()

	for proc in jobs:
		rets.append(queue.get())
		proc.join()

	return np.hstack(rets)


num_cores = 4

image = []
for i in range(1): 
	image.append(np.matrix(np.random.randint(0,255, size=(5000, 5000))))
dx = int(round(2*np.cos(math.pi/8)))
dy = int(round(-2*np.sin(math.pi/8)))
# dx, dy = 3,0

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
print('dy, dy:',dy,dx)

# print(image)
# print('--------------')
# print(A)
# print('--------------')
# print(B)

print("A == B:", np.isclose(A, B).all())