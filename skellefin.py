from PIL import Image
from collections import defaultdict
import random

FILE="shapes.png"
im = Image.open(FILE)

def get_neighbors(position):
    return 


def shape_separate(image):
    # basically a flood fill, but only for pixels of the same color
    pixels = image.load()
    shape_no = 0
    visited = defaultdict(int)
    width, height = image.size

    for i, px in enumerate(image.getdata()):
        x = i % width
        y = int(i / width)

        if not visited[(x, y)]:
            shape_no += 1
            shape_color = (
                random.randint(0, 128),
                random.randint(0, 128),
                random.randint(0, 128) )
            # do our flood fill...
            to_visit = [(x, y)]
            index = 0

            while index < len(to_visit):
                position = to_visit[index]
                index += 1

                if visited[position]:
                    continue

                visited[position] = shape_no
                neighbors = (
                    (position[0] + 0, position[1] + 1),
                    (position[0] + 1, position[1] + 0),

                    (position[0] - 0, position[1] - 1),
                    (position[0] - 1, position[1] - 0),
                )


                for neighbor in neighbors:
                    if neighbor[0] < 0 or neighbor[1] < 0:
                        continue

                    if neighbor[0] >= width or neighbor[1] >= height:
                        continue

                    delta = \
                        abs(pixels[neighbor][0] - pixels[position][0]) + \
                        abs(pixels[neighbor][1] - pixels[position][1]) + \
                        abs(pixels[neighbor][2] - pixels[position][2])

                    if delta > 20:
                        continue

                    to_visit.append(neighbor)

                pixels[position] = shape_color


    print "FOUND %s SHAPES" % shape_no
    image.save(FILE + ".shapes.png")


            



def flood_fill(image):
    to_visit = []
    visited = defaultdict(int)

    # FIND ALL BLACK PIXELS, FIRST
    pixels = image.load()
    index = 0
    width, height = image.size
    for px in image.getdata():
        if px[0] == 0 and px[1] == 0 and px[2] == 0:
            to_visit.append(((index % width, int(index / width)), 0))
        index += 1
        

    count = 0
    index = 0
    max_depth = 0

    print "BLACK PIXELS COUNT", len(to_visit)
    while index < len(to_visit):
        position, depth = to_visit[index]

        index += 1

        if visited[position]:
            continue

        max_depth = max(depth, max_depth)
        count += 1
        visited[position] = depth
        neighbors = (
            (position[0] + 0, position[1] + 1),
            (position[0] + 1, position[1] + 0),

            (position[0] - 0, position[1] - 1),
            (position[0] - 1, position[1] - 0),
        )


        for neighbor in neighbors:
            if neighbor[0] < 0 or neighbor[1] < 0:
                continue

            if neighbor[0] >= width or neighbor[1] >= height:
                continue

            to_visit.append((neighbor, depth + 1))


    print 'VISITED', count

    # DEPTH STEPS = max_depth, so take 128 and divide by max_depth then multiply
    print 'MAX DEPTH', max_depth
    color_step = 2
    print "COLOR STEP", color_step
    for pos in visited:
        depth = visited[pos]
        px_val = color_step * depth
        pixels[pos] = (px_val, px_val, px_val)

    image.save(FILE + ".skel.png")

shape_separate(im.copy())
flood_fill(im.copy())

