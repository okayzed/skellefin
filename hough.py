# TAKEN FROM OPENCV EXAMPLES

import cv2
import cv2.cv as cv

import numpy as np
import sys

from PIL import Image, ImageFilter

FILE = sys.argv[1]

im = Image.open(FILE)
im1 = im.filter(ImageFilter.BLUR)

img = cv2.imread(FILE)
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
blur = cv2.blur(img, (5, 5))
edges = cv2.Canny(gray,50,150,apertureSize = 3)

gray = (255-gray)

cv2.imwrite(FILE + "gray.jpg", gray)
cv2.imwrite(FILE + "edges.jpg", edges)

minLineLength = 20
maxLineGap = 5

lines = cv2.HoughLinesP(gray,1,np.pi/180,10,minLineLength,maxLineGap)
circles = cv2.HoughCircles(gray,cv.CV_HOUGH_GRADIENT,1,50,
                            param1=50,param2=30,minRadius=0,maxRadius=0)


if lines is not None:
  print "FOUND ", len(lines[0]), "LINES"
  for x1,y1,x2,y2 in lines[0]:
      cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)


if circles is not None:
  print "FOUND ", len(circles[0]), "CIRCLES"
  for x,y,r in circles[0]:
      cv2.circle(img, (x,y), r, (0, 255, 0), 2)


cv2.imwrite(FILE + 'houghlines3.jpg',img)

