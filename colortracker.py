import numpy as np
import cv2
import sys
import traceback
from picamera.array import PiRGBArray
from picamera import PiCamera
import time 
import threading
from kali import QuadController

resx = 176
resy = 156

maxthrust = 45 # max cant increase 127
minthrust = 5 # min cant decrease 0
kd=10
ki=400
px=RefCenterX = int(resx/2)
py=RefCenterY = int(resy/2)
pradius=2

color_to_track = raw_input("orange,blue,green,red ?")
type(color_to_track)
if color_to_track == 'green':
   colorLower = (30, 86, 70)
   colorUpper = (75, 255, 255)
elif color_to_track == 'blue':
   colorLower = (50,100,120)
   colorUpper = (130,254,254)
elif color_to_track == 'orange':
   colorLower = (15,100,120)
   colorUpper = (25,254,254)
elif color_to_track == 'red':
   colorLower = (0,100,70)
   colorUpper = (8,255,255)

   UColorLower = (172,100,70)
   UColorUpper = (180,255,255)

else:
   colorLower = (0,0,245)
   colorUpper = (180,10,255)

last_seen=False
syma = QuadController('/dev/ttyUSB0',9600)
syma.setCenter(RefCenterX,RefCenterY)
syma.setThrust(maxthrust,minthrust)
maxrange = RefCenterX if RefCenterX < RefCenterY else RefCenterY
syma.setRange(maxrange,2)
syma.kd=kd
syma.ki=ki
syma.log("-------------Started------------")
x1=x2=x3=x4=x5=y1=y2=y3=y4=y5=0

camera = PiCamera()
camera.resolution = (resx, resy)
#camera.framerate = 10 
rawCapture = PiRGBArray(camera, size=(resx, resy))
dispvid = 1
frame=0

found=0
ss=[]
ishow = threading.Event()

def displayvid():
    global dispvid
    global ishow
    global px
    global frame
    global py
    global ss
    global syma
    #cv2.namedWindow('preview',cv2.WINDOW_NORMAL)
    #cv2.startWindowThread()
    #cv2.resizeWindow('preview',560,530)

    while(dispvid):
        ishow.wait()
        cv2.imshow('preview',frame)
        c=cv2.waitKey(5)
        #c=67
        if ord('c') == c: 
            break;
        try:
              if ord('1') == c:
                  px=ss[0][0]
                  py=ss[0][1]
              elif ord('2') == c:
                  px=ss[1][0]
                  py=ss[1][1]
              elif ord('3') == c:
                  px=ss[2][0]
                  py=ss[2][1]
              elif ord('4') == c:
                  px=ss[3][0]
                  py=ss[3][1]
        except:
               pass
        ishow.clear()
    print 'display terminated'
    syma.quit()


a = threading.Thread(target=displayvid)
a.start()
 
try:
    for framer in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        frame = framer.array
        rawCapture.truncate(0)
        #ishow.set()
        #continue
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv, colorLower, colorUpper)
        if(color_to_track=='red'):
          msk1=cv2.inRange(hsv,UColorLower,UColorUpper)
          mask=mask+msk1
        mask = cv2.erode(mask, None, iterations=1)
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]

        if len(cnts) > 0:
                mini = 10000
                nearest = 0
                nx=ny=nr=0
                ss=[] 

                for s in cnts:
                    ((npx,npy),rd)=cv2.minEnclosingCircle(s)
                    if rd<3 :
                        continue
                    val= ((abs(npx-px))**2+(abs(npy-py))**2)**(1/2.0) #distance from recent traced contour
                    if val<mini:
                        nearest =s 
                        mini=val
                    if val<140:
                        found=1

                if(found):
                    ((nx,ny),nr)=cv2.minEnclosingCircle(nearest)
                #else:
                #	(py,px)=(RefCenterY,RefCenterX)
                for cc in cnts:
                    ((x, y), radius) = cv2.minEnclosingCircle(cc)
                    if radius > 4:
                        if((x,y,radius)==(nx,ny,nr) and found): 
                            px = (int(x)+x1)/2.0
                            x1 = int(x)

                            py = (int(y)+y1)/2.0
                            y1=int(y)

                            pradius=int(radius)
                            found=0
                            last_seen=True
                        else:
                            cv2.circle(frame, (int(x), int(y)), int(radius),(0, 0, 255), 2)
                            cv2.putText(frame,str(len(ss)+1),(int(x),int(y)),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),3)
                            ss.append([x,y])
 
        cv2.circle(frame, (int(px), int(py)), int(pradius),(0, 255, 0), 2)
        ishow.set()
        syma.target(px,py) 
        if  syma.kill_deamons==True: 
                syma.log("Main: Deamons are killed, I'm quiting")
                break
except BaseException as b:

   syma.log("Main: Unknown error")
   syma.log(str(b))
   traceback.print_exc()
dispvid = 0
ishow.set()
syma.quit()
camera.close()
cv2.destroyAllWindows()
