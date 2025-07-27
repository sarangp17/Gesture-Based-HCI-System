import tkinter as tk
from threading import Thread
import cv2
import mediapipe as mp
from google.protobuf.json_format import MessageToDict
from brightnes_lefthand import Brightness
from volume_control_righthand import Volume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import time
import htm as htm  
import numpy as np
import pyautogui
import sys  

# Audio settings for volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volMin, volMax = volume.GetVolumeRange()[:2]

# Initialize mediapipe hands
mphands = mp.solutions.hands
hands = mphands.Hands(static_image_mode=False, model_complexity=1, max_num_hands=2,
                      min_detection_confidence=0.75, min_tracking_confidence=0.5)
Draw = mp.solutions.drawing_utils
cap = None
mouse_tracker_running = False  # Mouse tracker running flag

# Flag to control webcam process
running = False

def start_camera():
    global cap, running
    if running:
        return
    running = True
    cap = cv2.VideoCapture(0)
    process_video()

def process_video():
    global running
    cv2.namedWindow("Hand Control", cv2.WINDOW_NORMAL)
    cv2.moveWindow("Hand Control", -10000, -10000)  # Move the window off-screen
    
    while running:
        ret, img = cap.read()
        if not ret:
            break
        img = cv2.flip(img, 1)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)
        if results.multi_hand_landmarks:
            if len(results.multi_handedness) == 2:
                cv2.putText(img, 'bothhands', (250, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
            else:
                for i in results.multi_handedness:
                    label = MessageToDict(i)['classification'][0]['label']
                    if label == 'Left':
                        cv2.putText(img, label + ' hand', (250, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 255), 2)
                        Brightness(img, imgRGB, results, Draw, mphands, hands)
                    if label == 'Right':
                        cv2.putText(img, label + ' hand', (460, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                        Volume(img, imgRGB, results, Draw, mphands, hands)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    stop_camera()

def stop_camera():
    global cap, running, mouse_tracker_running
    running = False
    mouse_tracker_running = False  # Stop mouse tracker when Stop Control is clicked
    if cap is not None:
        cap.release()
        cv2.destroyAllWindows()

def mouse_tracker():
    global mouse_tracker_running
    mouse_tracker_running = True

    wCam, hCam = 640, 480
    frameR = 100
    smoothening = 7
    pTime = 0
    plocX, plocY = 0, 0
    clocX, clocY = 0, 0

    cap = cv2.VideoCapture(0)
    cap.set(3, wCam)
    cap.set(4, hCam)
    detector = htm.handDetector(detectionCon=0.60, maxHands=1)
    wScr, hScr = pyautogui.size()

    while mouse_tracker_running:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList, bbox = detector.findPosition(img)
        if len(lmList) != 0:
            x1, y1 = lmList[8][1:]  # Index finger tip
            x2, y2 = lmList[12][1:]  # Middle finger tip

            fingers = detector.fingersUp()

            if fingers[1] == 1 and fingers[2] == 0:  # Only index finger up
                x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
                y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
                clocX = plocX + (x3 - plocX) / smoothening
                clocY = plocY + (y3 - plocY) / smoothening
                pyautogui.moveTo(wScr - clocX, clocY)
                cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                plocX, plocY = clocX, clocY
            if fingers[1] == 1 and fingers[2] == 1:  # Index and middle finger up
                length, img, lineInfo = detector.findDistance(8, 12, img)
                if length < 30:  # If fingers are close together
                    cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                    pyautogui.click()

            cTime = time.time()
            fps = 1 / (cTime - pTime)
            pTime = cTime
            cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

            cv2.imshow("Mouse Tracker", img)
            if cv2.waitKey(1) & 0xFF == 27:  # Escape key
                break

    cap.release()
    cv2.destroyAllWindows()

# Disable minimize button by overriding protocol
def disable_minimize(root):
    root.update_idletasks()
    root.attributes('-toolwindow', 1)  # Prevents minimize
    root.attributes('-topmost', True)  # Keeps window always on top

# Function to create a 3D-looking button
def create_3d_button(canvas, x, y, width, height, text, command, bg_color, fg_color):
    shadow_offset = 4
    shadow = canvas.create_rectangle(x + shadow_offset, y + shadow_offset, x + width + shadow_offset, y + height + shadow_offset, fill="gray", outline="")
    button = canvas.create_rectangle(x, y, x + width, y + height, fill=bg_color, outline="darkgray", width=2)
    button_text = canvas.create_text(x + width / 2, y + height / 2, text=text, fill=fg_color, font=("Helvetica", 12, "bold"))

    def on_enter(event):
        canvas.itemconfig(button, fill="#85C1E9")
    def on_leave(event):
        canvas.itemconfig(button, fill=bg_color)

    canvas.tag_bind(button, "<Enter>", on_enter)
    canvas.tag_bind(button_text, "<Enter>", on_enter)
    canvas.tag_bind(button, "<Leave>", on_leave)
    canvas.tag_bind(button_text, "<Leave>", on_leave)

    canvas.tag_bind(button, "<Button-1>", lambda e: command())
    canvas.tag_bind(button_text, "<Button-1>", lambda e: command())

# GUI code using tkinter
def create_gui():
    global canvas, status_text  # Declare as global for access in update_status_text
    root = tk.Tk()
    root.title("Hand Control for Brightness, Volume, and Mouse Tracking")

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 900
    window_height = 120
    x_position = (screen_width // 2) - (window_width // 2)
    y_position = 0

    root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    disable_minimize(root)

    canvas = tk.Canvas(root, width=window_width, height=window_height, bg="black")
    canvas.pack()

    title_font = ("Helvetica", 12, "bold")
    canvas.create_text(window_width // 2 + 2, 20 + 2, text="Hand Control System", fill="gray", font=title_font)
    canvas.create_text(window_width // 2, 20, text="Hand Control System", fill="#FFFFFF", font=title_font)

    # Text box on the canvas to display current operation
    status_text = canvas.create_text(window_width // 2, 50, text="Current Operation: None", fill="white", font=("Helvetica", 12, "bold"))

    create_3d_button(canvas, 160, 70, 180, 30, "B/V Control", lambda: [update_status_text("Current Operation: B/V Control"), Thread(target=start_camera).start()], "#98FF98", "black")
    create_3d_button(canvas, 360, 70, 180, 30, "Stop Control", lambda: [update_status_text("Current Operation: None"), stop_camera()], "#E74C3C", "white")
    create_3d_button(canvas, 560, 70, 180, 30, "Mouse Tracker", lambda: [update_status_text("Current Operation: Mouse Tracking"), Thread(target=mouse_tracker).start()], "#3498DB", "white")
    #create_3d_button(canvas, 760, 70, 120, 30, "Close", lambda: close_tool(root), "#E74C3C", "white")

    root.mainloop()

def update_status_text(text):
    canvas.itemconfig(status_text, text=text)

def close_tool(root):
    stop_camera()
    root.quit()
    sys.exit()  # Close the entire application

if __name__ == "__main__":
    create_gui()
