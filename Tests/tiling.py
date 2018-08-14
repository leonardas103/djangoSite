import numpy as np

def split_easy_sq(image, overlap, sections):
	height, width = np.shape(image)
	tiles = []
	step = int(np.ceil(width/(sections//2)))
	step_h = int(np.ceil(height/2))
	for row in [0, step_h]: 
		for col in range(0, width, step):
				row_start = row-overlap if row-overlap > 0 else 0
				col_start = col-overlap if col-overlap > 0 else 0
				tiles.append(image[row_start:row+step_h+overlap:, col_start:col+step+overlap])
	return tiles

def split_easy_row(image, overlap, sections):
	height, _ = np.shape(image)
	tiles = []
	step = int(np.ceil(height/sections))
	for row in range(0, height, step):
		row_start = row-overlap if row-overlap > 0 else 0
		tiles.append(image[row_start:row+step+overlap:,])
	return tiles

def merge_easy_row(image, tiles, overlap, sections):
	height, _ = np.shape(image)
	data_type = int if isinstance(tiles[0][0,:],int) else float	
	result = np.empty_like(image, dtype=data_type)
	tile_num = 0
	step = int(np.ceil(height/sections))
	for row in range(0, height, step):
		row_start = overlap if row-overlap > 0 else 0
		result[row:row+step,] = tiles[tile_num][row_start:row_start+step:,]
		tile_num += 1
	return result

def merge_easy_sq(image, tiles, overlap, sections):
	height, width = np.shape(image)
	data_type = int if isinstance(tiles[0][0,:],int) else float	
	result = np.empty_like(image, dtype=data_type) 
	step = int(np.ceil(width/(sections//2)))
	step_h = int(np.ceil(height/2))
	tile_num = 0
	for row in [0, step_h]: 
		for col in range(0, width, step):
			row_start = overlap if row-overlap > 0 else 0
			col_start = overlap if col-overlap > 0 else 0
			result[row:row+step_h, col:col+step] = tiles[tile_num][row_start:row_start+step_h:, col_start:col_start+step]
			tile_num += 1
	return result