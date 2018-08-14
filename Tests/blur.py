import time
import cv2
import numpy as np
from scipy import signal
import multiprocessing as mp
import tiling

timing = []

def sigma2sz(sigma):
	return int(np.ceil(sigma*3))*2 + 1

def blur(image, kernel):
	return signal.convolve(image, kernel, mode='same')

def getFilter(sigma, sigmaRatio):
	sz = sigma2sz(sigma)
	kernel1 = np.outer(cv2.getGaussianKernel(sz, sigma), cv2.getGaussianKernel(sz, sigma))
	kernel2 = np.outer(cv2.getGaussianKernel(sz, sigma * sigmaRatio), cv2.getGaussianKernel(sz, sigma * sigmaRatio))
	return kernel2 - kernel1


def blur_worker(queue, image, kernel):
	queue.put(signal.convolve(image, kernel, mode='same'))


def blur_par(image, kernel):
	t0 = time.time()
	overlap = len(kernel)//2
	if overlap>len(image)//num_cores:
		import sys 
		sys.exit('[Warning] select a smaller kernel or large image')
	tiles = tiling.split_easy_row(image, overlap, num_cores)
	# timing.append(("\tsplitting image", (time.time()-t0)*1000))
	queues = [mp.Queue() for i in range(len(tiles))]
	jobs = [mp.Process(target=blur_worker, args=[queues[i], tiles[i], kernel]) for i in range(len(tiles))]
	for job in jobs: job.start()
	t0 = time.time()
	ret = [queue.get() for queue in queues]
	# timing.append(("\tthreads done:", (time.time()-t0)*1000))
	for job in jobs: job.join()
	t0 = time.time()
	image = tiling.merge_easy_row(image, ret, overlap, num_cores)
	# timing.append(("\tmerging", (time.time()-t0)*1000))
	return image


num_cores = mp.cpu_count()
# num_cores = 4

def main():
	kernel = getFilter(1.8, 0.5)
	images, A,B = [],[],[]
	images.append(np.matrix(np.random.randint(0,255, size=(101, 103))))
	images.append(np.matrix(np.random.randint(0,255, size=(2000, 2000))))

	for img in images:
		t0 = time.time()
		A.append(signal.convolve(img, kernel, mode='same'))
		timing.append('seq['+str(len(img))+']:' +str((time.time()-t0)*1000))
	timing.append('--------------')

	for img in images:
		t0 = time.time()
		B.append(blur_par(img, kernel))
		timing.append('B_par['+str(len(img))+']:' +str((time.time()-t0)*1000))
	timing.append('--------------')

	for i in timing:
		print(i)
	for i,_ in enumerate(A):
		print(len(A[i]),": A == B:", np.isclose(A[i], B[i]).all() )

if __name__ == '__main__':
	main()
