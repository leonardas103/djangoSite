import time

import cv2
import numpy as np
from scipy import signal
import multiprocessing as mp

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


def split(image, kernel):
    height, width = np.shape(image)
    tiles = []
    step = int(np.ceil(width/(num_cores//2)))
    overlap = len(kernel)//2
    tile_num = 0
    for i, row in enumerate([0, height//2]): 
        for j, col in enumerate(range(0, width, step)):
            if(col+step >= width): #last col
                last_tile = image[row:row+height//2+2*overlap:,col:width]
                if(row == height//2):
                    last_tile = image[row:height:,col:width]
                if len(last_tile) > overlap:
                    tiles.append(last_tile)
                    tile_num += 1 
            else:
                tiles.append(image[row:row+height//2+2*overlap:,col:col+step+2*overlap])
                tile_num += 1 
            # print('step:%s overlap:%s i:%s col:%s #cols:%s' % (step, overlap, i ,col, range(0, len(image), step)))
            # print(tiles[tile_num-1])
    return tiles

def merge_old(image, kernel, tiles):
    height, width = np.shape(image)
    step = int(np.ceil(width/(num_cores//2)))
    overlap = len(kernel)//2
    result_0, result_1, result = [],[],[]
    tile_num = 0
    for i, row in enumerate([0, height//2]): 
        for j, col in enumerate(range(0, width, step)):
            if (i == 0):
                if(j==0):
                    result_0.append(tiles[tile_num][0:height//2 + overlap, 0:step+overlap])
                else:
                    result_0.append(tiles[tile_num][0:height//2 + overlap, overlap:step+overlap])
            else:
                if(j==0):
                    result_1.append(tiles[tile_num][overlap:height//2 + overlap, 0:step+overlap])
                else:        
                    result_1.append(tiles[tile_num][overlap:height//2 + overlap, overlap:step+overlap])
            tile_num += 1
        if i == 0:
            result.append(np.hstack(result_0))
        else:
            result.append(np.hstack(result_1))
            
    return np.vstack(result)

def blur_par(image, kernel):
    t0 = time.time()
    tiles = split(image, kernel)
    # timing.append(("\tsplitting image", (time.time()-t0)*1000))
    queues = [mp.Queue() for i in range(len(tiles))]
    jobs = [mp.Process(target=blur_worker, args=[queues[i], tiles[i], kernel]) for i in range(len(tiles))]
    for job in jobs: job.start()
    t0 = time.time()
    ret = [queue.get() for queue in queues]
    # timing.append(("\tthreads done:", (time.time()-t0)*1000))
    for job in jobs: job.join()
    t0 = time.time()
    image = merge(image, kernel, ret)
    # timing.append(("\tmerging", (time.time()-t0)*1000))
    return image

def merge(image, kernel, tiles):
    height, width = np.shape(image)
    result = np.empty_like(image, dtype=float)
    step = int(np.ceil(width/(num_cores//2)))
    overlap = len(kernel)//2
    tile_num = 0
    for i, _ in enumerate([0, height//2]): 
        for j, col in enumerate(range(0, width, step)):
            if (i == 0):
                if(j==0):
                    result[0:overlap+height//2, 0:step+overlap] = tiles[tile_num][0:height//2 + overlap, 0:step+overlap]
                else:
                    result[0:overlap+height//2, col+overlap:col+step+overlap] = tiles[tile_num][0:height//2 + overlap, overlap:step+overlap]
            else:
                if(j==0):
                    result[overlap+height//2:height, col:col+step+overlap] = tiles[tile_num][overlap:height//2 + overlap, 0:step+overlap]
                else:        
                    result[overlap+height//2:height, col+overlap:col+step+overlap] = tiles[tile_num][overlap:height//2 + overlap, overlap:step+overlap]
            tile_num += 1
    return result


num_cores = mp.cpu_count()
# num_cores = 4

def main():
    kernel = getFilter(1.8, 0.5)
    # kernel = np.outer([1,2,3,4,5],[1,2,3,4,5])
    images, A,B = [],[],[]
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
        B.append(blur_par(img, kernel))
        timing.append('B_par['+str(len(img))+']:' +str((time.time()-t0)*1000))
    timing.append('--------------')

    for i in timing:
        print(i)
    # for i,_ in enumerate(A):
    #     print(len(A[i]),": A == B:", np.isclose(A[i], B[i]).all())

if __name__ == '__main__':
    main()
