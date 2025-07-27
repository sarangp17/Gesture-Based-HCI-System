import cv2
import numpy as np
import pyautogui
import time
import htm  # Ensure this module is implemented as per the first program

# Constants
wCam, hCam = 640, 480
frameR = 100  # Frame Reduction
smoothening = 7

# Initialize Variables
plocX, plocY = 0, 0  # Previous location
clocX, clocY = 0, 0  # Current location

# Screen Size
wScr, hScr = pyautogui.size()

# Hand Detector Initialization
detector = htm.handDetector(detectionCon=0.6, maxHands=1)

# Webcam Setup
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

while True:
    success, img = cap.read()
    if not success:
        break
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)

    if len(lmList) != 0:
        # Get the tip of the index and middle fingers
        x1, y1 = lmList[8][1:]  # Index finger
        x2, y2 = lmList[12][1:]  # Middle finger

        # Check which fingers are up
        fingers = detector.fingersUp()

        # Moving mode: index finger up, middle finger down
        if fingers[1] == 1 and fingers[2] == 0:
            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening
            pyautogui.moveTo(wScr - clocX, clocY)
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            plocX, plocY = clocX, clocY

        # Click mode: both index and middle fingers up
        if fingers[1] == 1 and fingers[2] == 1:
            length, img, lineInfo = detector.findDistance(8, 12, img)
            if length < 30:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                pyautogui.click()

    # Display the image
    cv2.imshow("Mouse Control", img)
    if cv2.waitKey(1) & 0xFF == 27:  # Press Esc to exit
        break

cap.release()
cv2.destroyAllWindows()
