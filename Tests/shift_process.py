import math
import multiprocessing as mp
import os
import time
import numpy as np

timing = []

def info(title):
	print('axis: %s pid: %s'% (title,os.getpid()) )

def shiftImage(image, dx, dy):
	shift = np.roll(image, dx, axis=1)
	shift = np.roll(shift, dy, axis=0)
	return shift

def shiftImageWorker(queue, image, shift, axis):
	result = np.roll(image, shift, axis=axis)
	queue.put(result)

def shiftImageHelper(imageTiles, shift, axis):
	queues = [mp.Queue() for i in range(num_cores)]
	jobs = [mp.Process(target=shiftImageWorker, args=[queues[i], imageTiles[i], shift, axis]) for i in range(num_cores)]
	
	for job in jobs: job.start()
	ret = [queue.get() for queue in queues]
	for job in jobs: job.join()
	
	if axis == 1:
		return np.vstack(ret)
	return np.hstack(ret)

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
	image, A,B = [],[],[]
	image.append(np.matrix(np.random.randint(0,255, size=(1000, 1000))))
	image.append(np.matrix(np.random.randint(0,255, size=(2000, 2000))))
	image.append(np.matrix(np.random.randint(0,255, size=(4000, 4000))))
	dx, dy = 20, -20

	
	for img in image:
		t0 = time.time()  
		A.append(shiftImage(img, dx, dy))
		timing.append('seq['+str(len(img))+']:' +str((time.time()-t0)*1000))
	timing.append('--------------')
	
	for img in image:
		t0 = time.time()  
		B.append(shiftImageParallel(img, dx, dy))
		timing.append('par['+str(len(img))+']:' +str((time.time()-t0)*1000))
	timing.append('--------------')

	for i in timing:
		print(i)
	for i,_ in enumerate(A):
		print(len(A[i]),": A == B:", np.isclose(A[i], B[i]).all())

if __name__ == '__main__':
	# freeze_support()
	main()