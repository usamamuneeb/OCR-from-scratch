from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import cv2
import argparse
import os



parser = argparse.ArgumentParser()
parser.add_argument('--filename', required=True)
parser.add_argument('--ext', required=True)

parser.add_argument('--a1', type=int, required=True)
parser.add_argument('--a2', type=int, required=True)
parser.add_argument('--b1', type=int, required=True)
parser.add_argument('--b2', type=int, required=True)
parser.add_argument('--c1', type=int, required=True)
parser.add_argument('--c2', type=int, required=True)
parser.add_argument('--d1', type=int, required=True)
parser.add_argument('--d2', type=int, required=True)
opt = parser.parse_args()



# Load image and convert it from BGR to RGB
image = cv2.cvtColor(cv2.imread(opt.filename + "." + opt.ext), cv2.COLOR_BGR2RGB)

orig_height = image.shape[1]
orig_width  = image.shape[0]





pageContour = np.array([
    [opt.a1, opt.a2],
    [opt.b1, opt.b2],
    [opt.c1, opt.c2],
    [opt.d1, opt.d2]
])

diff = []
summ = []

for p in pageContour:
	diff = diff + [(p[1]-p[0])]
	summ = summ + [(p[1]+p[0])]

pageContour = np.array([
	pageContour[np.argmin(summ)],
	pageContour[np.argmax(diff)],
	pageContour[np.argmax(summ)],
	pageContour[np.argmin(diff)]
])

# # # # # print("pageContour MANUAL")
# # # # # print(pageContour)


# Recalculate to original scale - start Points
sPoints = pageContour.dot(image.shape[0] / 800)


# orig_height = image.shape[0]
# orig_width = image.shape[1]



for pts in sPoints:
    if pts[0] < 0:
        pts[0] = 0
    if pts[0] >= orig_height:
        pts[0] = orig_height - 1

    if pts[1] < 0:
        pts[1] = 0
    if pts[1] >= orig_width:
        pts[1] = orig_width - 1



# Using Euclidean distance
# Calculate maximum height (maximal length of vertical edges) and width
height = max(np.linalg.norm(sPoints[0] - sPoints[1]),
             np.linalg.norm(sPoints[2] - sPoints[3]))
width = max(np.linalg.norm(sPoints[1] - sPoints[2]),
             np.linalg.norm(sPoints[3] - sPoints[0]))

# Create target points
tPoints = np.array([[0, 0],
                    [0, height],
                    [width, height],
                    [width, 0]], np.float32)

# getPerspectiveTransform() needs float32
if sPoints.dtype != np.float32:
    sPoints = sPoints.astype(np.float32)

# Wraping perspective
M = cv2.getPerspectiveTransform(sPoints, tPoints) 
newImage = cv2.warpPerspective(image, M, (int(width), int(height)))

# Saving the result. Yay! (don't forget to convert colors bact to BGR)
cv2.imwrite(os.path.join('python_scripts', 'post_skew.png'), cv2.cvtColor(newImage, cv2.COLOR_BGR2RGB))

print("%d,%d %d,%d %d,%d %d,%d" % (
    pageContour.astype(np.int)[0][0], pageContour.astype(np.int)[0][1],
    pageContour.astype(np.int)[1][0], pageContour.astype(np.int)[1][1],
    pageContour.astype(np.int)[2][0], pageContour.astype(np.int)[2][1],
    pageContour.astype(np.int)[3][0], pageContour.astype(np.int)[3][1]
))
