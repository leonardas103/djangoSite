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
	image = np.vstack(return_value)
	return image

def overhead_worker_pool(args):
	image, dummy_var = args
	return image


def overhead_pool(image):
	image_tiles = np.array_split(image, num_cores, axis=0)
	dummy_var = 0
	args = zip(image_tiles, [dummy_var]*num_cores,)
	with mp.Pool(processes=num_cores) as p:
		image = p.map(overhead_worker_pool, args)
		# image = p.map_async(overhead_worker_pool, args).get()
	return np.vstack(image)

def overhead_worker_process(queue, image):
	queue.put(image)

def overhead_process(image):
	image_tiles = np.array_split(image, num_cores, axis=0)
	queues = [mp.SimpleQueue() for i in range(num_cores)]
	jobs = [mp.Process(target=overhead_worker_process, args=[queues[i], image_tiles[i]]) for i in range(num_cores)]
	
	for job in jobs: job.start()
	return_value = [queue.get() for queue in queues]
	for job in jobs: job.join()
	
	image = np.vstack(return_value)
	return image


def overhead_worker_process_pipe(pipe, image):
	pipe.send(image)
	pipe.close()

def overhead_process_pipe(image):
	image_tiles = np.array_split(image, num_cores, axis=0)
	pipes = [mp.Pipe(duplex=False) for _ in range(num_cores)]
	jobs = [mp.Process(target=overhead_worker_process_pipe, args=[pipes[i][1], image_tiles[i]]) for i in range(num_cores)]
	
	for job in jobs: job.start()
	pipes_out = [pipe[0].recv() for pipe in pipes]
	for job in jobs: job.join()
	
	image = np.vstack(pipes_out)
	return image

def control(image):
	image_tiles = np.array_split(image, num_cores, axis=0)
	s = np.vstack(image_tiles)
	return s

def time_function(func, images):
	results = []
	num_tests = 10
	for img in images:
		times = []
		for _ in range(num_tests):
			t0 = time.time() 
			tmp = eval(func)(img)
			times.append(time.time()-t0)
		average = np.mean(times)*1000
		results.append(tmp)
		timing.append(func+'['+str(len(img))+']:' +str(average) )
	timing.append('--------------')
	return results


num_cores = mp.cpu_count()

def main():
	images = []
	images.append(np.matrix(np.random.randint(0,255, size=(1000, 1001))))
	images.append(np.matrix(np.random.randint(0,255, size=(2000, 2000))))
	images.append(np.matrix(np.random.randint(0,255, size=(4000, 4000))))

	A = time_function('control', images)
	B = time_function('overhead_process_pipe', images)
	C = time_function('overhead_process', images)
	D = time_function('overhead_joblib', images)
	E = time_function('overhead_pool', images)
	

	for i in timing:
		print(i)
	# for i,_ in enumerate(A):
	# 	print(len(A[i]),": A == B:", np.isclose(A[i], B[i]).all())
	# 	print(len(A[i]),": A == C:", np.isclose(A[i], C[i]).all())
		# print(len(A[i]),": A == D:", np.isclose(A[i], D[i]).all())
		# print(len(A[i]),": A == E:", np.isclose(A[i], E[i]).all())

if __name__ == '__main__':
	# freeze_support()
	main()