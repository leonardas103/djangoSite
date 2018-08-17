import time
import cv2
import numpy as np
from scipy import signal
import multiprocessing as mp
import tiling

timing = []

def sigma2sz(sigma):
	return int(np.ceil(sigma*3))*2 + 1

def blur_seq(image, kernel, split_type):
	return signal.convolve(image, kernel, mode='same')

def getFilter(sigma, sigmaRatio):
	sz = sigma2sz(sigma)
	kernel1 = np.outer(cv2.getGaussianKernel(sz, sigma), cv2.getGaussianKernel(sz, sigma))
	kernel2 = np.outer(cv2.getGaussianKernel(sz, sigma * sigmaRatio), cv2.getGaussianKernel(sz, sigma * sigmaRatio))
	return kernel2 - kernel1


def blur_worker(queue, image, kernel):
	queue.put(signal.convolve(image, kernel, mode='same'))


def blur_par(image, kernel, split_type):
	overlap = len(kernel)//2
	if overlap>len(image)//num_cores:
		import sys 
		sys.exit('[Warning] select a smaller kernel or large image')
	tiles = getattr(tiling, 'split_'+split_type)(image, overlap, num_cores) #tiles = tiling.split_sq(image, overlap, num_cores)
	queues = [mp.Queue() for i in range(len(tiles))]
	jobs = [mp.Process(target=blur_worker, args=[queues[i], tiles[i], kernel]) for i in range(len(tiles))]
	for job in jobs: job.start()
	ret = [queue.get() for queue in queues]
	for job in jobs: job.join()
	image = getattr(tiling, 'merge_'+split_type)(image, ret, overlap, num_cores)
	return image


def time_function(func, images, kernel, split_type):
	results = []
	num_tests = 10
	for img in images:
		times = []
		for _ in range(num_tests):
			t0 = time.time() 
			tmp = eval(func)(img, kernel, split_type)
			times.append(time.time()-t0)
		average = np.mean(times)*1000
		results.append(tmp)
		timing.append(func+'_'+split_type+'['+str(len(img))+']:' +str(average) )
	timing.append('--------------')
	return results

num_cores = mp.cpu_count()
# num_cores = 4

def main():
	kernel = getFilter(1.8, 0.5)
	images, A,B,C = [],[],[],[]
	images.append(np.matrix(np.random.randint(0,255, size=(512, 512))))
	images.append(np.matrix(np.random.randint(0,255, size=(1024, 1024))))
	images.append(np.matrix(np.random.randint(0,255, size=(2048, 2048))))
	images.append(np.matrix(np.random.randint(0,255, size=(4096, 4096))))

	A = time_function('blur_seq', images, kernel, '')
	B = time_function('blur_par', images, kernel, 'row')
	C = time_function('blur_par', images, kernel, 'square')

	for i in timing:
		print(i)
	# for i,_ in enumerate(A):
	# 	print(len(A[i]),": A == B:", np.isclose(A[i], B[i]).all() )
	# 	print(len(A[i]),": A == C:", np.isclose(A[i], C[i]).all() )

if __name__ == '__main__':
	main()
