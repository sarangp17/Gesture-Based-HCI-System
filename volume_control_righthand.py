import cv2
import numpy as np
from math import hypot
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities,IAudioEndpointVolume
devices=AudioUtilities.GetSpeakers()
interface=devices.Activate(IAudioEndpointVolume._iid_,CLSCTX_ALL,None)
volume=cast(interface,POINTER(IAudioEndpointVolume))
volbar=400
volper=0
volMin,volMax=volume.GetVolumeRange()[:2]
def Volume(frame,frameRGB,results,Draw,mphands,hands):
    landmarkList = []
    if results.multi_hand_landmarks:
        for handlm in results.multi_hand_landmarks:
            for id, lm in enumerate(handlm.landmark):
                h, w, c = frame.shape
                x, y = int(lm.x * w), int(lm.y * h)
                landmarkList.append([id, x, y])
            Draw.draw_landmarks(frame,
                                handlm,
                                mphands.HAND_CONNECTIONS)
    if landmarkList != []:
        x_1, y_1 = landmarkList[4][1], landmarkList[4][2]#thumb
        x_2, y_2 = landmarkList[8][1], landmarkList[8][2]#index finger
        cv2.circle(frame, (x_1, y_1), 13, (0, 255, 0),
                   cv2.FILLED)
        cv2.circle(frame, (x_2, y_2), 13, (0, 255, 0),
                   cv2.FILLED)
        cv2.line(frame, (x_1, y_1), (x_2, y_2), (255, 0, 0), 3)
        L = hypot(x_2 - x_1, y_2 - y_1)#find distance
        ##set of volume
        vol=np.interp(L,[30,350],[volMin,volMax])
        volbar=np.interp(L,[30,350],[400,150])
        volper=np.interp(L,[30,350],[0,100])
        print(vol,int(L))
        volume.SetMasterVolumeLevel(vol,None)
        #create volume bar
        cv2.rectangle(frame,(50,150),(85,400),(255,0,0),4)#video,intial position,ending postion,rgb,thickness
        cv2.rectangle(frame,(50,int(volbar)),(85,400),(0,0,255),cv2.FILLED)
        cv2.putText(frame,f"{int(volper)}%",(10,40),cv2.FONT_ITALIC,1,(0,255,98),3)
    cv2.imshow('img', frame)