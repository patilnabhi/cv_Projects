#!/usr/bin/python

import Image, ImageDraw
import sys
from itertools import product
from ccl import *
import matplotlib.pyplot as plt

# Erosion function for white images on black background
def Erosion(img, SE):
	X, Y = img.size
	data = img.load()
	outimg = Image.new(img.mode, img.size)
	outimg_data = outimg.load()

	# Define dimensions of SE
	seX = 3 
	seY = 3

	# Define centre of SE
	hx = seX/2
	hy = seY/2

	for y, x in product(range(hy, Y-hy), range(hx, X-hx)):
		x0 = []
		if(data[x, y] == 255): 
		# Check all pixels in SE and set only elements at the above range to be white
			if SE[0]: x0.append(data[x-1, y-1])
			if SE[1]: x0.append(data[x, y-1])
			if SE[2]: x0.append(data[x+1, y-1])
			if SE[3]: x0.append(data[x-1, y])
			if SE[4]: x0.append(data[x, y])
			if SE[5]: x0.append(data[x+1, y])
			if SE[6]: x0.append(data[x-1, y+1])
			if SE[7]: x0.append(data[x, y+1])
			if SE[8]: x0.append(data[x+1, y+1])
			if all(x0): outimg_data[x, y] = 255

	return outimg

# Dilation function for white images on black background
def Dilation(img, SE):
	X, Y = img.size
	data = img.load()
	outimg = Image.new(img.mode, img.size)
	outimg_data = outimg.load()

	# Define dimensions of SE
	seX = 3
	seY = 3

	# Define centre of SE
	hx = seX/2
	hy = seY/2

	for y, x in product(range(hy, Y-hy), range(hx, X-hx)):
		if(data[x, y] == 255):
			# Check SE & set the respective surrounding pixels in original image to be white
			if SE[0]: outimg_data[x-1, y-1] = 255
			if SE[1]: outimg_data[x, y-1] = 255
			if SE[2]: outimg_data[x+1, y-1] = 255
			if SE[3]: outimg_data[x-1, y] = 255
			if SE[4]: outimg_data[x, y] = 255
			if SE[5]: outimg_data[x+1, y] = 255
			if SE[6]: outimg_data[x-1, y+1] = 255
			if SE[7]: outimg_data[x, y+1] = 255
			if SE[8]: outimg_data[x+1, y+1] = 255

	return outimg

# Define 'Opening' function as a combination of Erosion followed by Dilation 
def Opening(img, SE):
	return Dilation(Erosion(img, SE), SE)

# Define 'Opening' function as a combination of Dilation followed by Erosion 
def Closing(img, SE):
	return Erosion(Dilation(img, SE), SE)

'''Define Boundary as a function that performs the following morphological operation : 
A - A(-)B where A is original image and B is SE
'''
def Boundary(img):
	X, Y = img.size
	data1 = img.load()
	outimg = Image.new(img.mode, img.size)
	outimg_data = outimg.load()

	data2 = Erosion(img, (1,1,1,1,1,1,1,1,1)).load()

	for y, x in product(range(Y), range(X)):
		outimg_data[x, y] = data1[x, y] - data2[x, y]
	
	return outimg

# A helper function to get the image after filtering and removing noise (using CCL and size filter from MP01)
def getOutputImg2(img, TH):
	labels = applyCcl(img)
	labels = applySizeFilter(labels, TH)
	output_img = Image.new(img.mode, img.size)
	outdata = output_img.load()

	colors = {}
	
	for (x, y) in labels:
		temp = find(labels[(x, y)])
		labels[(x, y)] = temp

		if temp not in colors:
			colors[temp] = 255

		outdata[x, y] = colors[temp]

	return output_img

'''
When running in command line, this program takes in 3 arguments:
1. image: e.g. 'gun.bmp'
2. SE (3x3 pix element): e.g. 111111111
3. morph operations (any number of combinations): e.g. D2E1CB

D2E1CB = Dilation x 2 --> Erosion x 1 --> Closing --> Boundary Extraction
'''
def main():
	img = Image.open(sys.argv[1])
	img = img.convert('1')
	outimg = img
	
	try:
		SE = sys.argv[2]
		SE = map(int, SE)
		todo = sys.argv[3]
		for i in range(len(todo)):
			if todo[i] == 'D':
				itr = int(todo[i+1])
				for i in range(itr):
					outimg = Dilation(outimg, SE)

			if todo[i] == 'E':
				itr = int(todo[i+1])
				for i in range(itr):
					outimg = Erosion(outimg, SE)
		
			if todo[i] == 'C':
				outimg = Closing(outimg, SE)

			if todo[i] == 'O':
				outimg = Opening(outimg, SE)

			if todo[i] == 'B':
				# outimg = getOutputImg2(outimg)
				outimg = Boundary(outimg)

			if todo[i] == 'N':
				outimg = getOutputImg2(outimg, int(sys.argv[4]))
		
		img.show() # Display original image
		outimg.show() # Display output image
	except:
		print "Please check your input arguments!"

if __name__ == "__main__": main()