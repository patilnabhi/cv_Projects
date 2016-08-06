#!/usr/bin/python

import cv2
import numpy as np 
import sys
import Image
from mp05 import getEdges

def hough_transform(img, th_res=1, rho_res=1):
	width, height = img.shape
	th = np.linspace(-90.0, 0.0, np.ceil(90.0/th_res) + 1.0)
	th = np.concatenate((th, -th[len(th)-2::-1]))

	D = np.sqrt((height - 1)**2 + (width - 1)**2)
	q = np.ceil(D/rho_res)
	nrho = 2*q + 1
	rho = np.linspace(-q*rho_res, q*rho_res, nrho)

	H_img = np.zeros((len(rho), len(th)))

	for y in range(width):
		for x in range(height):
			if img[y, x]:
				for theta in range(len(th)):
					rhoVal = x*np.cos(th[theta]*np.pi/180.0) + y*np.sin(th[theta]*np.pi/180.0)
					rhoInd = np.nonzero(np.abs(rho-rhoVal) == np.min(np.abs(rho-rhoVal)))[0]
					H_img[rhoInd[0], theta] += 1
	return rho, th, H_img

def rho_x_y_pairs(H_img, n, rhos, thetas):
	flat = list(set(np.hstack(H_img)))
	flat_sort = sorted(flat, key=lambda n: -n)
	sorted_coords = [(np.argwhere(H_img == value)) for value in flat_sort[0:n]]
	rho_th = []
	x_y = []

	for i in range(0, len(sorted_coords), 1):
	    temp = sorted_coords[i]
	    
	    for j in range(0, len(temp), 1):
			n,m = temp[j]
			rho = rhos[n]
			theta = thetas[m]
			rho_th.append([rho, theta])
			x_y.append([m, n])

	return [rho_th[0:n], x_y]

def valid(pt, ymax, xmax):
	x, y = pt
	if x <= xmax and x >= 0 and y <= ymax and y >= 0:
		return True
	else:
		return False

def round_tuple(tup):
	x,y = [int(round(num)) for num in tup]
	return (x,y)

def draw_lines(out_img, pairs):
	out_img_y, out_img_x, channels = np.shape(out_img)
	
	for i in range(0, len(pairs), 1):
		pt = pairs[i]
		rho = pt[0]
		th = pt[1] * np.pi / 180

		m = -np.cos(th) / np.sin(th)
		b = rho / np.sin(th)

		left = (0, b)
		right = (out_img_x, out_img_x * m + b)
		top = (-b / m, 0)
		bottom = ((out_img_y - b) / m, out_img_y)

		pts = [pnt for pnt in [left, right, top, bottom] if valid(pnt, out_img_y, out_img_x)]
		
		if len(pts) == 2:
			cv2.line(out_img, round_tuple(pts[0]), round_tuple(pts[1]), (0,255,0), 1)

def main():
	img_in = cv2.imread(sys.argv[1],)
	th_factor = float(sys.argv[2])
	rho_factor = float(sys.argv[3])
	img = img_in[:,:,::-1]
	img = Image.fromarray(img)
	edges = getEdges(img, 1.4, 0.4)
	img = np.array(img)
	rho, th, H_img = hough_transform(edges, th_factor, rho_factor)

	rho_th, x_y = rho_x_y_pairs(H_img, 15, rho, th)
	out_img = img.copy()
	draw_lines(out_img, rho_th)

	out_img = Image.fromarray(out_img)
	out_img.show()

if __name__ == "__main__": main()