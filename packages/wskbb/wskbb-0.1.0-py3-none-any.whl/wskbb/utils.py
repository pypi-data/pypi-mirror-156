import skimage
from sklearn.cluster import KMeans
from numpy import linalg as LA
import numpy as np
import cv2
from matplotlib import pyplot as plt
import math

def pixelate(img, w, h):
    height, width = img.shape[:2]

    # Resize input to "pixelated" size
    temp = cv2.resize(img, (w, h), interpolation=cv2.INTER_LINEAR)

    # Initialize output image
    return cv2.resize(temp, (width, height), interpolation=cv2.INTER_NEAREST)

def colorClustering(idx, img, k):
    clusterValues = []
    for _ in range(0, k):
        clusterValues.append([])
    
    for r in range(0, idx.shape[0]):
        for c in range(0, idx.shape[1]):
            clusterValues[idx[r][c]].append(img[r][c])

    imgC = np.copy(img)

    clusterAverages = []
    for i in range(0, k):
        clusterAverages.append(np.average(clusterValues[i], axis=0))
    
    for r in range(0, idx.shape[0]):
        for c in range(0, idx.shape[1]):
            imgC[r][c] = clusterAverages[idx[r][c]]
            
    return imgC

def segmentImgClrRGB(img, k):
    
    imgC = np.copy(img)
    
    h = img.shape[0]
    w = img.shape[1]
    
    imgC.shape = (img.shape[0] * img.shape[1], 3)
    
    #5. Run k-means on the vectorized responses X to get a vector of labels (the clusters); 
    #  
    kmeans = KMeans(n_clusters=k, random_state=0).fit(imgC).labels_
    
    #6. Reshape the label results of k-means so that it has the same size as the input image
    #   Return the label image which we call idx
    kmeans.shape = (h, w)

    return kmeans

def kMeansImage(image, k):
    idx = segmentImgClrRGB(image, k)
    return colorClustering(idx, image, k)


def limit_size(img, max_x, max_y=0):
    if max_x == 0:
        return img

    if max_y == 0:
        max_y = max_x

    ratio = min(1.0, float(max_x) / img.shape[1], float(max_y) / img.shape[0])

    if ratio != 1.0:
        shape = (int(img.shape[1] * ratio), int(img.shape[0] * ratio))
        return cv2.resize(img, shape, interpolation=cv2.INTER_AREA)
    else:
        return img


def clipped_addition(img, x, _max=255, _min=0):
    if x > 0:
        mask = img > (_max - x)
        img += x
        np.putmask(img, mask, _max)
    if x < 0:
        mask = img < (_min - x)
        img += x
        np.putmask(img, mask, _min)


def regulate(img, hue=0, saturation=0, luminosity=0):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV_FULL)
    if hue < 0:
        hue = 255 + hue
    hsv[:, :, 0] += hue
    clipped_addition(hsv[:, :, 1], saturation)
    clipped_addition(hsv[:, :, 2], luminosity)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR_FULL)


class ColorPalette:
    def __init__(self, colors, base_len=0):
        self.colors = colors
        self.base_len = base_len if base_len > 0 else len(colors)

    @staticmethod
    def from_image(img, n, max_img_size=200, n_init=10):
        # scale down the image to speedup kmeans
        img = limit_size(img, max_img_size)

        clt = KMeans(n_clusters=n, n_init=n_init)
        try:
            clt.fit(img.reshape(-1, 3))
        except:
            clt.fit(img.reshape(-1, 1))

        return ColorPalette(clt.cluster_centers_)

    def extend(self, extensions):
        extension = [regulate(self.colors.reshape((1, len(self.colors), 3)).astype(np.uint8), *x).reshape((-1, 3)) for x
                     in
                     extensions]

        return ColorPalette(np.vstack([self.colors.reshape((-1, 3))] + extension), self.base_len)

    def to_image(self):
        cols = self.base_len
        rows = int(math.ceil(len(self.colors) / cols))

        res = np.zeros((rows * 80, cols * 80, 3), dtype=np.uint8)
        for y in range(rows):
            for x in range(cols):
                if y * cols + x < len(self.colors):
                    color = [int(c) for c in self.colors[y * cols + x]]
                    cv2.rectangle(res, (x * 80, y * 80), (x * 80 + 80, y * 80 + 80), color, -1)

        return res

    def __len__(self):
        return len(self.colors)

    def __getitem__(self, item):
        return self.colors[item]

class VectorField:
    def __init__(self, fieldx, fieldy):
        self.fieldx = fieldx
        self.fieldy = fieldy

    @staticmethod
    def from_gradient(gray):
        fieldx = cv2.Scharr(gray, cv2.CV_32F, 1, 0) / 15.36
        fieldy = cv2.Scharr(gray, cv2.CV_32F, 0, 1) / 15.36

        return VectorField(fieldx, fieldy)

    def get_magnitude_image(self):
        res = np.sqrt(self.fieldx**2 + self.fieldy**2)
        
        return (res * 255/np.max(res)).astype(np.uint8)

    def smooth(self, radius, iterations=1):
        s = 2*radius + 1
        for _ in range(iterations):
            self.fieldx = cv2.GaussianBlur(self.fieldx, (s, s), 0)
            self.fieldy = cv2.GaussianBlur(self.fieldy, (s, s), 0)

    def direction(self, i, j):
        return math.atan2(self.fieldy[i, j], self.fieldx[i, j])

    def magnitude(self, i, j):
        return math.hypot(self.fieldx[i, j], self.fieldy[i, j])