import numpy as np
from joblib import Parallel, delayed
import multiprocessing as mp
import time

timing = []


def worker_joblib(image):
	return image

def joblib(image):
	image_tiles = np.array_split(image, num_cores, axis=0)
	return_value = Parallel(n_jobs=num_cores)(delayed(worker_joblib)(image_tiles[i],) for i in range(num_cores))
	image = np.vstack(return_value)
	return image

def worker_pool(args):
	image, dummy_var = args
	return image


def pool(image):
	image_tiles = np.array_split(image, num_cores, axis=0)
	dummy_var = 0
	args = zip(image_tiles, [dummy_var]*num_cores,)
	with mp.Pool(processes=num_cores) as p:
		image = p.map(worker_pool, args)
		# image = p.map_async(worker_pool, args).get()
	return np.vstack(image)

def worker_process(queue, image):
	queue.put(image)

def process(image):
	image_tiles = np.array_split(image, num_cores, axis=0)
	queues = [mp.SimpleQueue() for i in range(num_cores)]
	jobs = [mp.Process(target=worker_process, args=[queues[i], image_tiles[i]]) for i in range(num_cores)]
	
	for job in jobs: job.start()
	return_value = [queue.get() for queue in queues]
	for job in jobs: job.join()
	
	image = np.vstack(return_value)
	return image


def worker_process_pipe(pipe, image):
	pipe.send(image)
	pipe.close()

def process_pipe(image):
	image_tiles = np.array_split(image, num_cores, axis=0)
	pipes = [mp.Pipe(duplex=False) for _ in range(num_cores)]
	jobs = [mp.Process(target=worker_process_pipe, args=[pipes[i][1], image_tiles[i]]) for i in range(num_cores)]
	
	for job in jobs: job.start()
	pipes_out = [pipe[0].recv() for pipe in pipes]
	for job in jobs: job.join()
	
	image = np.vstack(pipes_out)
	return image

def worker_process_manager(image, shared_memory, idx):
	shared_memory.append(image)

def process_manager(image):
	image_tiles = np.array_split(image, num_cores, axis=0)
	manager = mp.Manager()
	shared_memory = manager.list()
	jobs = [mp.Process(target=worker_process_manager, args=[image_tiles[i], shared_memory, i]) for i in range(num_cores)]
	
	for job in jobs: job.start()
	for job in jobs: job.join()

	return np.vstack(shared_memory[:])

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
	images.append(np.matrix(np.random.randint(0,255, size=(1024, 1024))))
	images.append(np.matrix(np.random.randint(0,255, size=(2048, 2048))))
	images.append(np.matrix(np.random.randint(0,255, size=(4096, 4096))))

	A = time_function('control', images)
	B = time_function('process_pipe', images)
	C = time_function('process', images)
	D = time_function('joblib', images)
	E = time_function('pool', images)
	F = time_function('process_manager', images)
	

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