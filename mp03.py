#!/usr/bin/python

import Image, ImageDraw
import sys
import numpy as np 

# function to carry out histogram equalization on a image
# input is a image array
def HistoEqualization(imgarr):
	# generate histogram and bins using histogram function from numpy - use 256 bins & normalize
	imghist, bins = np.histogram(imgarr.flatten(), 256, normed=True)
	
	# calculate the cumulative distributive function using the histogram obtained above
	cdf = imghist.cumsum()

	# reinitialize the cdf to a 'gray level' image
	cdf = 255 * cdf / cdf[-1]

	# perform linear interpolation to map the new values obtained above to the original values in imgarr
	outimg = np.interp(imgarr.flatten(), bins[:-1], cdf)
	return outimg.reshape(imgarr.shape)

# Lighting correction done using Log transformation
def LightCorrect(imgarr):
	imgarr = imgarr.astype('float')
	maxval = np.max(imgarr)
	# carry out log transformation
	outimgarr = (255.0 * np.log(1+imgarr))/np.log(1+maxval)
	outimgarr = outimgarr.astype('int')
	return outimgarr

def main():
	img = Image.open(sys.argv[1])
	imgarr = np.array(img.convert('L')) # convert image to gray image
	outimg = Image.fromarray(np.uint8(HistoEqualization(imgarr))) # convert image from array to PIL
	outimg2 = Image.fromarray(np.uint8(LightCorrect(HistoEqualization(imgarr)))) # convert image from array to PIL
	
	img.show()
	outimg.show()
	outimg2.show()

if __name__ == "__main__": main()
