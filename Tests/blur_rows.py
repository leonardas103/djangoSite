import time
import cv2
import numpy as np
import multiprocessing as mp
from scipy import signal

timing = []

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

def split(image, kernel):
    tiles = []
    step = len(image)//num_cores
    overlap = len(kernel)//2
    for i, row in enumerate(range(0, len(image), step)):
        if(row+step >= len(image)): #last row
            last_tile = image[row:len(image),]
            if len(last_tile) > overlap:
                tiles.append(last_tile)
        else:
            tiles.append(image[row:row+step+2*overlap,])
    return tiles

def blur_worker_split(queue, image, kernel, idx):
    step = len(image) // num_cores
    overlap = len(kernel) // 2
    if (idx + step >= len(image)):  # last row
        last_tile = image[idx:len(image), ]
        if len(last_tile) > overlap:
            tile = last_tile
    else:
        tile = image[idx:idx + step + 2 * overlap, ]

    queue.put(signal.convolve(tile, kernel, mode='same'))

def blur_and_split(image, kernel):
    step = len(image) // num_cores
    overlap = len(kernel) // 2
    row_idx = range(0, len(image), step)
    queues = [mp.Queue() for i in range(len(row_idx))]
    jobs = [mp.Process(target=blur_worker_split, args=[queues[i], image, kernel, row_idx[i]]) for i in range(len(row_idx))]
    for job in jobs: job.start()
    ret = [queue.get() for queue in queues]
    for job in jobs: job.join()
    for i, row in enumerate(row_idx):
        if (i == 0):
            ret[i] = ret[i][0:step + overlap, ]
        else:
            ret[i] = ret[i][overlap:step + overlap, ]
    return np.vstack(ret)

def blur_from_split(image, tiles, kernel):
    step = len(image) // num_cores
    overlap = len(kernel) // 2
    row_idx = range(0, len(image), step)
    queues = [mp.Queue() for i in range(len(tiles))]
    jobs = [mp.Process(target=blur_worker, args=[queues[i], tiles[i], kernel]) for i in range(len(tiles))]
    for job in jobs: job.start()
    ret = [queue.get() for queue in queues]
    for job in jobs: job.join()
    for i, _ in enumerate(row_idx):
        if (i == 0):
            ret[i] = ret[i][0:step + overlap, ]
        else:
            ret[i] = ret[i][overlap:step + overlap, ]
    return np.vstack(ret)

num_cores = mp.cpu_count()
def main():
    kernel = getFilter(1.8, 0.5)
    images, A,B,C = [],[],[],[]
    images.append(np.matrix(np.random.randint(0,255, size=(1000, 1000))))
    images.append(np.matrix(np.random.randint(0,255, size=(2000, 2000))))
    images.append(np.matrix(np.random.randint(0,255, size=(4000, 4000))))
    images.append(np.matrix(np.random.randint(0,255, size=(6000, 6000))))

    for img in images:
        t0 = time.time()  
        A.append(signal.convolve(img, kernel, mode='same'))
        timing.append('seq['+str(len(img))+']:' +str((time.time()-t0)*1000))
    timing.append('--------------')

    for img in images:
        t0 = time.time()  
        B.append(blur_from_split(img, split(img, kernel), kernel))
        timing.append('B_par['+str(len(img))+']:' +str((time.time()-t0)*1000))
    timing.append('--------------')

    for img in images:
        t0 = time.time()  
        C.append(blur_and_split(img, kernel))
        timing.append('C_par['+str(len(img))+']:' +str((time.time()-t0)*1000))
    timing.append('--------------')

    for i in timing:
        print(i)
    # for i,_ in enumerate(A):
    #     print(len(A[i]),": A == B:", np.isclose(A[i], B[i]).all())
    #     print(len(A[i]),": A == C:", np.isclose(A[i], C[i]).all())

if __name__ == '__main__':
    main()