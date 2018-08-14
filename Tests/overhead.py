import numpy as np
from joblib import Parallel, delayed
import multiprocessing as mp
import time

timing = []


def overhead_worker_joblib(image):
	return image

def overhead_joblib(image):
	image_tiles = np.array_split(image, num_cores, axis=0)
	return_value = Parallel(n_jobs=num_cores)(delayed(overhead_worker_joblib)(image_tiles[i],) for i in range(num_cores))
	image = np.hstack(return_value)
	return image


def overhead_worker_pool(args):
	image, dummy_var = args
	return image


def overhead_pool(image):
	dummy_var = 0
	image_tiles = np.array_split(image, num_cores, axis=0)
	args = zip(image_tiles, [dummy_var]*num_cores)
	with mp.Pool(processes=num_cores) as p:
		image = p.map(overhead_worker_pool, args)
	image = np.hstack(image)
	return image

def overhead_worker_process(queue, image):
	queue.put(image)

def overhead_process(image):
	image_tiles = np.array_split(image, num_cores, axis=0)
	queues = [mp.Queue() for i in range(num_cores)]
	jobs = [mp.Process(target=overhead_worker_process, args=[queues[i], image_tiles[i]]) for i in range(num_cores)]
	
	for job in jobs: job.start()
	return_value = [queue.get() for queue in queues]
	for job in jobs: job.join()
	
	image = np.hstack(return_value)
	return image

def merge(image, tiles, sections):
	height, _ = np.shape(image)
	result = np.empty_like(image)
	for row,tile in enumerate(tiles):
		result[row:len(tile),] = tile
	return result

def control(image):
	image_tiles = np.array_split(image, num_cores, axis=0)
	m = merge(image, image_tiles, num_cores)
	s = np.hstack(image_tiles)
	print(":stack == merge:", np.isclose(m, s).all())
	return s

num_cores = mp.cpu_count()

def main():
	image, A,B,C,D,E = [],[],[],[],[],[]
	image.append(np.matrix(np.random.randint(0,255, size=(1000, 1000))))
	image.append(np.matrix(np.random.randint(0,255, size=(2000, 2000))))
	image.append(np.matrix(np.random.randint(0,255, size=(4000, 4000))))

	for img in image:
		t0 = time.time()  
		A.append(control(img))
		timing.append('control['+str(len(img))+']:' +str((time.time()-t0)*1000))
	timing.append('--------------')

	for img in image:
		t0 = time.time()  
		B.append(overhead_process(img))
		timing.append('process['+str(len(img))+']:' +str((time.time()-t0)*1000))
	timing.append('--------------')

	for img in image:
		t0 = time.time()  
		C.append(overhead_pool(img))
		timing.append('pool['+str(len(img))+']:' +str((time.time()-t0)*1000))
	timing.append('--------------')

	for img in image:
		t0 = time.time()  
		D.append(overhead_joblib(img))
		timing.append('joblib['+str(len(img))+']:' +str((time.time()-t0)*1000))
	timing.append('--------------')

	# for img in image:
	# 	t0 = time.time()  
	# 	A.append(overhead_process_pipe(img))
	# 	timing.append('seq['+str(len(img))+']:' +str((time.time()-t0)*1000))
	# timing.append('--------------')

	for i in timing:
		print(i)
	for i,_ in enumerate(A):
		print(len(A[i]),": A == B:", np.isclose(A[i], B[i]).all())
		print(len(A[i]),": A == C:", np.isclose(A[i], C[i]).all())
		print(len(A[i]),": A == D:", np.isclose(A[i], D[i]).all())
		# print(len(A[i]),": A == E:", np.isclose(A[i], E[i]).all())

if __name__ == '__main__':
	# freeze_support()
	main()