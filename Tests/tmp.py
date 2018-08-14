import numpy as np
import multiprocessing as mp
import time

def merge(image, tiles, sections):
	result = np.empty_like(image)
	last = 0
	for _,tile in enumerate(tiles):
		result[last:last+len(tile),] = tile
		last += len(tile)

	return result



timing = []
num_cores = mp.cpu_count()
image = (np.matrix(np.random.randint(0,255, size=(8265, 7535))))

image_tiles = np.array_split(image, num_cores, axis=0)

times = []
for i in range(100):
	t0 = time.time() 
	s = np.vstack(image_tiles)
	times.append(time.time()-t0)
	average = np.mean(times)*1000
timing.append('stack['+str(len(image))+']:' +str(average) )

for i in range(100):
	t0 = time.time() 
	m = merge(image, image_tiles, num_cores)
	times.append(time.time()-t0)
	average = np.mean(times)*1000
timing.append('merge['+str(len(image))+']:' +str(average) )

for i in range(100):
	t0 = time.time() 
	s = np.vstack(image_tiles)
	times.append(time.time()-t0)
	average = np.mean(times)*1000
timing.append('stack['+str(len(image))+']:' +str(average) )


for i in timing:
		print(i)
print(":stack == merge:", np.isclose(m, s).all())
