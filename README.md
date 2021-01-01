# Hand-Gestures-Musicplayer
This  is a real time music player by hand gestures.

Our project is a real time music player by hand gestures. The user can manipulate the music player to play, pause,
continue and other basic operations for the music. The hand gesture recognition process can be divided into the following steps:

## Algorithm Process
1: Capture the video.  
2: Define the region of object.  
3: Use the opencv library to convert the RGB picture to HSV picture.  
4: Define the skin color in HSV.  
5: Create the mask and extract skin color image and blur the image.  
6: Find a contour.    
7: Define the convex hull around the hand.  
8: Define the area of hull and area of hand.  
9: Find the percentage of are not covered by hand in convex hall.  
10: Find the defects in convex hull with respect to hand.  
11: Find the numbers of defects in convex hull with the respect of hand.  
12: Apply the cosine and calculate the angle.  
13: Determine different gestures based on different characteristics.  



![mask](https://github.com/maying0120/Hand-Gestures-Musicplayer/blob/main/mask.png)

## Gestures Table

![mask](https://github.com/maying0120/Hand-Gestures-Musicplayer/blob/main/ges1.png)

![mask](https://github.com/maying0120/Hand-Gestures-Musicplayer/blob/main/ges2.png)
