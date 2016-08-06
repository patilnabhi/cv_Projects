#!/usr/bin/python

import cv2
import sys
import Image, ImageDraw
import numpy as np
import mouse_click as mc 

def hist1(img, samimg):
	oriimg = img
	img = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
	M = cv2.calcHist([samimg],[0, 1], None, [180, 256], [0, 180, 0, 256] )
	I = cv2.calcHist([img],[0, 1], None, [180, 256], [0, 180, 0, 256] )
	# h,s,v = cv2.split(img)
	# M = np.histogram2d(h.ravel(),s.ravel(),256,[[0,180],[0,256]])[0]
	# h,s,v = cv2.split(samimg)
	# I = np.histogram2d(h.ravel(),s.ravel(),256,[[0,180],[0,256]])[0]

	R = M/(I+1)

	h,s,v = cv2.split(img)
	B = R[h.ravel(), s.ravel()]
	B = np.minimum(B,1)
	B = B.reshape(img.shape[:2])
	disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7,7))
	cv2.filter2D(B,-1,disc,B)
	B = np.uint8(B)
	cv2.normalize(B,B,0,255,cv2.NORM_MINMAX)

	ret,thresh = cv2.threshold(B,0,255,0)

	for i in range(oriimg.shape[0]):
		for j in range(oriimg.shape[1]):
			for k in range(oriimg.shape[2]):
				if thresh[i, j] == 0:
					oriimg[i,j] = 0

	cv2.imshow('out', oriimg)
	cv2.waitKey(0)

def gaus(img, samimg):
	oriimg = img
	I = samimg
	I = np.float64(I)
	R = I[:,:,0]
	G = I[:,:,1]
	B = I[:,:,2]
	Int = R+G+B
	Int[np.where(Int==0)] = 1000000
	r = np.divide(R*1.,Int)
	g = np.divide(G*1.,Int)

	mean_r = np.mean(r)
	sigma_r = np.std(r)
	mean_g = np.mean(g)
	sigma_g = np.std(g)

	A = img
	A = np.float64(A)
	RA = A[:,:,0]
	GA = A[:,:,1]
	BA = A[:,:,2]
	IntA = RA+GA+BA
	IntA[np.where(IntA==0)] = 1000000 # to remove division by 0
	rA = np.divide(RA*1.,IntA)
	gA = np.divide(GA*1.,IntA)

	pr = (1/(sigma_r*np.sqrt(2*np.pi)))*np.exp(-((rA-mean_r)**2)/(2*sigma_r**2))
	pg = (1/(sigma_g*np.sqrt(2*np.pi)))*np.exp(-((gA-mean_g)**2)/(2*sigma_g**2))
	final = np.round(np.multiply(pr,pg))
	
	for i in range(oriimg.shape[0]):
		for j in range(oriimg.shape[1]):
			for k in range(oriimg.shape[2]):
				if final[i, j] == 0:
					oriimg[i,j] = 0

	cv2.imwrite('out.png', oriimg)
	cv2.imshow('out', oriimg)
	cv2.waitKey(0)

def main():
	img = cv2.imread(sys.argv[1])
	roi = []
	num = int(sys.argv[3])
	for i in range(num):
		mc.getSample()
		samimg = cv2.imread('samimg.bmp')
		if sys.argv[2] == 'histogram':
			samimg = cv2.cvtColor(samimg,cv2.COLOR_BGR2HSV)
		roi.append(samimg)
	samimg = roi[0]
	for i in range(num-1):
		samimg = np.vstack((samimg, roi[i+1]))

	if sys.argv[2] == 'histogram':
		hist1(img, samimg)
	elif sys.argv[2] == 'gaussian':
		gaus(img, samimg)

def hist2(img, samimg):
	I = samimg
	I = np.float32(I)
	B = I[:,:,0]
	G = I[:,:,1]
	R = I[:,:,2]
	Int = R+G+B
	Int[np.where(Int==0)] = 1000000
	r = np.divide(R*1.,Int)
	g = np.divide(G*1.,Int)
	bins = 256
	rint = np.round(r*(bins-1)+1)
	gint = np.round(g*(bins-1)+1)
	colors = gint.flatten()+(rint.flatten()-1)*bins
	hist = np.zeros((bins,bins))
	for row in range(bins-1):
		for col in range(bins-row):
			hist[row,col] = len(np.where(colors==(((col+(row-1)*bins)))))

	A = img
	A = np.float32(A)
	BA = A[:,:,0]
	GA = A[:,:,1]
	RA = A[:,:,2]
	IntA = RA+GA+BA
	IntA[np.where(IntA==0)] = 1000000
	rA = np.divide(RA*1.,IntA)
	gA = np.divide(GA*1.,IntA)

	proj_array = np.zeros((np.size(rA,0),np.size(rA,1)))
	for i in range(np.size(rA,0)-1):
		for j in range(np.size(rA,1)-1):
			r_proj = np.round(rA[i,j]*(bins-1)+1)
			g_proj = np.round(gA[i,j]*(bins-1)+1)
			proj_array[i,j] = hist[r_proj, g_proj]
	
	# print proj_array
	# final = Image.fromarray(proj_array)
	cv2.imshow('out', proj_array)
	cv2.waitKey(0) 

if __name__ == "__main__": main()