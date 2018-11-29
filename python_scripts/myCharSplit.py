import cv2
import numpy as np
import sys
import queue
import argparse
import os
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


SMOOTHING_KERNEL_LENGTH = 9
SMOOTHING_KERNEL_LENGTH_COLS = 1

IDX_LEFT = 0
IDX_RIGHT = 1
IDX_TOP = 2
IDX_BOTTOM = 3



intermediateImages = os.path.join('python_scripts', 'myCharSplit')

if not os.path.exists(intermediateImages):
    os.makedirs(intermediateImages)


parser = argparse.ArgumentParser()
parser.add_argument('--filename', required=True)
parser.add_argument('--ext', required=True)
parser.add_argument('--pointsArray', required=True)
opt = parser.parse_args()





img = cv2.imread(opt.filename + "." + opt.ext, 0)


output=img
binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

cv2.imwrite(os.path.join(intermediateImages, "0_binary.png"), binary)



# print("\n\nopt.pointsArray from command line arguments")


finalPoints = []
myItems = opt.pointsArray[1:-1].split('],[')

for item in myItems:
    finalPoints = finalPoints + [
        [int(numeric_string) for numeric_string in item.split(',')]
    ]


# print(finalPoints)



f = open("demofile.csv", "w")


numClipped = 1


clippedCharacters = []

for (idx, block) in enumerate(finalPoints):
    clippedBlockCharacters = []

    blockRows = []

    
    # ITERATE FROM TOP "block[2]" TO THE BOTTOM "block[3]" OF THE BLOCK
    for i in range(block[IDX_TOP], block[IDX_BOTTOM]):

        # SUM UP THE VALUES OF EACH (i'th) ROW
        sum = np.sum(binary[i])
        blockRows.append(sum)

    smoothing_kernel = np.ones(SMOOTHING_KERNEL_LENGTH) / SMOOTHING_KERNEL_LENGTH

    blockRows = np.convolve(blockRows, smoothing_kernel, 'valid')


    minSum = np.min(blockRows)
    maxSum = np.max(blockRows)

    centerLine = (minSum + maxSum) // 2




    blockRows_Binary = [1 if rowSum < centerLine else 0 for rowSum in blockRows]
    blockRows_Binary = np.concatenate((np.ones(SMOOTHING_KERNEL_LENGTH//2), blockRows_Binary, np.ones(SMOOTHING_KERNEL_LENGTH//2)), axis=0)



    betweenLines = False
    startingRow = 0
    endingRow = 0

    cuttingLines = []


    for (idx, rowBinaryVal) in enumerate(blockRows_Binary):
        if (rowBinaryVal==1 and betweenLines == False):
                betweenLines = True
                startingRow = idx
        if (rowBinaryVal==0 and betweenLines == True):
                betweenLines = False
                endingRow = idx

                # cuttingLines = cuttingLines + [ ((endingRow + startingRow) // 2) ]
                cuttingLines = cuttingLines + [ ((endingRow + startingRow) // 2) + block[IDX_TOP] ]

    cuttingLines = cuttingLines + [block[IDX_BOTTOM]]






    # ITERATE OVER ROWS FROM 1st to END, LEAVE END for else
    for (idx_col, cuttingLine) in enumerate(cuttingLines):
        if (idx_col < len(cuttingLines)-1):
            cv2.line(output, (block[IDX_LEFT], cuttingLine), (block[IDX_RIGHT], cuttingLine), (255, 0, 0), 1)
        else:
            cv2.line(output, (block[IDX_LEFT], cuttingLine), (block[IDX_RIGHT], cuttingLine), (0, 0, 0), 1)



    """ FOR EACH LINE, WE WILL NOW SPLIT THE CHARACTERS """
    """ FOR EACH LINE, WE WILL NOW SPLIT THE CHARACTERS """
    """ FOR EACH LINE, WE WILL NOW SPLIT THE CHARACTERS """
    """ FOR EACH LINE, WE WILL NOW SPLIT THE CHARACTERS """


    # ITERATE OVER ROWS FROM 1st to END, LEAVE END for else
    for (idx_col, cuttingLine) in enumerate(cuttingLines):

        if (idx_col < len(cuttingLines)-1):


            blockCols = []

            # ITERATE FROM LEFT "block[0]" TO THE RIGHT "block[1]" OF THE LINE
            for i in range(block[IDX_LEFT], block[IDX_RIGHT]):

                # SUM UP THE VALUES OF EACH (i'th) COL from TOP to BOTTOM
                sum = np.sum(binary[cuttingLines[idx_col]:cuttingLines[idx_col+1],i])
                blockCols.append(sum)



            smoothing_kernel_cols = np.ones(SMOOTHING_KERNEL_LENGTH_COLS) / SMOOTHING_KERNEL_LENGTH_COLS


            blockCols = np.convolve(blockCols, smoothing_kernel_cols, 'valid')

            minSum = np.min(blockCols)
            maxSum = np.max(blockCols)

            # centerLine = (minSum + maxSum) // 2
            centerLine = np.percentile(blockCols, 30)

            blockCols_Binary = [1 if colSum < centerLine else 0 for colSum in blockCols]
            blockCols_Binary = np.concatenate((np.ones(SMOOTHING_KERNEL_LENGTH_COLS//2), blockCols_Binary, np.ones(SMOOTHING_KERNEL_LENGTH_COLS//2)), axis=0)


            for colBinaryVal in blockCols_Binary:
                f.write(str(colBinaryVal) + "\n")


            betweenChars = False
            startingCol = 0
            endingCol = 0








            cuttingLinesChars = []


            for (idx, colBinaryVal) in enumerate(blockCols_Binary):
                if (colBinaryVal==1 and betweenChars == False):
                        betweenChars = True
                        startingCol = idx

                        cuttingLinesChars = cuttingLinesChars + [ startingCol + block[IDX_LEFT] ]
                if (colBinaryVal==0 and betweenChars == True):
                        betweenChars = False
                        endingCol = idx

                        cuttingLinesChars = cuttingLinesChars + [ endingCol + block[IDX_LEFT] ]
                        # cuttingLinesChars = cuttingLinesChars + [ ((endingCol + startingCol) // 2) + block[IDX_LEFT] ]

            cuttingLinesChars = cuttingLinesChars + [block[IDX_RIGHT]]

            # print(len(cuttingLinesChars))





            for (idx_col_draw, cuttingLineChar) in enumerate(cuttingLinesChars):

                # draw lines
                if (idx_col_draw < len(cuttingLinesChars)-1):
                    cv2.line(output, (cuttingLineChar, cuttingLines[idx_col]), (cuttingLineChar, cuttingLines[idx_col+1]), (255, 0, 0), 1)
                else:
                    cv2.line(output, (cuttingLineChar, cuttingLines[idx_col]), (cuttingLineChar, cuttingLines[idx_col+1]), (0, 0, 0), 1)

                # store images for neural network
                if (idx_col_draw == 0):
                    leftMargin = block[IDX_LEFT]
                else:
                    leftMargin = cuttingLinesChars[idx_col_draw-1]

                rightMargin = cuttingLinesChars[idx_col_draw]
                topMargin = cuttingLines[idx_col]
                bottomMargin = cuttingLines[idx_col+1]

                width = rightMargin - leftMargin
                height = bottomMargin - topMargin

                aspectRatio = height / width if width > 0 else 0

                if (width > 0 and height > 0 and aspectRatio > 0.22 and aspectRatio < 4.5):
                    clippedImage = binary[topMargin:bottomMargin, leftMargin:rightMargin]
                    clippedImage_1 = clippedImage.astype(np.uint8)
                    clippedImage_1[clippedImage_1 > 0] = 1

                    whitePercentage = np.sum(clippedImage_1)
                    whitePercentage = whitePercentage / (width * height)

                    # print(type(clippedImage))
                    # print(whitePercentage)

                    if (whitePercentage > 0.05):
                        mask = clippedImage_1
                        clippedImage_cropped = clippedImage_1[np.ix_(mask.any(1),mask.any(0))]
                        
                        clippedImage_cropped = Image.fromarray(clippedImage_cropped)
                        clippedImage_cropped = clippedImage_cropped.resize((28,28), Image.ANTIALIAS)
                        clippedImage_cropped = np.array(clippedImage_cropped).astype(np.uint8)

                        # kernel = np.ones((1,1), np.uint8)
                        # clippedImage = cv2.erode(clippedImage_cropped, kernel, iterations=1)

                        clippedImage = clippedImage_cropped

                        clippedImage[clippedImage > 0] = 255


                        # # cv2.imwrite(os.path.join(intermediateImages, "clipped", str(numClipped) + "_" + str(whitePercentage) + ".png"), clippedImage)
                        # cv2.imwrite(os.path.join(intermediateImages, "clipped", str(numClipped) + ".png"), clippedImage)

                        clippedBlockCharacters = clippedBlockCharacters + [clippedImage_cropped]
                    else:
                        # # cv2.imwrite(os.path.join(intermediateImages, "clipped", str(numClipped) + "_" + str(whitePercentage) + ".png"), np.zeros((48,48)))
                        # cv2.imwrite(os.path.join(intermediateImages, "clipped", str(numClipped) + ".png"), np.zeros((48,48)))

                        clippedBlockCharacters = clippedBlockCharacters + ['*']


                    numClipped = numClipped + 1

    clippedCharacters = clippedCharacters + [clippedBlockCharacters]


# for sentence in clippedCharacters:
#     print(len(sentence))
#     for char in sentence:
#         print(type(char))


np.save(os.path.join('python_scripts', 'postSplit'), clippedCharacters)



# # MAKE A RECTANGLE AROUND THIS BLOCK
# for (idx, block) in enumerate(finalPoints):
#     cv2.rectangle(output,  (block[0], block[2]),  (block[1], block[3]), 3)







#return rowsplit
cv2.imwrite(os.path.join(intermediateImages, "1_output.png"), output)
