import numpy as np
from scipy import signal


def conv_split(image, kernel, num_cores):
    q = []
    tiles = np.array_split(image, num_cores, axis=0)
    for i in range(len(tiles)):
        q.append(signal.convolve(tiles[i], kernel, mode='same'))
    return np.vstack(q)

def split(image, kernel, sections):
    tiles = []
    step = len(image)//sections
    overlap = len(kernel)//2
    print('image:%s kernel:%s step:%s  overlap:%s' % (len(image), len(kernel), step,overlap))
    for i, row in enumerate(range(0, len(image), step)):
        print('i=',i, ' row=',row)
        print('tile:')
        print(image[row:row+step+2*overlap,])
        if(row+step > len(image)):
            tiles.append(signal.convolve(image[row:len(image),], kernel, mode='same'))
            print('after:')
            print(tiles[i])
        else:    
            tiles.append(signal.convolve(image[row:row+step+2*overlap,], kernel, mode='same'))
            tmp = tiles[i]
            if(i==0):
                tmp = tmp[0:step+overlap,]
            else:
                tmp = tmp[1:step+overlap,]
            tiles[i] = tmp
            print('after:')
            print(tiles[i])
    return np.vstack(tiles)

def main():
    kernel = np.outer([1,2,3], [4,5,6])
    image = np.matrix(np.random.randint(0, 10, size=(10, 10)))
    print('initial:')
    print(image)

    A = signal.convolve(image, kernel, mode='same')
    B = split(image, kernel, 3)
    print(A)
    print('----------')
    print(B)
    print("A == B:", np.isclose(A, B).all())


if __name__ == '__main__':
    main()