import math as m
import cv2
from PIL import Image
import numpy as np

def normalize(image):
    mn = image.min()
    mx = image.max()
    if (mn == mx):
        if (mn == 0):
            return image
        else:
            return image/mn
    else:
        image -= mn
        return image/(mx-mn)

def rescaleImage(image, mn, mx):
    image = normalize(image)*(mx-mn)
    image += mn
    return image

def sigma2sz(sigma):
    return m.ceil(sigma*3)*2 + 1; 

def convolve(image, sigma ):
    sz = sigma2sz(sigma)
    kernel = cv2.getGaussianKernel(sz, sigma)
    return cv2.sepFilter2D(image, -1, kernel, kernel, borderType=0)

def main(image, sigma):
    subject = 255 - np.asarray(Image.open(image).convert('RGB'), dtype=np.float64)[:,:,1]
    subject = subject/255

    result = rescaleImage(convolve(subject, sigma), 0, 255)
    img = Image.fromarray(result.astype(np.uint8))
    #return img to site

# if __name__ == "__main__":
#     main()
