import cosfire as c
import numpy as np
import math as m
import cv2
import time
from PIL import Image
import sys


def main(image, prototype, center, sigma, rhoList, sigma0,  alpha, rotationInvariance):
	proto = np.asarray(prototype, dtype=np.float64)
	# print('>>>>>>>>!',prototype[100,100])
	# print(image, prototype, center, sigma, rhoList, sigma0,  alpha, rotationInvariance)
	subject = 255 - np.asarray(image, dtype=np.float64)
	subject = subject/255
	cosfire_symm = c.COSFIRE(c.CircleStrategy(c.DoGFilter, (sigma, 1), prototype=prototype, center=center, rhoList=rhoList, sigma0=sigma0,  alpha=alpha, rotationInvariance = rotationInvariance)).fit()
	result_symm = cosfire_symm.transform(subject)
	result = c.rescaleImage(result_symm, 0, 255)
	return result
	# binaryResult = np.where(result > 37, 255, 0)

# Saving
# img_symm = Image.fromarray(result_symm.astype(np.uint8))
# img_symm.save('output/output_symm.png')



