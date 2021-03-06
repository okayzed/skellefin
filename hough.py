# TAKEN FROM OPENCV EXAMPLES

import cv2
import cv2.cv as cv

import numpy as np
import sys

import math

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


def line_length(line):
  return math.sqrt((line[0] - line[2])**2 + (line[1] + line[3])**2)

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

  print "JOINED INTO %s LINES" % len(lines)
  for x1,y1,x2,y2 in lines:
      color = (
        random.randint(0, 255), 
        random.randint(0, 255), 
        random.randint(0, 255), 
      )

      cv2.line(blankimg,(x1,y1),(x2,y2),color,2)

  cv2.imwrite(FILE + 'houghlines.jpg',blankimg)

  blankimg[:] = (255, 255, 255)

  lines = list(lines)
  while joined:
      didjoin = False
      print len(lines), "LINES ARE", lines

      newlines = []

      from collections import defaultdict
      used = defaultdict(bool)

      lines.sort(key=lambda x: math.sqrt(abs(x[2] - x[0])**2 + abs(x[3] - x[1])**2))
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
              candidates = []
              for corner_pair in CORNERS:
                if joined:
                    break

                x, y = corner_pair[0]
                a, b = corner_pair[1]

                x_val = line[x]
                y_val = line[y]

                a_val = neighbor[a]
                b_val = neighbor[b]

                THRESH=30
                closeness = math.sqrt((x_val - a_val)**2 + (y_val - b_val)**2)

                if closeness > THRESH:
                    continue

                print "CORNERS MATCH", (x_val, y_val), (a_val, b_val), line, neighbor

                if abs(slope1 - slope2) > 0.002:
                    continue

                print "SLOPES MATCH", slope1, slope2

                candidates.append((closeness, [x, y, a, b]))

              if not candidates:
                continue

              candidates.sort()
              closeness, (x, y, a, b) = candidates[0]



              # now, we take the two corners that we matched with and use
              # their complements as the line segment...
              new_x_val = line[(x+2) % 4]
              new_y_val = line[(y+2) % 4]

              new_a_val = neighbor[(a + 2) % 4]
              new_b_val = neighbor[(b + 2) % 4]

              # THIS IS WHERE WE NEED TO DO IT RIGHT?
              newline = [
                  new_x_val,
                  new_y_val,
                  new_a_val,
                  new_b_val
              ]

              if tuple(newline) != tuple(line) and tuple(newline) != tuple(neighbor):
                  print "LINE LENGTHS", line_length(line), line_length(neighbor), line_length(newline)
                  if (line_length(line) > line_length(newline) or line_length(neighbor) > line_length(newline)):
                    print "RESULTING LINE IS TOO SMALL", newline, "SKIPPING"
                    continue

                  print "JOINING", line, neighbor
                  print "NEWLINE IS", newline

                  used[tuple(line)] = True
                  used[tuple(neighbor)] = True
            
                  didjoin = True
                  joined = True

                  newlines.append(newline)

          if not joined:
            print "COULDNT JOIN LINE, ADDING IN", line
            newlines.append(line)



      lines = newlines
      if didjoin:
          joined = True

          

  print "JOINED INTO %s LINES" % len(lines)
  for x1,y1,x2,y2 in lines:
      color = (
        random.randint(0, 128), 
        random.randint(0, 128), 
        random.randint(0, 128), 
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


cv2.imwrite(FILE + 'joinedlines.jpg',blankimg)

