# TAKEN FROM OPENCV EXAMPLES

import cv2
import cv2.cv as cv

import numpy as np
import sys

import random

from PIL import Image, ImageFilter

FILE = sys.argv[1]

im = Image.open(FILE)
im1 = im.filter(ImageFilter.BLUR)

img = cv2.imread(FILE)
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
blur = cv2.blur(img, (5, 5))
edges = cv2.Canny(gray,50,150,apertureSize = 3)

blankimg = img.copy()
blankimg[:] = (255, 255, 255)

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
  unjoined_lines = []
  joined = True
  CORNERS = [
    ([0, 1], [0, 1]),
    ([0, 1], [2, 3]),
    ([2, 3], [0, 1]),
    ([2, 3], [2, 3]),
  ]

  lines = lines[0]

  newlines = []
  for line in lines:
    if line[0] == line[2]:
      if line[1] > line[3]:
        newlines.append([line[2], line[3], line[0], line[1]])

      else:
        newlines.append(line)
    else:
      newlines.append(line)
     
  lines = newlines
  while joined:
      didjoin = False
      print len(lines), "LINES ARE", lines

      newlines = []

      from collections import defaultdict
      used = defaultdict(bool)

      lines.sort(key=lambda x: abs(x[2] - x[0]) + abs(x[3] - x[1]))
      for line in lines:
          joined = False
          if used[tuple(line)]:
              continue

          for neighbor in lines:
              if used[tuple(neighbor)]:
                  continue

              if tuple(line) == tuple(neighbor):
                  continue


              # now to check slope...
              slope1 = 0
              slope2 = 0
              try:
                  slope1 = float(line[3] - line[1]) / float(line[2] - line[0]) 
              except:
                pass

              try:
                  slope2 = float(neighbor[3] - neighbor[1]) / float(neighbor[2] - neighbor[0]) 
              except:
                  pass

              # need to check the distance of all possible pairs...
              for corner_pair in CORNERS:
                if joined:
                    break

                x, y = corner_pair[0]
                a, b = corner_pair[1]

                x_val = line[x]
                y_val = line[y]

                a_val = neighbor[a]
                b_val = neighbor[b]

                THRESH=5
                if abs(x_val - a_val) > THRESH or abs(y_val - b_val) > THRESH:
                    continue

                print "CORNERS MATCH", (x_val, y_val), (a_val, b_val), line, neighbor

                if abs(slope1 - slope2) > 0.001:
                    continue

                print "SLOPES MATCH", slope1, slope2

                # now, we take the two corners that we matched with and use
                # their complements as the line segment...
                new_x_val = line[(x+2) % 4]
                new_y_val = line[(y+2) % 4]

                new_a_val = neighbor[(a + 2) % 4]
                new_b_val = neighbor[(b + 2) % 4]

                used[tuple(line)] = True
                used[tuple(neighbor)] = True
          
                # THIS IS WHERE WE NEED TO DO IT RIGHT?
                newline = [
                    new_x_val,
                    new_y_val,
                    new_a_val,
                    new_b_val
                ]

                if tuple(newline) != tuple(line) and tuple(newline) != tuple(neighbor):
                    didjoin = True
                    joined = True

                    print "JOINING", line, neighbor
                    print "NEWLINE IS", newline

                    newlines.append(newline)

          if not joined:
            newlines.append(line)



      lines = newlines
      if didjoin:
          joined = True

          

  print "JOINED INTO %s LINES" % len(lines)
  for x1,y1,x2,y2 in lines:
      color = (
        random.randint(0, 255), 
        random.randint(0, 255), 
        random.randint(0, 255), 
      )

      cv2.line(blankimg,(x1,y1),(x2,y2),color,2)


if circles is not None:
  print "FOUND ", len(circles[0]), "CIRCLES"
  for x,y,r in circles[0]:
      color = (
        random.randint(0, 255), 
        random.randint(0, 255), 
        random.randint(0, 255), 
      )
      cv2.circle(blankimg, (x,y), r, color, 2)


cv2.imwrite(FILE + 'houghlines3.jpg',blankimg)

