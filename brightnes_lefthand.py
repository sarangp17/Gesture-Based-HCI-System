import cv2
import numpy as np
import mediapipe as mp
# import time
# import os
from math import hypot
import screen_brightness_control as sbc
# mphands = mp.solutions.hands
# hands=mphands.Hands(static_image_mode=False,
#                     model_complexity=1,
#                     max_num_hands=1,
#                     min_detection_confidence=0.75,
#                     min_tracking_confidence=0.75)
# Draw=mp.solutions.drawing_utils
# cap=cv2.VideoCapture(0)
# while True:
#     _,frame=cap.read()
#     frame=cv2.flip(frame,1)
#     frameRGB=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
#     results=hands.process(frameRGB)

def Brightness(frame,frameRGB,results,Draw,mphands,hands):##left hand
        landmarkList=[]
        if results.multi_hand_landmarks:
            for handlm in results.multi_hand_landmarks:
                for id, lm in enumerate(handlm.landmark):
                    h, w, c = frame.shape
                    x,y=int(lm.x*w),int(lm.y*h)
                    landmarkList.append([id,x,y])
                Draw.draw_landmarks(frame,
                                    handlm,
                                    mphands.HAND_CONNECTIONS)
        if landmarkList !=[]:
            x_1,y_1=landmarkList[4][1],landmarkList[4][2]
            x_2,y_2=landmarkList[8][1],landmarkList[8][2]
            cv2.circle(frame,(x_1,y_1),5,(0,255,0),
                       cv2.FILLED)
            cv2.circle(frame,(x_2,y_2),5,(0,255,0),
                       cv2.FILLED)
            cv2.line(frame,(x_1,y_1),(x_2,y_2),(255,0,0),3)
            L=hypot(x_2-x_1,y_2-y_1)
            b_level=np.interp(L,[15,220],[15,100])
            sbc.set_brightness(int(b_level))
        cv2.imshow('img',frame)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
# cap.release()
# cv2.destroyAllWindows()