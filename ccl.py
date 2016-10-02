#!/usr/bin/python

import Image, ImageDraw
import sys
import math, random
from itertools import product
from collections import Counter

etable = [] # equivalence table defined as global (empty) 'array'

# function to add new labels to equivalence table 
def makeLabel(label):
	a = label
	etable.append(a)
	return a

# function to update labels in equivalence table
def setVal(a, val):
	while etable[a] < a:
		b = etable[a]
		etable[a] = val
		a = b
	etable[a] = val

# function to scan labels through equivalence table in order to find lowest label
def findVal(a):
	while etable[a] < a:
		a = etable[a]
	return a

# function to find lowest label and replace label in equivalence table
def find(a):
	val = findVal(a)
	setVal(a, val)
	return val

# function to set 2 labels as equal in equivalence table
def merge(a, b):
	if a != b:
		vala = findVal(a)
		valb = findVal(b)
		if vala > valb: 
			vala = valb
		setVal(b, vala)
		setVal(a, valb)

# function to flatten the equivalence table into a 1D array
def flatten():
	for i in range(1, len(etable)):
		etable[i] = etable[etable[i]]
	return etable

# function to get no. of components in image given a labels dictionary
def getNumLabel(labels):
	return len(set((Counter(labels).values())))

# function to perform a second scan of the labels 
# and replace each label by lowest label in its equivalent set
def secondScan(labels):
	for (x, y) in labels:
		temp = find(labels[(x, y)])
		labels[(x, y)] = temp
	return labels

# function to apply CCL algorithm to the image
def applyCcl(img):
	data = img.load() # a pixel access object is stored in data; it is a 2D array
	width, height = img.size # get width & height of image

	label = 0 # set initial label as '0'
	labels = {} # define labels as 'dictionary' type

	# perform top <--> down & left <--> right scan of image
	for v, u in product(range(height), range(width)): # nested 'for' loop using 'product' from itertools
		if data[u,v] == 0: # if pixel is black, skip
			pass

		# if upper pixel (b) is white, assign its label to current pixel
		elif v > 0 and data[u, v-1] == 255:  
			b = labels[(u, v-1)]
			labels[u, v] = b

			# if left pixel (c) (together with (b)), is also white, 'merge' both labels
			if u > 0 and data[u-1, v] == 255:
				c = labels[(u-1, v)]
				merge(b,c)

		# if only left pixel (c) is white, assign its label to current pixel
		elif u > 0 and data[u-1, v] == 255:
			labels[u, v] = labels[(u-1, v)]

		# if none of above, assign new label to the pixel and enter label in equivalence table 
		else:
			labels[u, v] = makeLabel(label)
			label += 1
	
	flatten()
	labels = secondScan(labels)	# replace each label by lowest label in its equivalent set
	
	return labels

# function to apply size filter to 'labels' data based on a threshold 'TH' value
def applySizeFilter(labels, TH):
	coun = Counter(labels.values())
	labels = dict((k, v) for k, v in labels.items() if coun[v] > TH)
	return labels

# function to generate an output image where each component is given a (random) different color
def getOutputImg(img, labels):
	width, height = img.size
	output_img = Image.new("RGB", (width, height))
	outdata = output_img.load()

	colors = {}
	
	for (x, y) in labels:
		temp = find(labels[(x, y)])
		labels[(x, y)] = temp

		if temp not in colors:
			colors[temp] = (random.randint(0,255), random.randint(0,255), random.randint(0,255))

		outdata[x, y] = colors[temp]

	return output_img

'''
'Main' function prints the number of different labels 
and displays an output image
'''
def main():
	img = Image.open(sys.argv[1])
	img = img.convert('1') # convert input image to black & white image

	labels = applyCcl(img)
	try:
		TH = sys.argv[2]
		labels = applySizeFilter(labels, int(TH))
	except:
		pass

	num = getNumLabel(labels)
	print "No. of different labels = ", num

	output_img = getOutputImg(img, labels)
	output_img.show()

if __name__ == "__main__": main()