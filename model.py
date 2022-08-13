# -*- coding: utf-8 -*-
"""round2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/12PxlBHq-n6p0yWZtmYQHD9lP3WBVZgra
"""

import cv2
# from google.colab.patches import cv2_imshow
from keras.models import load_model

import cv2 
import numpy as np 
import scipy.fftpack 

def clearborder(imgBW, radius):

    imgBWcopy = imgBW.copy()
    contours,hierarchy = cv2.findContours(imgBWcopy.copy(), cv2.RETR_LIST, 
        cv2.CHAIN_APPROX_SIMPLE)

    imgRows = imgBW.shape[0]
    imgCols = imgBW.shape[1]    

    contourList = [] 

    for idx in np.arange(len(contours)):
        
        cnt = contours[idx]

        
        for pt in cnt:
            rowCnt = pt[0][1]
            colCnt = pt[0][0]

            check1 = (rowCnt >= 0 and rowCnt < radius) or (rowCnt >= imgRows-1-radius and rowCnt < imgRows)
            check2 = (colCnt >= 0 and colCnt < radius) or (colCnt >= imgCols-1-radius and colCnt < imgCols)

            if check1 or check2:
                contourList.append(idx)
                break

    for idx in contourList:
        cv2.drawContours(imgBWcopy, contours, idx, (0,0,0), -1)

    return imgBWcopy


def areaopen(imgBW, areaPixels):

    imgBWcopy = imgBW.copy()
    contours,hierarchy = cv2.findContours(imgBWcopy.copy(), cv2.RETR_LIST, 
        cv2.CHAIN_APPROX_SIMPLE)

    for idx in np.arange(len(contours)):
        area = cv2.contourArea(contours[idx])
        if (area >= 0 and area <= areaPixels):
            cv2.drawContours(imgBWcopy, contours, idx, (0,0,0), -1)

    return imgBWcopy


def mos(img,t):
    img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    rows = img.shape[0]
    cols = img.shape[1]

    imgLog = np.log1p(np.array(img, dtype="float") / 255)

    M = 2*rows + 1
    N = 2*cols + 1
    sigma = 10
    (X,Y) = np.meshgrid(np.linspace(0,N-1,N), np.linspace(0,M-1,M))
    centerX = np.ceil(N/2)
    centerY = np.ceil(M/2)
    gaussianNumerator = (X - centerX)**2 + (Y - centerY)**2

    Hlow = np.exp(-gaussianNumerator / (2*sigma*sigma))
    Hhigh = 1 - Hlow

    HlowShift = scipy.fftpack.ifftshift(Hlow.copy())
    HhighShift = scipy.fftpack.ifftshift(Hhigh.copy())

    If = scipy.fftpack.fft2(imgLog.copy(), (M,N))
    Ioutlow = np.real(scipy.fftpack.ifft2(If.copy() * HlowShift, (M,N)))
    Iouthigh = np.real(scipy.fftpack.ifft2(If.copy() * HhighShift, (M,N)))

    gamma1 = 0.3
    gamma2 = 1.5
    Iout = gamma1*Ioutlow[0:rows,0:cols] + gamma2*Iouthigh[0:rows,0:cols]

    Ihmf = np.expm1(Iout)
    Ihmf = (Ihmf - np.min(Ihmf)) / (np.max(Ihmf) - np.min(Ihmf))
    Ihmf2 = np.array(255*Ihmf, dtype="uint8")

    Ithresh = Ihmf2 < t
    Ithresh = 255*Ithresh.astype("uint8")

    Iclear = clearborder(Ithresh, 5)

    Iopen = areaopen(Iclear, 50)

    # cv2.imshow('Original Image', img)
    # cv2.imshow('Homomorphic Filtered Result', Ihmf2)
    # cv2.imshow('Thresholded Result', Ithresh)
    # cv2.imshow('Opened Result', Iopen)

    return Iopen
   
def edited(img):
    imge = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    imge = cv2.medianBlur(imge,5)
    # _,imge = cv2.threshold(imge,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    imge = cv2.adaptiveThreshold(imge,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,49,2)

    # _,imge = cv2.threshold(imge,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    
    # cv2.imshow('at',imge)
    imge = cv2.bitwise_not(imge)
    # imge = cv2.equalizeHist(imge)
    kernel = np.ones((3,3),np.uint8)
    # imge = cv2.dilate(imge,kernal,iterations=1)
    imge = cv2.erode(imge,kernel,iterations=1)
    kernel = np.ones((1,1),np.uint8)
    imge = cv2.erode(imge,kernel,iterations=1)
    
    # cv2.imshow('fi',imge)
    # imge = bwareaopen(imge,100)
    # cv2.imshow('fiii',imge)
    return imge


def segment(img,t):
    images = []
    ct = 0
    imb = img.copy()
    img = mos(img,t)
    kernel = np.ones((1,1),np.uint8)
    img = cv2.morphologyEx(img,cv2.MORPH_OPEN,kernel)
    # cv2.imshow('morph',img)

    contours,_ = cv2.findContours(img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    sorted_c = sorted(contours, key = lambda contours :cv2.boundingRect(contours[0]))

    # for i,cnt in enumerate(sorted_c):
        # cv2.drawContours(imb, contours, -1, (0, 0, 255), 2)
    img_area = img.shape[0]*img.shape[1]
    #print(img_area)
    for i,cnt in enumerate(sorted_c):
        x,y,w,h = cv2.boundingRect(cnt)
        AREA = cv2.contourArea(cnt)
        area = w*h
        # print(area)
        
        if area<200 or AREA<40 or area>0.5*img_area or w>30 or h/w > 8:
            continue
        #print(area)
        #print(w,h)
        # cv2.rectangle(imb,(x,y),(x+w,y+h),(0,255,0),2)
        imf = imb[y:y+h,x:x+w,:]
        # imf = cv2.resize(imf,(64,64))
        # cv2.imshow('imf',imf)
        images.append(imf)
        ct+=1
    # cv2.imshow('img',img)   
    # cv2.imshow('imge',imb)
    return images,ct,img

def dev(img):
    t = 90
    images,ct,im0 = segment(img,t)
    # print(ct)
    if ct == 10:
        #cv2.imshow('Iop0',im0)
        return images
    else:
        i1,c1,im1 = segment(img,80)
        i2,c2,im2 = segment(img,70)
        i3,c3,im3 = segment(img,60)
        i4,c4,im4 = segment(img,100)
        i5,c5,im5 = segment(img,110)

        dic = {c1:i1, c2:i2, c3:i3, c4:i4, c5:i5, ct:images}
        dic2 = {c1:im1, c2:im2, c3:im3, c4:im4, c5:i5, ct:im0}
        lst = [ct,c1,c2,c3,c4,c5]
        lst.sort(reverse=True)

        for c in lst:
            if c<=10:
                #cv2.imshow('Iop1',dic2[c])
                return dic[c]
        return images

#if __name__ == "__main__":

def pred(img):

    # img = cv2.imread('a0.png')
    img = cv2.resize(img,(300,100))
    #cv2.imshow('orig',img)

    # images = segment(img)
    images = dev(img)
    segmented = []
    for i,img in enumerate(images):
        img = edited(img)
        img = cv2.copyMakeBorder(img,10,10,30,30,cv2.BORDER_CONSTANT,value=[0,0,0])
        img = cv2.resize(img,(28,28))
        segmented.append(img)
        # print(img.shape)
        #cv2.imshow('char'+str(i),img)

    return segmented

dicte = {0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: 'A', 11: 'B', 12: 'C',
         13: 'D', 14: 'E', 15: 'F', 16: 'G', 17: 'H', 18: 'I', 19: 'J', 20: 'K', 21: 'L', 22: 'M', 23: 'N', 24: 'O',
         25: 'P', 26: 'Q', 27: 'R', 28: 'S', 29: 'T', 30: 'U', 31: 'V', 32: 'W', 33: 'X', 34: 'Y', 35: 'Z'}

import keras
import keras.utils

model = keras.models.load_model('model1.h5')

def filter(lst):
  if len(lst) != 10:
    return lst
  else:
    # print(len(lst))
    for i in range(0,len(lst)):
      if i==0 or i==1 or i==4 or i==5:
        if lst[i] == '0':
          lst[i] = 'O'
        elif lst[i] == '1':
          lst[i] = 'I'
        elif lst[i] == '2':
          lst[i] = 'Z'
        elif lst[i] == '3':
          lst[i] = 'B'
        elif lst[i] == '4':
          lst[i] = 'A'
        elif lst[i] == '5':
          lst[i] = 'S'
        elif lst[i] == '6':
          lst[i] = 'G'
        elif lst[i] == '7':
          lst[i] = 'Z'
        elif lst[i] == '8':
          lst[i] = 'B'
        elif lst[i] == '9':
          lst[i] = 'Q'
      else:
        if lst[i] == 'A':
          lst[i] = '4'
        elif lst[i] == 'B':
          lst[i] = '3'
        elif lst[i] == 'C':
          lst[i] = '0'
        elif lst[i] == 'D':
          lst[i] = '0'
        elif lst[i] == 'E':
          lst[i] = '6'
        elif lst[i] == 'F':
          lst[i] = '?'
        elif lst[i] == 'G':
          lst[i] = '6'
        elif lst[i] == 'H':
          lst[i] = '?'
        elif lst[i] == 'I':
          lst[i] = '1'
        elif lst[i] == 'J':
          lst[i] = '1'
        elif lst[i] == 'K':
          lst[i] = '?'
        elif lst[i] == 'L':
          lst[i] = '1'
        elif lst[i] == 'M':
          lst[i] = '?'
        elif lst[i] == 'N':
          lst[i] = '?'
        elif lst[i] == 'O':
          lst[i] = '0'
        elif lst[i] == 'P':
          lst[i] = '?'
        elif lst[i] == 'Q':
          lst[i] = '0'
        elif lst[i] == 'R':
          lst[i] = '?'
        elif lst[i] == 'S':
          lst[i] = '5'
        elif lst[i] == 'T':
          lst[i] = '1'
        elif lst[i] == 'U':
          lst[i] = '0'
        elif lst[i] == 'V':
          lst[i] = '?'
        elif lst[i] == 'W':
          lst[i] = '?'
        elif lst[i] == 'X':
          lst[i] = '8'
        elif lst[i] == 'Y':
          lst[i] = '4'
        elif lst[i] == 'Z':
          lst[i] = '7'
  
    return lst

img = cv2.imread('a0.png')
lp = img.copy()
# cv2_imshow(img)
images = pred(img)

ans = []
# cv2_imshow(img)
for img in images:
  # cv2_imshow(img)
  a = np.argmax(model.predict(img.reshape(1,28,28,1)))
  ans.append(dicte[a])

print(ans)

fin_ans = filter(ans)
# print(len(ans))
print(fin_ans)

# cv2_imshow(lp)
j = 0
print("LICENSE PLATE")
for e in fin_ans:
  print(e,end=' ')
  j+=1
  if j==2 or j==4 or j==6:
    print('', end=' ')
