import time

import cv2
import numpy as np
from scipy import signal
import multiprocessing as mp


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
    print('worker')
    queue.put(signal.convolve(image, kernel, mode='same'))

def blur_par(image, kernel):
    tiles = np.array_split(image, num_cores, axis=0)
    queues = [mp.Queue() for i in range(len(tiles))]
    jobs = [mp.Process(target=blur_worker, args=[queues[i], tiles[i], kernel]) for i in range(len(tiles))]
    for job in jobs: job.start()
    print('all started')
    ret = [queue.get() for queue in queues]
    for job in jobs: job.join()
    print('all join')
    image = np.vstack(ret)
    return image

num_cores = mp.cpu_count()

def main():
    image = []
    for i in range(1):
        image.append(np.matrix(np.random.randint(0, 10, size=(6, 6))))

    kernel = getFilter(1.8, 0.5)

    t0 = time.time()
    A = blur(image[0], kernel)
    print('time1:', (time.time() - t0) * 1000)
    print(A)
    t0 = time.time()
    B = blur_par(image[0], kernel)
    print('time2:', (time.time() - t0) * 1000)
    print(B)
    print("A == B:", np.isclose(A, B).all())


if __name__ == '__main__':
    main()
