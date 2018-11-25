from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import cv2
import argparse
import os


intermediateImages = os.path.join('python_scripts', 'mySlant')

if not os.path.exists(intermediateImages):
    os.makedirs(intermediateImages)


parser = argparse.ArgumentParser()
parser.add_argument('--filename', required=True)
parser.add_argument('--ext', required=True)
opt = parser.parse_args()



# Load image and convert it from BGR to RGB
image = cv2.cvtColor(cv2.imread(opt.filename + "." + opt.ext), cv2.COLOR_BGR2RGB)

orig_height = image.shape[1]
orig_width  = image.shape[0]



TOP_LEFT = 0
BOT_LEFT = 1
BOT_RIGHT = 2
TOP_RIGHT = 3



def resize(img, height=800):
    aspect_ratio = img.shape[0] / img.shape[1]
    return cv2.resize(img, (int(height / aspect_ratio), height))



# Resize and convert to grayscale
img = cv2.cvtColor(resize(image), cv2.COLOR_BGR2GRAY)

#     Bilateral filter preserv edges
#     cv2.bilateralFilter(src, d, sigmaColor, sigmaSpace)


cv2.imwrite(os.path.join(intermediateImages, "0_1_before_bilat.jpg"), img)

img = cv2.bilateralFilter(img, 9, 75, 75)

cv2.imwrite(os.path.join(intermediateImages, "0_2_after_bilat.jpg"), img)


# Create black and white image based on adaptive threshold
img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 115, 4)
# # # # # print("POST adaptiveThreshold: ", img.shape)
cv2.imwrite(os.path.join(intermediateImages, "1_adaptiveThreshold.jpg"), img)

# Median filter clears small details
img = cv2.medianBlur(img, 11)

# Add black border in case that page is touching an image border
img = cv2.copyMakeBorder(img, 5, 5, 5, 5, cv2.BORDER_CONSTANT, value=[0, 0, 0])
# # # # # print("POST copyMakeBorder: ", img.shape)
cv2.imwrite(os.path.join(intermediateImages, "2_copyMakeBorder.jpg"), img)

edges = cv2.Canny(img, 200, 250)
# # # # # print("POST Canny: ", edges.shape)
cv2.imwrite(os.path.join(intermediateImages, "3_Canny.jpg"), edges)








# Getting contours  
_, contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
# # # # # print("POST findContours: ", edges.shape)


# # # # # print("contours: ", len(contours))
# 321 contours having L points (e.g. 60) having 2 coordinates (x and y)
# print("hierarchy: ", (hierarchy[0][320][3]))







# Finding contour of biggest rectangle
# Otherwise return corners of original image
# Don't forget on our 5px border!
height = edges.shape[0]
width = edges.shape[1]
MAX_COUNTOUR_AREA = (width - 10) * (height - 10)

# Page fill at least half of image, then saving max area found
maxAreaFound = MAX_COUNTOUR_AREA * 0.5

# Saving page contour
pageContour = np.array([[5, 5], [5, height-5], [width-5, height-5], [width-5, 5]])

# Go through all contours
for cnt in contours:
    # Simplify contour
    perimeter = cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, 0.03 * perimeter, True)

    # Page has 4 corners and it is convex
    # Page area must be bigger than maxAreaFound 
    if (len(approx) == 4 and
            cv2.isContourConvex(approx) and
            maxAreaFound < cv2.contourArea(approx) < MAX_COUNTOUR_AREA):

        maxAreaFound = cv2.contourArea(approx)
        pageContour = approx

# Result in pageConoutr (numpy array of 4 points):







def fourCornersSort(pts):

    # # # # # print("inside fourCornersSort")
    # # # # # print(pts)

    """ Sort corners: top-left, bot-left, bot-right, top-right """
    # Difference and sum of x and y value
    # Inspired by http://www.pyimagesearch.com

    # # diff = np.diff(pts, axis=1)    
    # # summ = pts.sum(axis=1)

    diff = []
    summ = []

    for point in pts:
        point = np.ndarray.flatten(point)
        # # # # # print("POINT: ", point)
        diff = diff + [(point[1] - point[0])]
        summ = summ + [(point[1] + point[0])]

    # # # # # print("diff")
    # # # # # print(diff)

    # # # # # print("summ")
    # # # # # print(summ)
    
    # Top-left point has smallest sum...
    # np.argmin() returns INDEX of min
    return np.array([pts[np.argmin(summ)],
                     pts[np.argmax(diff)],
                     pts[np.argmax(summ)],
                     pts[np.argmin(diff)]])





def contourOffset(cnt, offset):
    """ Offset contour, by 5px border """
    # Matrix addition
    cnt += offset
    
    # if value < 0 => replace it by 0
    cnt[cnt < 0] = 0
    return cnt


# Sort and offset corners

# # # # # print("pageContour")
# # # # # print(pageContour)

# pageContour = fourCornersSort(pageContour[:, 0])
pageContour = fourCornersSort(pageContour)

# # # # # print("pageContour POST fourCornersSort")
# # # # # print(pageContour)


pageContour = contourOffset(pageContour, (-5, -5))

pageContour = np.squeeze(pageContour)

# # # # # print("pageContour POST contourOffset")
# # # # # print(pageContour)



# pageContour = np.array([
#     [10, 141],
#     [83, 781],
#     [596, 642],
#     [439, 102]
# ])


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
