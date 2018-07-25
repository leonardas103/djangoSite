import cosfire as c
import numpy as np
import math as m
import cv2
import time
from PIL import Image
import sys


def main(image, prototype, center, rhoList, sigma0,  alpha, rotationInvariance):
	proto = np.asarray(prototype, dtype=np.float64)
	subject = 255 - np.asarray(image, dtype=np.float64)[:,:,1]
	subject = subject/255

	cosfire_symm = c.COSFIRE(c.CircleStrategy, c.DoGFilter, (2.4, 1), prototype=proto, center=(cx,cy), rhoList=range(0,9,2), sigma0=3,  alpha=0.7, rotationInvariance = np.arange(12)/12*np.pi).fit()
	result_symm = cosfire_symm.transform(subject)

	Image.fromarray(c.rescaleImage(cosfire_symm.strategy.protoStack.stack[0].image, 0, 255).astype(np.uint8)).save('output/filtered_prototype_symm.png')
	result = c.rescaleImage(result_symm, 0, 255)
	return result
	# binaryResult = np.where(result > 37, 255, 0)

# Saving
# img_symm = Image.fromarray(result_symm.astype(np.uint8))
# img_symm.save('output/output_symm.png')



