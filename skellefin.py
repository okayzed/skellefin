from PIL import ImageOps
from PIL import Image
from PIL import ImageFilter

from collections import defaultdict
import random
import math
import sys

FILE="shapes.png"
#FILE="qIrIf0G.png"
if len(sys.argv) > 1:
    FILE=sys.argv[1]

MIN_DIST=5
im = Image.open(FILE)

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


    print "FOUND %s SHAPES (INCLUDING OUTLINES)" % shape_no
    image.save(FILE + ".shapes.png")

    # visited is a map from the pixel -> the shape it belongs in
    return visited





def shape_fill(image, included_pixels):
    visited = defaultdict(bool)
    distances = defaultdict(lambda: defaultdict(int))
    min_distances = defaultdict(int)
    min_neighbors = {}

    from PIL import ImageDraw
    draw = ImageDraw.Draw(image)

    # Find out all pixel distances to each other...

    # DRAW LINES BETWEEN ALL CLOSEST PIXELS

    included_pixels.sort(key=lambda p: p[1])

    min_used = defaultdict(int)
    for i in xrange(len(included_pixels)):
        px1 = included_pixels[i]
        min_distances[px1] = sys.maxint
        for j in xrange(0, len(included_pixels)):
            px2 = included_pixels[j]

            if px2 == px1:
                continue

            distances[px1][px2] = math.sqrt((px1[0] - px2[0]) ** 2 + (px1[1] - px2[1])**2)
            if min_distances[px1] > distances[px1][px2] and min_used[px2] < 2:
                min_distances[px1] = distances[px1][px2]

                if px1 in min_neighbors:
                    min_used[min_neighbors[px1]] -= 1

                min_neighbors[px1] = px2
                min_used[px2] += 1



    for px in included_pixels:
        if px in min_neighbors:
            draw.line([px, min_neighbors[px]], fill=(128, 128, 128), width=1)

    
    
def grassfire_fill(image):
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
            visited[position] = min(depth, visited[position])
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
    color_step = max(256 / max_depth, 1)
    print "COLOR STEP", color_step
    for pos in visited:
        depth = visited[pos]
        px_val = color_step * depth

        if px_val < 256:
            pixels[pos] = (px_val, px_val, px_val)
        elif px_val < 256 * 2:
            px_val = px_val % 128
            pixels[pos] = (128, px_val / 2, 128)
        elif px_val < 256 * 3:
            px_val = px_val % 128
            pixels[pos] = (128, px_val, px_val / 2)
        elif px_val < 256 * 4:
            px_val = px_val % 128
            pixels[pos] = (128, px_val, px_val)
        else:
            px_val = px_val % 128
            pixels[pos] = (128, 128 - px_val, 128 - px_val)

    image.save(FILE + ".skel.png")

    # invert image (rgba) (TAKEN FROM STACK OVERFLOW)
    if image.mode == 'RGBA':
        r,g,b,a = image.split()
        rgb_image = Image.merge('RGB', (r,g,b))
        inverted_image = ImageOps.invert(rgb_image)
        r2,g2,b2 = inverted_image.split()
        final_transparent_image = Image.merge('RGBA', (r2,g2,b2,a))
        final_transparent_image.save(FILE + '.skel.inverted.png')
    else:
        inverted_image = ImageOps.invert(image)
        inverted_image.save(FILE + '.skel.inverted.png')

    return visited

def find_ridges(im):
    shape_list = defaultdict(list)

    width, height = im.size
    print "DIMENSIONS: %s %s" % (width, height)
    for i, px in enumerate(im.getdata()):
        x = i % width
        y = int(i / width)

        shape = shape_map[(x, y)]

        shape_list[shape].append(((x, y), px))

        # check its neighbor depth delta for that shape...



    pixels = im.load()
    bbox = im.getbbox()

    ridge_list = defaultdict(list)

    for shape_index in shape_list:
        shape = shape_list[shape_index]
        shape.sort(key=lambda px_data: grassfire_map[px_data[0]])
        max_val = shape[-1]
        max_depth = grassfire_map[max_val[0]]

        shape_color = pixels[max_val[0]]
        if shape_color[0] == 0 and shape_color[1] == 0 and shape_color[2] == 0:
            continue

        shape_color = random.randint(0, 56)
        color_idx = random.randint(0, 2)
        color_arr = [0, 0, 0]
        color_arr[color_idx] = shape_color

        is_bg = False

        for px in shape:
            pos = px[0]
            if pos[0] == bbox[0] or pos[1] == bbox[2]:
                is_bg = True
            elif pos[1] == bbox[1] or pos[1] == bbox[3]:
                is_bg = True

        if is_bg:
            continue

        for px in reversed(shape):
            pos = px[0]
            px_depth = grassfire_map[pos]

            x = pos[0]
            y = pos[1]
            left_depth = grassfire_map[(x-1, y)]
            right_depth = grassfire_map[(x+1, y)]

            top_depth = grassfire_map[(x, y-1)]
            bot_depth = grassfire_map[(x, y+1)]

            if not left_depth or not right_depth or not top_depth or not bot_depth:
                continue

            if px_depth < MIN_DIST:
                continue

            is_ridge = False

            if abs(left_depth - right_depth) == 0 and abs(top_depth - bot_depth) == 0:
                color_copy = list(color_arr)
                color_copy[color_idx] += px_depth * 5
                pixels[pos] = tuple(color_copy)
                is_ridge = True

            if abs(left_depth - right_depth) == 1 and abs(top_depth - bot_depth) == 1:
                color_copy = list(color_arr)
                color_copy[color_idx] += px_depth * 5
                pixels[pos] = tuple(color_copy)
                is_ridge = True

            if is_ridge:
                ridge_list[shape_index].append(pos)

    im.save(FILE + ".red.png")
    return ridge_list


def connect_lines(im, ridge_map):
    for shape in ridge_map:
        # TODO: need to join all the points?
        # calculate distance from every pixel to each other...
        ridge_pixels = ridge_map[shape]
        ridge_pixels.sort(key=lambda p: p[0])


        pixels = im.load()
        width, height = im.size
        shape_color = (
            random.randint(0, 128),
            random.randint(0, 128),
            random.randint(0, 128) )

        for px in ridge_map[shape]:
            neighbors = (
                (px[0] + 0, px[1] + 1),
                (px[0] + 1, px[1] + 0),

                (px[0] - 0, px[1] - 1),
                (px[0] - 1, px[1] - 0),

            )

            pixels[px] = shape_color

            for neighbor in neighbors:
                if neighbor[0] < 0 or neighbor[1] < 0:
                    continue

                if neighbor[0] >= width or neighbor[1] >= height:
                    continue

                pixels[neighbor] = shape_color
        shape_fill(im, ridge_map[shape])

            
            
    im.save(FILE + ".blot.png")            





if __name__ == "__main__":
    shape_map = shape_separate(im.copy())
    grassfire_map = grassfire_fill(im.copy())
    ridge_map = find_ridges(im.copy())


   
    connect_lines(im.copy(), ridge_map)
