import cosfire as c
import numpy as np
import math as m
import cv2
import time
from PIL import Image
import sys
#import matplotlib.pyplot as plt

global_timings = []
numthreads = 1 if len(sys.argv) < 2 else int(sys.argv[1])

# Prototype image
t0 = time.time()                  # Time point
proto_symm = np.asarray(Image.open('line.png').convert('L'), dtype=np.float64)
print('>>>>>>>>>>',proto_symm[100,100])
(cx, cy) = (100,100)
mask = np.asarray(Image.open('mask.png').convert('L'), dtype=np.float64)
subject = 255 - np.asarray(Image.open('01_test.tif').convert('RGB'), dtype=np.float64)[:,:,1]
subject = subject/255

# Store timing
global_timings.append( ("Loading in the prototype(.png), mask(.png) and input(.csv)", time.time()-t0) )

# Symmetrical filter
t1 = time.time()                  # Time point
cosfire_symm = c.COSFIRE(
		c.CircleStrategy(c.DoGFilter, (2.4, 1), prototype=proto_symm, center=(cx,cy), rhoList=range(0,9,2), sigma0=3,  alpha=0.7,
		rotationInvariance = np.arange(12)/12*np.pi)
	   ).fit()

# Store timing
global_timings.append( ("Creating the symmetrical filter, fitting it with the prototype", time.time()-t1) )
t2 = time.time()                  # Time point

result_symm = cosfire_symm.transform(subject)

# Store timing
global_timings.append( ("Transforming the subject with the symmetrical filter", time.time()-t2) )

# Asymmetrical filter
t3 = time.time()                  # Time point
cosfire_asymm = c.COSFIRE(
		c.CircleStrategy(c.DoGFilter, (1.8, 1), prototype=proto_symm, center=(cx,cy), rhoList=range(0,23,2), sigma0=2,  alpha=0.1,
		rotationInvariance = np.arange(24)/12*np.pi)
	   ).fit()
# Make asymmetrical
asymmTuples = []
for tupl in cosfire_asymm.strategy.tuples:
	if tupl[1] <= np.pi:
		asymmTuples.append(tupl)
cosfire_asymm.strategy.tuples = asymmTuples

# Store timing
global_timings.append( ("Creating the asymmetrical filter, fitting it with the prototype", time.time()-t3) )
t4 = time.time()                  # Time point

result_asymm = cosfire_asymm.transform(subject)

# Store timing
global_timings.append( ("Transforming the subject with the asymmetrical filter", time.time()-t4) )

# Save filtered prototypes for reference
Image.fromarray(c.rescaleImage(cosfire_symm.strategy.protoStack.stack[0].image, 0, 255).astype(np.uint8)).save('output/filtered_prototype_symm.png')
Image.fromarray(c.rescaleImage(cosfire_asymm.strategy.protoStack.stack[0].image, 0, 255).astype(np.uint8)).save('output/filtered_prototype_asymm.png')

t5 = time.time()                  # Time point

# Add results from symmetrical and asymmetrical operators
result = result_symm + result_asymm

# Stretching and binarization
result_symm = c.rescaleImage(result_symm, 0, 255)
result_asymm = c.rescaleImage(result_asymm, 0, 255)
#result = np.multiply(result, mask)
result = c.rescaleImage(result, 0, 255)
binaryResult = np.where(result > 27, 255, 0)

# Store timing
global_timings.append( ("Combining results, stretching them, masking them, binarization", time.time()-t5) )
t6 = time.time()                  # Time point

# Saving
img_symm = Image.fromarray(result_symm.astype(np.uint8))
img_symm.save('output/output_symm.png')
img_asymm = Image.fromarray(result_asymm.astype(np.uint8))
img_asymm.save('output/output_asymm.png')
img = Image.fromarray(result.astype(np.uint8))
img.save('output/output.png')
imgBinary = Image.fromarray(binaryResult.astype(np.uint8))
imgBinary.save('output/output_binary.png')

global_timings.append( ("Storing results to file", time.time()-t6) )

print("\n --- TIME MEASUREMENTS: Symmetric Filter, {} thread(s) --- ".format(numthreads))
for timing in cosfire_symm.strategy.timings:
	print( "{:7.2f}ms\t{}".format(timing[1]*1000, timing[0]) )
print("\n --- TIME MEASUREMENTS: Asymmetric Filter, {} thread(s) --- ".format(numthreads))
for timing in cosfire_asymm.strategy.timings:
	print( "{:7.2f}ms\t{}".format(timing[1]*1000, timing[0]) )
print("\n --- TIME MEASUREMENTS: Global, {} thread(s) --- ".format(numthreads))
for timing in global_timings:
	print( "{:7.2f}ms\t{}".format(timing[1]*1000, timing[0]) )
