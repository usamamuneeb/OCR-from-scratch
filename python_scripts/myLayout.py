import cv2
import numpy as np
import sys
import queue
import argparse
import os


intermediateImages = os.path.join('python_scripts', 'myLayout')

if not os.path.exists(intermediateImages):
    os.makedirs(intermediateImages)


parser = argparse.ArgumentParser()
parser.add_argument('--filename', required=True)
parser.add_argument('--ext', required=True)
opt = parser.parse_args()





"""
Initial Image Processing
Initial Image Processing
Initial Image Processing
"""




# Reading the input image
img = cv2.imread(opt.filename + "." + opt.ext, 0)
(height, width) = img.shape[:2]
# Taking a matrix of size 5 as the kernel
kernel = np.ones((5, 5), np.uint8)
#gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.bitwise_not(img)






"""
Finer Operations
Finer Operations
Finer Operations
"""






# initial thresholding, setting all foreground pixels to 255 and all background pixels to 0
thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

# post processing on the monochrome image
img_dilation = cv2.dilate(thresh, kernel, iterations=10)
blur = cv2.GaussianBlur(img_dilation, (5, 5), 0)

# threshold once again to make monochrome again
thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
cv2.imwrite(os.path.join(intermediateImages, "0_binary.png"), thresh)







"""
Perform repeated FloodFills
Perform repeated FloodFills
Perform repeated FloodFills
"""

dim_y = thresh.shape[0]
dim_x = thresh.shape[1]



groups = np.zeros((dim_y,dim_x,3)).astype(np.uint8)
groups[:,:,0] = 1 * (thresh > 0)



# plt.imshow(groups[:,:,0])
# plt.show()


TOP_LEFT = 0
TOP_RIGHT = 1
BOTTOM_LEFT = 2
BOTTOM_RIGHT = 3

COORD_R = 0
COORD_C = 1
DIFF_R_C = 2
SUM_R_C = 2


blob_corners = []

MARGIN_LEFT = 0
MARGIN_RIGHT = 1
MARGIN_TOP = 2
MARGIN_BOTTOM = 3

blob_margins = []

def colorFill(r, c):
    global groups
    global blob_id
    global dim_x
    global dim_y
    global blob_corners
    global blob_margins

    L = queue.Queue()
    L.put((r,c))

    while (not L.empty()):
        (r,c) = L.get()

        # groups[r,c,0]                     shows that it requires grouping
        groups[r,c,1] = 1                   # grouped
        groups[r,c,2] = blob_id             # assign group


        # FIND CORNERS
        # FIND CORNERS
        r_c_diff = c-r
        r_c_sum  = c+r

        if (r_c_diff > blob_corners[BOTTOM_LEFT][DIFF_R_C]):
            blob_corners[BOTTOM_LEFT][0:2] = [r,c]
            blob_corners[BOTTOM_LEFT][DIFF_R_C] = r_c_diff

        elif (r_c_diff < blob_corners[TOP_RIGHT][DIFF_R_C]):
            blob_corners[TOP_RIGHT][0:2] = [r,c]
            blob_corners[TOP_RIGHT][DIFF_R_C] = r_c_diff

        elif (r_c_sum > blob_corners[BOTTOM_RIGHT][SUM_R_C]):
            blob_corners[BOTTOM_RIGHT][0:2] = [r,c]
            blob_corners[BOTTOM_RIGHT][SUM_R_C] = r_c_sum

        elif (r_c_sum < blob_corners[TOP_LEFT][SUM_R_C]):
            blob_corners[TOP_LEFT][0:2] = [r,c]
            blob_corners[TOP_LEFT][SUM_R_C] = r_c_sum


        # FIND LEFT, RIGHT, TOP and BOTTOM MARGINS
        # FIND LEFT, RIGHT, TOP and BOTTOM MARGINS
        if (r < blob_margins[MARGIN_TOP]):
            blob_margins[MARGIN_TOP] = r
        elif (r > blob_margins[MARGIN_BOTTOM]):
            blob_margins[MARGIN_BOTTOM]= r
        
        if (c < blob_margins[MARGIN_LEFT]):
            blob_margins[MARGIN_LEFT] = c
        elif (c > blob_margins[MARGIN_RIGHT]):
            blob_margins[MARGIN_RIGHT]= c





        if (r-1 >= 0):
            if (groups[r-1,c,0]==1 and groups[r-1,c,1]==0):
                groups[r-1,c,1] = 1                   # grouped
                groups[r-1,c,2] = blob_id             # assign group
                L.put((r-1,c))
                # print("COLORFILL CALLED 1")

        if (r+1 < dim_y):
            if (groups[r+1,c,0]==1 and groups[r+1,c,1]==0):
                groups[r+1,c,1] = 1                   # grouped
                groups[r+1,c,2] = blob_id             # assign group
                L.put((r+1,c))

        if (c-1 >= 0):
            if (groups[r,c-1,0]==1 and groups[r,c-1,1]==0):
                groups[r,c-1,1] = 1                   # grouped
                groups[r,c-1,2] = blob_id             # assign group
                L.put((r,c-1))

        if (c+1 < dim_x):
            if (groups[r,c+1,0]==1 and groups[r,c+1,1]==0):
                groups[r,c+1,1] = 1                   # grouped
                groups[r,c+1,2] = blob_id             # assign group
                L.put((r,c+1))








# print(groups[900:910,800:810,0])




"""
groups[...,0] = 0 (does not require grouping) and 1 (requires grouping)
groups[...,1] = 0 (ungrouped) and 1 (grouped)
groups[...,2] = 0 (ungrouped) and 1, 2, 3 (grouped)
"""



pixels_require_grouping = np.sum(groups[:,:,0])
grouped_pixels = np.sum(groups[:,:,1])


blob_id = 1



starting_r = None
starting_c = None

foundStartingPixel = False

for r in range(0,dim_y):
    for c in range(0,dim_x):
        if (groups[r,c,0] == 1 and groups[r,c,1] == 0):
            starting_r = r
            starting_c = c
            foundStartingPixel = True
            break
    if foundStartingPixel:
        break


# print("Starting r: %d, Starting c: %d" % (starting_r, starting_c))

# while `those which require grouping` are more than `those grouped`
while (1):

    # print("Starting r: %d, Starting c: %d" % (starting_r, starting_c))
    sys.stdout.flush()


    blob_corners = [
        [starting_r, starting_c, starting_c-starting_r],
        [starting_r, starting_c, starting_c-starting_r],
        [starting_r, starting_c, starting_c+starting_r],
        [starting_r, starting_c, starting_c+starting_r]
    ]

    
    blob_margins = [
        starting_c,
        starting_c,
        starting_r,
        starting_r
    ]


    colorFill(starting_r, starting_c)


    grouped_pixels = np.sum(groups[:,:,1])
    completion = (grouped_pixels * 100) // pixels_require_grouping
    

    print("ITEM_%d_PCNT_%d" % (blob_id, completion))
    # print([corner[0:2] for corner in blob_corners])
    print(blob_margins)
    
    
    # print("ITEM_%d_END" % blob_id)

    cv2.imwrite(os.path.join('python_scripts', 'post_layout.png'), groups[:,:,2] * 40)

    if (np.sum(groups[:,:,0]) == np.sum(groups[:,:,1])):
        break

    blob_id = blob_id + 1

    foundStartingPixel = False

    for r in range(starting_r,dim_y):
        for c in range(0,dim_x):
            if (groups[r,c,0] == 1 and groups[r,c,1] == 0):
                starting_r = r
                starting_c = c
                foundStartingPixel = True
                break
        if foundStartingPixel:
            break


# print("ITEMS_END")