import cv2
import scipy.signal as signal
import numpy as np
import time

timing = []

def convolution_2d(image, kernel, var):
    return signal.convolve(image, kernel, mode='same')

def sep_conv_DoG(image, kernel1, kernel2):
    first = cv2.sepFilter2D(image.astype(float), -1, kernel1, kernel1, borderType=0)
    second = cv2.sepFilter2D(image.astype(float), -1, kernel2, kernel2, borderType=0)
    return first-second


def time_function(func, images, kernel1, kernel2):
	results = []
	num_tests = 10
	for img in images:
		times = []
		for _ in range(num_tests):
			t0 = time.time() 
			tmp = eval(func)(img, kernel1, kernel2)
			times.append(time.time()-t0)
		average = np.mean(times)*1000
		results.append(tmp)
		timing.append(func+'['+str(len(img))+']:' +str(average) )
	timing.append('--------------')
	return results

def main():
	images = []
	images.append(np.matrix(np.random.randint(0,255, size=(512, 512))))
	images.append(np.matrix(np.random.randint(0,255, size=(1024, 1024))))
	images.append(np.matrix(np.random.randint(0,255, size=(2048, 2048))))
	kernel1 = cv2.getGaussianKernel(13, 2)
	kernel2 = cv2.getGaussianKernel(13, 1)
	kernel1_2D = np.outer(kernel1, kernel1)
	kernel2_2D = np.outer(kernel2, kernel2)
	kernel_DoG = kernel1_2D - kernel2_2D

	
	A = time_function('convolution_2d', images, kernel_DoG, None)
	B = time_function('sep_conv_DoG', images, kernel1, kernel2)
	
	for i in timing:
		print(i)
	for i,_ in enumerate(A):
		print(len(A[i]),": A == B:", np.isclose(A[i], B[i]).all())

if __name__ == '__main__':
	main()





