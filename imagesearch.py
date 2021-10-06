import cv2
import numpy as np
import pyautogui
import random
import time
import platform
import subprocess
import os
import mss

# Added imports for image scale detection changes.
import imutils


is_retina = False
if platform.system() == "Darwin":
    is_retina = subprocess.call("system_profiler SPDisplaysDataType | grep 'retina'", shell=True) == 0

'''

grabs a region (topx, topy, bottomx, bottomy)
to the tuple (topx, topy, width, height)

input : a tuple containing the 4 coordinates of the region to capture

output : a PIL image of the area selected.

'''


def region_grabber(region):
    if is_retina: region = [n * 2 for n in region]
    x1 = region[0]
    y1 = region[1]
    width = region[2] - x1
    height = region[3] - y1

    region = x1, y1, width, height
    with mss.mss() as sct:
        return sct.grab(region)

'''

Searchs for an image within an area

input :

image : path to the image file (see opencv imread for supported types)
x1 : top left x value
y1 : top left y value
x2 : bottom right x value
y2 : bottom right y value
precision : the higher, the lesser tolerant and fewer false positives are found default is 0.8
im : a PIL image, usefull if you intend to search the same unchanging region for several elements

returns :
the top left corner coordinates of the element if found as an array [x,y] or [-1,-1] if not

'''


def imagesearcharea(image, x1, y1, x2, y2, precision=0.8, im=None):
    if im is None:
        im = region_grabber(region=(x1, y1, x2, y2))
        if is_retina:
            im.thumbnail((round(im.size[0] * 0.5), round(im.size[1] * 0.5)))
        # im.save('testarea.png') usefull for debugging purposes, this will save the captured region as "testarea.png"

    img_rgb = np.array(im)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(image, 0)
    if template is None:
        raise FileNotFoundError('Image file not found: {}'.format(image))

    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if max_val < precision:
        return [-1, -1]
    return max_loc


'''

click on the center of an image with a bit of random.
eg, if an image is 100*100 with an offset of 5 it may click at 52,50 the first time and then 55,53 etc
Usefull to avoid anti-bot monitoring while staying precise.

this function doesn't search for the image, it's only ment for easy clicking on the images.

input :

image : path to the image file (see opencv imread for supported types)
pos : array containing the position of the top left corner of the image [x,y]
action : button of the mouse to activate : "left" "right" "middle", see pyautogui.click documentation for more info
time : time taken for the mouse to move from where it was to the new position
'''


def click_image(image, pos, action, timestamp, offset=5):
    img = cv2.imread(image)
    if img is None:
        raise FileNotFoundError('Image file not found: {}'.format(image))
    height, width, channels = img.shape
    pyautogui.moveTo(pos[0] + r(width / 2, offset), pos[1] + r(height / 2, offset),
                     timestamp)
    pyautogui.click(button=action)


'''
Searchs for an image on the screen

input :

image : path to the image file (see opencv imread for supported types)
precision : the higher, the lesser tolerant and fewer false positives are found default is 0.8
im : a PIL image, usefull if you intend to search the same unchanging region for several elements

returns :
the top left corner coordinates of the element if found as an array [x,y] or [-1,-1] if not

'''



def imagesearch(image, precision=0.8):
    with mss.mss() as sct:
    
        # image and img_gray are screencaptures of the monitor
        #im = sct.grab(sct.monitors[0])
        #monitor = {"top": 160, "left": 160, "width": 160, "height": 135}
        monitorMain = sct.monitors[2]
        # get center of monitor
        centerX = monitorMain["width"] / 2
        centerY = monitorMain["height"] / 2
        print("centerX: " + str(centerX))
        print("centerY: " + str(centerY))
        
        # Declare upper left coordinate of capture box to search
        # need to optimize to a percentage of monitor pixels not magic numbers
        captureUpperLeftX = int(centerX - 400)
        captureUpperLeftY = int(centerY - 100)
        #Capture down to the center point of the screen (needs optimizing)
        captureWidth = int(centerX - captureUpperLeftX)
        captureHeight = int(centerY - captureUpperLeftY)
        print("captureWidth: " + str(captureWidth))
        print("captureHeight: " + str(captureHeight))
        
        monitorMainCenter = {"top": captureUpperLeftY, "left": captureUpperLeftX, "width": captureWidth, "height": captureHeight}
        im = sct.grab(monitorMainCenter)
        
        if is_retina:
            im.thumbnail((round(im.size[0] * 0.5), round(im.size[1] * 0.5)))
        img_rgb = np.array(im)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        cv2.imshow("img_gray", img_gray)
        cv2.waitKey(250)        
        
        
        # template is a medal in the images folder
        template = cv2.imread(image)
        if template is None:
            raise FileNotFoundError('Image file not found: {}'.format(image))
        template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        #template = cv2.Canny(template, 50, 200)
        (tH, tW) = template.shape[:2]
        #cv2.imshow("template", template)
        #cv2.waitKey(250)
        #time.sleep(5)

        # Added code here to handle multiple sizes of images
        # loop over the scales of the image
        #scales = np.linspace(0.2, 1.0, 20)[::-1]
        #print(scales)
        for scale in np.linspace(0.3, .6, 10)[::-1]:
            print('scale: ' + str(scale))
            # resize the image according to the scale, and keep track
            # of the ratio of the resizing
            resizedTemplate = imutils.resize(template, width = int(template.shape[1] * scale))
            #cv2.imshow('resizedTemplate', resizedTemplate)
            #cv2.waitKey(250)
            r = img_gray.shape[1] / float(resizedTemplate.shape[1])
            #cv2.imshow("img_gray", img_gray)
            #cv2.waitKey(250)
            # if the resized image is smaller than the template, then break
            # from the loop
            #if resizedTemplate.shape[0] < tH or resizedTemplate.shape[1] < tW:
            #    print('too large, break')
            #    break        
        
            #res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
            res = cv2.matchTemplate(img_gray, resizedTemplate, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            
            # if max_val < precision:
                # return [-1, -1]
            if max_val >= precision:
                return max_loc
        
        if max_val < precision:
            return [-1, -1]
            
        return max_loc
        
        

def imagesearchOLD(image, precision=0.8):
    with mss.mss() as sct:
        im = sct.grab(sct.monitors[0])
        if is_retina:
            im.thumbnail((round(im.size[0] * 0.5), round(im.size[1] * 0.5)))
        # im.save('testarea.png') useful for debugging purposes, this will save the captured region as "testarea.png"
        img_rgb = np.array(im)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        template = cv2.imread(image, 0)
        if template is None:
            raise FileNotFoundError('Image file not found: {}'.format(image))
        template.shape[::-1]

        # Added code here to handle multiple sizes of images
        # loop over the scales of the image
        #scales = np.linspace(0.2, 1.0, 20)[::-1]
        #print(scales)
        (tH, tW) = template.shape[:2]
        cvw.imshow("template", template)
        for scale in np.linspace(0.3, 0.6, 20)[::-1]:
            print('scale: ' + str(scale))
            # resize the image according to the scale, and keep track
            # of the ratio of the resizing
            resized = imutils.resize(img_gray, width = int(img_gray.shape[1] * scale))
            #cv2.imshow('template', template)
            #time.sleep(5)
            r = img_gray.shape[1] / float(resized.shape[1])
            # if the resized image is smaller than the template, then break
            # from the loop
            if resized.shape[0] < tH or resized.shape[1] < tW:
                print('too large, break')
                break        
        
            #res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
            res = cv2.matchTemplate(resized, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            
            # if max_val < precision:
                # return [-1, -1]
            if max_val >= precision:
                return max_loc
        
        if max_val < precision:
            return [-1, -1]
            
        return max_loc


'''
Searchs for an image on screen continuously until it's found.

input :
image : path to the image file (see opencv imread for supported types)
time : Waiting time after failing to find the image
precision : the higher, the lesser tolerant and fewer false positives are found default is 0.8

returns :
the top left corner coordinates of the element if found as an array [x,y]

'''


def imagesearch_loop(image, timesample, precision=0.8):
    pos = imagesearch(image, precision)
    while pos[0] == -1:
        print(image + " not found, waiting")
        time.sleep(timesample)
        pos = imagesearch(image, precision)
    return pos


'''
Searchs for an image on screen continuously until it's found or max number of samples reached.

input :
image : path to the image file (see opencv imread for supported types)
time : Waiting time after failing to find the image
maxSamples: maximum number of samples before function times out.
precision : the higher, the lesser tolerant and fewer false positives are found default is 0.8

returns :
the top left corner coordinates of the element if found as an array [x,y]

'''


def imagesearch_numLoop(image, timesample, maxSamples, precision=0.8):
    pos = imagesearch(image, precision)
    count = 0
    while pos[0] == -1:
        print(image + " not found, waiting")
        time.sleep(timesample)
        pos = imagesearch(image, precision)
        count = count + 1
        if count > maxSamples:
            break
    return pos


'''
Searchs for an image on a region of the screen continuously until it's found.

input :
image : path to the image file (see opencv imread for supported types)
time : Waiting time after failing to find the image
x1 : top left x value
y1 : top left y value
x2 : bottom right x value
y2 : bottom right y value
precision : the higher, the lesser tolerant and fewer false positives are found default is 0.8

returns :
the top left corner coordinates of the element as an array [x,y]

'''


def imagesearch_region_loop(image, timesample, x1, y1, x2, y2, precision=0.8):
    pos = imagesearcharea(image, x1, y1, x2, y2, precision)

    while pos[0] == -1:
        time.sleep(timesample)
        pos = imagesearcharea(image, x1, y1, x2, y2, precision)
    return pos


'''
Searches for an image on the screen and counts the number of occurrences.

input :
image : path to the target image file (see opencv imread for supported types)
precision : the higher, the lesser tolerant and fewer false positives are found default is 0.9

returns :
the number of times a given image appears on the screen.
optionally an output image with all the occurances boxed with a red outline.

'''


def imagesearch_count(image, precision=0.9):
    with mss.mss() as sct:
        img_rgb = sct.grab()
        if is_retina:
            img_rgb.thumbnail((round(img_rgb.size[0] * 0.5), round(img_rgb.size[1] * 0.5)))
        img_rgb = np.array(img_rgb)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        template = cv2.imread(image, 0)
        if template is None:
            raise FileNotFoundError('Image file not found: {}'.format(image))
        w, h = template.shape[::-1]
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= precision)
        count = 0
        for pt in zip(*loc[::-1]):  # Swap columns and rows
            # cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2) // Uncomment to draw boxes around found occurrences
            count = count + 1
        # cv2.imwrite('result.png', img_rgb) // Uncomment to write output image with boxes drawn around occurrences
        return count


'''
Get all screens on the provided folder and search them on screen.

input :
path : path of the folder with the images to be searched on screen
precision : the higher, the lesser tolerant and fewer false positives are found default is 0.8

returns :
A dictionary where the key is the path to image file and the value is the position where was found.
'''


def imagesearch_from_folder(path, precision):
    print(path)
    imagesPos = {}
    path = path if path[-1] == '/' or '\\' else path+'/'
    valid_images = [".jpg", ".gif", ".png", ".jpeg"]
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and os.path.splitext(f)[1].lower() in valid_images]
    for file in files:
        pos = imagesearch(path+file, precision)
        imagesPos[path+file] = pos
    return imagesPos


def r(num, rand):
    return num + rand * random.random()
