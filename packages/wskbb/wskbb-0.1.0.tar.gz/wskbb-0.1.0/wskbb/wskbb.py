# -*- coding: utf-8 -*-

__version__ = "0.1.0"

import cv2
import sys 
from matplotlib import pyplot as plt
import bisect
import scipy.spatial
import numpy as np
import random
import math
from .utils import regulate, limit_size, clipped_addition, kMeansImage, VectorField, ColorPalette
import argparse

parser = argparse.ArgumentParser(description='...')
parser.add_argument('--model', default='papin', type=str, help="Model output. Isikan dengan: papin atau botol")
parser.add_argument('img_path', nargs='?')

args = parser.parse_args()

def color_probs(pixels, palette, k=9):
    distances = scipy.spatial.distance.cdist(pixels, palette.colors)
    maxdist = np.amax(distances, axis=1)
    distances = maxdist[:, None] - distances
    smry = np.sum(distances, 1)
    distances /= smry[:, None]
    distances = np.exp(k*len(palette)*distances)
    smry = np.sum(distances, 1)
    distances /= smry[:, None]
    return np.cumsum(distances, axis=1, dtype=np.float32)


def color_select(probabilities, palette):
    r = random.uniform(0, 1)
    i = bisect.bisect_left(probabilities, r)
    return palette[i] if i < len(palette) else palette[-1]

def randomized_grid(h, w, scale):
    assert (scale > 0)
    r = scale//2
    grid = []
    for i in range(0, h, scale):
        for j in range(0, w, scale):
            y = random.randint(-r, r) + i
            x = random.randint(-r, r) + j
            grid.append((y % h, x % w))
    random.shuffle(grid)
    return grid

def pointilize(img, grayImage):
    stroke_scale = int(math.ceil(max(img.shape) / 1000))
    gradient_smoothing_radius = int(round(max(img.shape) / 50))
    palette = ColorPalette.from_image(grayImage, 20)
    palette = palette.extend([(0, 50, 0), (15, 30, 0), (-15, 30, 0)])

    gradient = VectorField.from_gradient(grayImage)
    gradient.smooth(gradient_smoothing_radius)
    res = cv2.medianBlur(img, 11)
    grid = randomized_grid(img.shape[0], img.shape[1], scale=3)
    batch_size = 10000
    for h in range(0, len(grid), batch_size):
        pixels = np.array([img[x[0], x[1]] for x in grid[h:min(h + batch_size, len(grid))]])
        color_prob = color_probs(pixels, palette, k=9)

        for i, (y, x) in enumerate(grid[h:min(h + batch_size, len(grid))]):
            color = color_select(color_prob[i], palette)
            angle = math.degrees(gradient.direction(y, x)) + 90
            length = int(round(stroke_scale + stroke_scale * math.sqrt(gradient.magnitude(y, x))))
            cv2.ellipse(res, (x, y), (length, stroke_scale), angle, 0, 360, color, -1, cv2.LINE_AA)
    return res 


path = args.img_path
if not path:
    print('masukkan path image dan model yang dipilih. contoh: python main.py /path/image.jpg --model=papin')
    sys.exit()

def main():
    img = cv2.imread(path)
    number_of_black_pix = np.sum(img == 0)
    fig = plt.figure(figsize=(18,6))
    ax  = fig.add_subplot(1,1,1)

    if args.model == 'papin':
        if number_of_black_pix > 2000:
            lab= cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            l_channel, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=12.0, tileGridSize=(10,10))
            cl = clahe.apply(l_channel)
            limg = cv2.merge((cl,a,b))
            img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        grayImage = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        try:
            res = pointilize(img,grayImage)
        except:
            res = cv2.cvtColor(grayImage, cv2.COLOR_GRAY2BGR)  

        img  = kMeansImage(res,6)
        grayImage = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        (thresh, blackAndWhiteImage) = cv2.threshold(grayImage, 127, 255, cv2.THRESH_BINARY)
        ax.imshow(blackAndWhiteImage, cmap='gray')
    elif args.model == 'botol':
        if number_of_black_pix > 2000:
            lab= cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            l_channel, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=12.0, tileGridSize=(8,8))
            cl = clahe.apply(l_channel)
            limg = cv2.merge((cl,a,b))
            img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        res = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img  = kMeansImage(res,5)
        ax.imshow(img)
    plt.axis('off')
    result = path.rsplit(".", -1)[0] + "_drawing_%s.jpg" % (args.model,)
    plt.savefig(result, bbox_inches='tight',pad_inches = 0)
    print('Image berhasil disimpan di: %s' % (result,))

