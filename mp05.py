#!/usr/bin/python

'''
Sample usage:
e.g. 01: ./mp05.py test1.bmp 2.6 0.04
e.g. 02: ./mp05.py lena.bmp 1.4 0.2
e.g. 03: ./mp05.py joy1.bmp 1.2 0.2
e.g. 04: ./mp05.py gun1.bmp 1.8 0.12
'''

import sys
import scipy.ndimage as ndi
import numpy as np 
import Image

def gaussSmooth(img, sigma):
    return ndi.filters.gaussian_filter(img, sigma)

def imgGrad(smoothImg):
    # Use Sobel Operator
    G = Image.new('L', (height,width))
    gradx = np.array(G, dtype = float)
    grady = np.array(G, dtype = float)
    Gx = [[1,1,1], [0,-1,0], [-1,0,-1]]
    Gy = [[-1,0,1], [-1,0,1], [-1,0,1]]
    for x in range(1, width-1):
        for y in range(1, height-1):
            tempx = (Gx[0][0] * smoothImg[x-1][y-1]) + (Gx[0][1] * smoothImg[x][y-1]) + \
                    (Gx[0][2] * smoothImg[x+1][y-1]) + (Gx[1][0] * smoothImg[x-1][y]) + \
                    (Gx[1][1] * smoothImg[x][y]) + (Gx[1][2] * smoothImg[x+1][y]) + \
                    (Gx[2][0] * smoothImg[x-1][y+1]) + (Gx[2][1] * smoothImg[x][y+1]) + \
                    (Gx[2][2] * smoothImg[x+1][y+1])
            tempy = (Gy[0][0] * smoothImg[x-1][y-1]) + (Gy[0][1] * smoothImg[x][y-1]) + \
                    (Gy[0][2] * smoothImg[x+1][y-1]) + (Gy[1][0] * smoothImg[x-1][y]) + \
                    (Gy[1][1] * smoothImg[x][y]) + (Gy[1][2] * smoothImg[x+1][y]) + \
                    (Gy[2][0] * smoothImg[x-1][y+1]) + (Gy[2][1] * smoothImg[x][y+1]) + \
                    (Gy[2][2] * smoothImg[x+1][y+1])
            gradx[x][y] = tempx
            grady[x][y] = tempy
    G_mag = np.hypot(gradx, grady)
    G_theta = np.arctan2(grady, gradx)
    G_theta = 180+(180/np.pi)*G_theta
    for x in range(width):
        for y in range(height):
            if (G_theta[x][y]<22.5 and G_theta[x][y]>=0) or (G_theta[x][y]>=157.5 and G_theta[x][y]<202.5) or (G_theta[x][y]>=337.5 and G_theta[x][y]<=360):
               G_theta[x][y]=0
            elif (G_theta[x][y]>=22.5 and G_theta[x][y]<67.5) or (G_theta[x][y]>=202.5 and G_theta[x][y]<247.5):
                 G_theta[x][y]=45
            elif (G_theta[x][y]>=67.5 and G_theta[x][y]<112.5)or (G_theta[x][y]>=247.5 and G_theta[x][y]<292.5):
                 G_theta[x][y]=90
            else:
                G_theta[x][y]=135
    return (G_mag, G_theta)

def magSuppress(G_mag, G_theta):
    sup_mag = G_mag.copy()
    for x in range(1, width-1):
        for y in range(1, height-1):
            if G_theta[x][y]==0:
                if (G_mag[x][y]<=G_mag[x][y+1]) or (G_mag[x][y]<=G_mag[x][y-1]):
                    sup_mag[x][y]=0
            elif G_theta[x][y]==45:
                if (G_mag[x][y]<=G_mag[x-1][y+1]) or (G_mag[x][y]<=G_mag[x+1][y-1]):
                    sup_mag[x][y]=0
            elif G_theta[x][y]==90:
                if (G_mag[x][y]<=G_mag[x+1][y]) or (G_mag[x][y]<=G_mag[x-1][y]):
                    sup_mag[x][y]=0
            else:
                if (G_mag[x][y]<=G_mag[x+1][y+1]) or (G_mag[x][y]<=G_mag[x-1][y-1]):
                    sup_mag[x][y]=0
    return sup_mag

def thresh(sup_mag, factor):
    return (factor*np.max(sup_mag), 0.5*factor*np.max(sup_mag))

def linkEdges(sup_img, th_H, th_L):    
    outImg = np.zeros((width, height))
    tempImg = np.zeros((width, height))
    for x in range(width):
        for y in range(height):
            if sup_img[x][y]>=th_H:
                outImg[x][y]=sup_img[x][y]
            if sup_img[x][y]>=th_L:
                tempImg[x][y]=sup_img[x][y]
    tempImg = tempImg - outImg

    def recursion(i, j):
        x = [-1,0,1,-1,1,-1,0,1]
        y = [-1,-1,-1,0,0,1,1,1]
        for k in range(8):
            if outImg[i+x[k]][j+y[k]]==0 and tempImg[i+x[k]][j+y[k]]!=0:
                outImg[i+x[k]][j+y[k]]=1
                recursion(i+x[k], j+y[k])

    for i in range(1, width-1):
        for j in range(1, height-1):
            if outImg[i][j]:
                outImg[i][j]=1
                recursion(i, j)
    return outImg

def main():
    img = Image.open(sys.argv[1])
    global width
    global height
    width = img.size[1]
    height = img.size[0]
    imgdata = np.array(img.convert('L'), dtype=float)
    sigma = float(sys.argv[2])
    factor = float(sys.argv[3])
    smoothImg = gaussSmooth(imgdata, sigma)
    G_mag, G_theta = imgGrad(smoothImg)
    sup_img = magSuppress(G_mag, G_theta)
    th_H, th_L = thresh(sup_img, factor)
    outImg = linkEdges(sup_img, th_H, th_L) 
    for x in range(width):
        for y in range(height):
            if outImg[x][y] == 1:
                outImg[x][y] = 255
    outImg = Image.fromarray(outImg)
    outImg.show() 

if __name__ == "__main__": main()