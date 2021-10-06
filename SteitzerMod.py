# SteitzerMod.py
# Searches screen for presence of a medal, and plays the corresponding
#   Announcement from Jeff Steitzer


print('SteitzerMod.py')
print('Carter Moody')

# Import os for path string extraction
import os

# Import for sleep function
import time


### pip3 install python-imagesearch
# This will search a region of the screen for the presence of images
from python_imagesearch.imagesearch import imagesearch_region_loop
# This search entire screen for an image in the folder
from python_imagesearch.imagesearch import imagesearch_from_folder

### pip install playsound
# Import for playing sound file
from playsound import playsound

### Sound settings
# Location of the sound effect files
soundEffectsFolder = './soundEffects/'
# Master dictionary matching image file names to associated sounds to play
soundDict = {
    'HINF_TechPre_Medal_DoubleKill.png':
    'Double Kill.mp3',
    'HINF_TechPre_Medal_TripleKill.png':
    'Triple Kill.mp3'
    }
    

# Search dictionary and return correct sound to play
def getSound(image):
    return soundDict[image]


# Play the sound based on provided imageHit
def hitSound(image):
    print('playing sound for: ' + image)
    soundFileName = getSound(image)
    pathToSound = str(soundEffectsFolder + soundFileName)
    playsound(pathToSound)


# Do some string parsing to get rid of path...
def extractImageString(image):
    imageNoPath = os.path.basename(image)
    return imageNoPath


# Determine what to do with an image 'hit'
def processHit(results, image):
    # do whatever processing necessary to this image...
    image = extractImageString(image)
    print('processing image: ' + str(image))
    # Call hitSound to play the appropriate sound
    hitSound(image)


# Checks results dictionary for a value that is NOT [-1, -1]
def checkForHit(results):
    for image in results:
        value = str(results[image])
        print('value: ' + value)
        if value != "[-1, -1]":
           print('match!')
           processHit(results, image)
        else:
           print('no match')


# Does the main processing for the results dictionary
def processResults(results):
    print('processing results')
    hit = False
    hit = checkForHit(results)


# Constantly checks screen for matching image file, creates dictionary
#   for processing
def processingLoop():
    while (True):
        try:
            results = imagesearch_from_folder('./killMedalImages/', .7)
            print(str(results))
            # Process the results  
            processResults(results)

        except FileNotFoundError:
            print('file not found error')
            pass
        #    exit
        
        
def main():
    print('sleeping for 2 seconds on startup...')
    time.sleep(2)
    processingLoop()

if __name__ == "__main__":
    main()