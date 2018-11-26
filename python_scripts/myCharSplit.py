import cv2
import numpy as np
import sys
import queue
import argparse
import os


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
binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
binary_INV = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

cv2.imwrite(os.path.join(intermediateImages, "0_binary.png"), binary_INV)



print("opt.pointsArray")
# print(opt.pointsArray)


finalPoints = []
myItems = opt.pointsArray[1:-1].split('],[')

for item in myItems:
    # print(item)
    finalPoints = finalPoints + [
        [int(numeric_string) for numeric_string in item.split(',')]
    ]


print(finalPoints)

points = finalPoints


def linespliting(coords):
    character = []
    Numberofitems=len(coords)
    rowsplit = []


    for i in range(Numberofitems):
        rowsplit.append([])
        points[i] = list(map(int, points[i]))

    threshold = 240

    for s in range(Numberofitems):

        rowflag = 1


        count = coords[s][1] - coords[s][0] # these are the number of pixels (right - left) of each row
        
        # ITERATE FROM TOP "coords[s][2]" TO THE BOTTOM "coords[s][3]" OF THE BLOCK
        for i in range(coords[s][2], coords[s][3]):
            
            sum = 0 # initialize the sum of pixels to 0 for every row

            
            # SUM UP THE VALUES OF THIS ROW
            sum = np.sum(binary[i])
            

            #print(sum / count)
            if sum / count > threshold and rowflag == 0:
                continue
            elif sum / count > threshold and rowflag == 1:  # just get out of the block
                rowsplit[s].append(i)
                rowflag = 0
                cv2.line(output, (coords[s][0], i), (coords[s][1], i), (0, 0, 0), 1)
                continue
            elif sum / count <= threshold and rowflag == 0:  # just get into the block
                rowsplit[s].append(i)
                rowflag = 1
                cv2.line(output, (coords[s][0], i), (coords[s][1], i), (0, 0, 0), 1)
                continue
            else:
                continue



    # MAKE A RECTANGLE AROUND THIS BLOCK
    for i in range(Numberofitems):
        cv2.rectangle(output, (coords[i][0], coords[i][2]),
                      (coords[i][1], coords[i][3]), 3)



    # CHARACTER SPLITTING
    for s in range(Numberofitems):
        splitnum=len(rowsplit[s])
        for k in range(splitnum-1):
            colflag = 1
            tempcol=[]
            for i in range(coords[s][0], coords[s][1]):
                summ = 0
                countt = rowsplit[s][k+1] - rowsplit[s][k]
                for j in range(rowsplit[s][k], rowsplit[s][k+1]):
                    summ = summ + binary[j][i]
                # print(sum / count)
                if summ / countt > threshold and colflag == 0:
                    continue
                elif summ / countt > threshold and colflag == 1:  # just get out of the block
                    #rowsplit[s].append(i)
                    colflag = 0
                    cv2.line(output, (i,rowsplit[s][k]), (i,rowsplit[s][k+1]), (0, 0, 0), 1)
                    continue
                elif summ / countt <= threshold and colflag == 0:  # just get into the block
                    #rowsplit[s].append(i)
                    colflag = 1
                    cv2.line(output, (i,rowsplit[s][k]), (i,rowsplit[s][k+1]), (0, 0, 0), 1)
                    continue
                else:
                    continue
    #return rowsplit
    cv2.imwrite(os.path.join(intermediateImages, "1_output.png"), output)

linespliting(points)