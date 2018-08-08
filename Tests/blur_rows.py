import time

import cv2
import numpy as np
import multiprocessing as mp
from scipy import signal

def sigma2sz(sigma):
    return int(np.ceil(sigma*3))*2 + 1

def getFilter(sigma, sigmaRatio):
    sz = sigma2sz(sigma)
    kernel1 = np.outer(cv2.getGaussianKernel(sz, sigma), cv2.getGaussianKernel(sz, sigma))
    kernel2 = np.outer(cv2.getGaussianKernel(sz, sigma * sigmaRatio), cv2.getGaussianKernel(sz, sigma * sigmaRatio))
    return kernel2 - kernel1

def blur_worker(queue, image, kernel):
    queue.put(signal.convolve(image, kernel, mode='same'))


def blur_par(image, kernel, sections):
    tiles, jobs = [], []
    step = len(image)//sections
    overlap = len(kernel)//2
    row_idx = range(0, len(image), step)
    queues = [mp.Queue() for i in range(len(row_idx))]

    for i, row in enumerate(row_idx):

        if(row+step >= len(image)): #last row
            last_tile = image[row:len(image),]
            if len(last_tile) > overlap:
                jobs.append(mp.Process(target=blur_worker, args=[queues[i], last_tile, kernel]))
                jobs[i].start()

        else:
            jobs.append(mp.Process(target=blur_worker, args=[queues[i], image[row:row+step+2*overlap,], kernel]))
            jobs[i].start()

    tiles = [queue.get() for queue in queues]
    for i, row in enumerate(row_idx):
        if (i == 0):
            tiles[i] = tiles[i][0:step + overlap, ]
        else:
            tiles[i] = tiles[i][overlap:step + overlap, ]

    return np.vstack(tiles)

def blue_split_seq(image, kernel, sections):
    tiles = []
    step = len(image)//sections
    overlap = len(kernel)//2
    for i, row in enumerate(range(0, len(image), step)):
        if(row+step >= len(image)): #last row
            last_tile = image[row:len(image),]
            if len(last_tile) > overlap:
                tiles.append(signal.convolve(last_tile, kernel, mode='same'))
                tiles[i] = tiles[i][overlap:step + overlap, ]

        else:    
            tiles.append(signal.convolve(image[row:row+step+2*overlap,], kernel, mode='same'))
            if(i==0):
                tiles[i] = tiles[i][0:step + overlap, ]
            else:
                tiles[i] = tiles[i][overlap:step + overlap, ]
    return np.vstack(tiles)

num_cores = mp.cpu_count()
def main():
    kernel = getFilter(1.8, 0.5)
    image = np.matrix(np.random.randint(0, 255, size=(8000, 8000)))

    t0 = time.time()
    A = signal.convolve(image, kernel, mode='same')
    print('time1:', (time.time() - t0) * 1000)
    t0 = time.time()
    B = blur_par(image, kernel, 2)
    print('time2:', (time.time() - t0) * 1000)
    print("A == B:", np.isclose(A, B).all())


if __name__ == '__main__':
    main()