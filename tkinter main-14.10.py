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
import htm  # Ensure this is a valid module with the required class
import numpy as np
import pyautogui  # pip install PyAutoGUI

# ------------------------ Audio Setup ------------------------

# Initialize audio device for volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume_control = cast(interface, POINTER(IAudioEndpointVolume))
volMin, volMax = volume_control.GetVolumeRange()[:2]

# -------------------- Mediapipe Setup ------------------------

# Initialize Mediapipe Hands
mphands = mp.solutions.hands
hands = mphands.Hands(
    static_image_mode=False,
    model_complexity=1,
    max_num_hands=2,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.5
)
Draw = mp.solutions.drawing_utils

# -------------------- Global Flags --------------------------

# Flags to control different processes
running = False              # For Brightness/Volume Control
mouse_control_running = False
b_v_control_running = False

# Timer to track when hands were last seen
last_hand_time = 0
no_hand_duration_limit = 7    # 7 seconds of no hands to stop B/V control

# -------------------- Mouse Control Variables -------------

wCam, hCam = 640, 480
frameR = 100  # Frame Reduction for the control region
smoothening = 7
pTime = 0     # Previous time for FPS calculation
plocX, plocY = 0, 0  # Previous location
clocX, clocY = 0, 0  # Current location

# Initialize mouse detector
detector = htm.handDetector(detectionCon=0.60, maxHands=1)
wScr, hScr = pyautogui.size()

# Initialize VideoCapture
cap = None

# -------------------- Mouse Control Functions -------------

def start_mouse_control():
    global mouse_control_running, cap, plocX, plocY, clocX, clocY, pTime
    if mouse_control_running:
        print("Mouse control is already running.")
        return
    mouse_control_running = True
    cap = cv2.VideoCapture(0)
    cap.set(3, wCam)
    cap.set(4, hCam)
    
    # Initialize previous time for FPS
    pTime = time.time()
    
    while mouse_control_running:
        success, img = cap.read()
        if not success:
            print("Failed to read from camera.")
            break
        img = detector.findHands(img)
        lmList, bbox = detector.findPosition(img)
        if len(lmList) != 0:
            x1, y1 = lmList[8][1:]  # Index finger tip
            x2, y2 = lmList[12][1:]  # Middle finger tip

            fingers = detector.fingersUp()

            # Moving mode: index finger is up, middle finger is down
            if fingers[1] == 1 and fingers[2] == 0:
                x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
                y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
                clocX = plocX + (x3 - plocX) / smoothening
                clocY = plocY + (y3 - plocY) / smoothening
                pyautogui.moveTo(wScr - clocX, clocY)
                cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                plocX, plocY = clocX, clocY  # Update previous location

            # Click mode: index and middle finger are both up
            if fingers[1] == 1 and fingers[2] == 1:
                length, img, lineInfo = detector.findDistance(8, 12, img)
                if length < 30:
                    cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                    pyautogui.click()

            # Display FPS
            cTime = time.time()
            fps = 1 / (cTime - pTime) if (cTime - pTime) > 0 else 0
            pTime = cTime
            cv2.putText(img, f'FPS: {int(fps)}', (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
        
        cv2.imshow("Mouse Control", img)
        if cv2.waitKey(1) & 0xFF == 27:  # Press Esc to exit
            break

    stop_mouse_control()

def stop_mouse_control():
    global mouse_control_running, cap
    if not mouse_control_running:
        print("Mouse control is not running.")
        return
    mouse_control_running = False
    if cap is not None:
        cap.release()
        cv2.destroyAllWindows()

# ---------------- Brightness/Volume Control Functions --------

def start_b_v_control():
    global cap, running, last_hand_time, b_v_control_running, mouse_control_running
    if b_v_control_running:
        print("Brightness/Volume control is already running.")
        return
    running = True
    b_v_control_running = True
    last_hand_time = time.time()  # Initialize the timer

    # Stop mouse control when B/V control starts
    if mouse_control_running:
        stop_mouse_control()

    # Start B/V control in a new thread
    Thread(target=process_b_v_control).start()

def process_b_v_control():
    global running, last_hand_time, b_v_control_running, cap
    cap = cv2.VideoCapture(0)
    while running:
        ret, img = cap.read()
        if not ret:
            print("Failed to read from camera.")
            break
        img = cv2.flip(img, 1)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)

        if results.multi_hand_landmarks:
            last_hand_time = time.time()  # Reset the timer on hand detection
            if len(results.multi_handedness) == 2:
                cv2.putText(img, 'Both Hands', (250, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
            else:
                for hand_handedness in results.multi_handedness:
                    label = MessageToDict(hand_handedness)['classification'][0]['label']
                    if label == 'Left':
                        cv2.putText(img, 'Left Hand', (250, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 255), 2)
                        Brightness(img, imgRGB, results, Draw, mphands, hands)
                    elif label == 'Right':
                        cv2.putText(img, 'Right Hand', (460, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                        Volume(img, imgRGB, results, Draw, mphands, hands)
        else:
            # If no hands are detected, check for the time elapsed since the last hand detection
            if time.time() - last_hand_time > no_hand_duration_limit:
                print("No hands detected for 7 seconds. Stopping control...")
                break  # Stop the control after 7 seconds of inactivity

        cv2.imshow('Hand Control', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    stop_b_v_control()

def stop_b_v_control():
    global running, b_v_control_running, cap

    if not b_v_control_running:
        print("Brightness/Volume control is not running.")
        return
    running = False
    b_v_control_running = False
    if cap is not None:
        cap.release()
        cv2.destroyAllWindows()

    # Restart mouse control when B/V control stops
    Thread(target=start_mouse_control).start()

def stop_camera():
    if b_v_control_running:
        stop_b_v_control()

# -------------------- GUI Setup -----------------------------

def disable_minimize(root):
    root.update_idletasks()
    root.attributes('-toolwindow', 1)  # Prevents minimize
    root.attributes('-topmost', True)  # Keeps window always on top

def create_3d_button(canvas, x, y, width, height, text, command, bg_color, fg_color):
    # Create shadow effect
    shadow_offset = 4
    shadow = canvas.create_rectangle(
        x + shadow_offset, y + shadow_offset,
        x + width + shadow_offset, y + height + shadow_offset,
        fill="gray", outline=""
    )

    # Create main button rectangle
    button = canvas.create_rectangle(
        x, y, x + width, y + height,
        fill=bg_color, outline="darkgray", width=2
    )

    # Create the text for the button
    button_text = canvas.create_text(
        x + width / 2, y + height / 2,
        text=text, fill=fg_color, font=("Helvetica", 12, "bold")
    )

    # Button hover effect (lighten color)
    def on_enter(event):
        canvas.itemconfig(button, fill="#85C1E9")

    def on_leave(event):
        canvas.itemconfig(button, fill=bg_color)

    canvas.tag_bind(button, "<Enter>", on_enter)
    canvas.tag_bind(button_text, "<Enter>", on_enter)
    canvas.tag_bind(button, "<Leave>", on_leave)
    canvas.tag_bind(button_text, "<Leave>", on_leave)

    # Button click binding
    canvas.tag_bind(button, "<Button-1>", lambda e: command())
    canvas.tag_bind(button_text, "<Button-1>", lambda e: command())

def create_gui():
    root = tk.Tk()
    root.title("Hand Control for Brightness and Volume")
    root.geometry("500x350")

    # Disable minimize, keep maximize and close
    disable_minimize(root)

    # Create a canvas to handle custom designs like gradient and shadows
    canvas = tk.Canvas(root, width=500, height=350)
    canvas.pack()

    # Create a gradient background
    for i in range(350):
        r = int(44 + (46 * (i / 350)))  # from #2C3E50 to #34495E
        g = int(62 + (59 * (i / 350)))
        b = int(80 + (66 * (i / 350)))
        color = f'#{r:02x}{g:02x}{b:02x}'
        canvas.create_line(0, i, 500, i, fill=color)

    # Add title with a shadow effect for 3D look
    title_shadow_offset = 2
    title_font = ("Helvetica", 20, "bold")
    canvas.create_text(
        252 + title_shadow_offset, 52 + title_shadow_offset,
        text="Hand Control System", fill="gray", font=title_font
    )
    canvas.create_text(
        252, 52,
        text="Hand Control System", fill="#FFFFFF", font=title_font
    )

    # Create 3D buttons
    create_3d_button(
        canvas, 100, 150, 150, 50, "B/V Control",
        lambda: Thread(target=start_b_v_control).start(),
        "#2980B9", "white"
    )
    create_3d_button(
        canvas, 260, 150, 150, 50, "Stop Control",
        lambda: stop_camera(),
        "#E74C3C", "white"
    )

    # Start mouse control by default in a separate thread
    Thread(target=start_mouse_control, daemon=True).start()

    root.mainloop()

# -------------------- Main Execution -----------------------

if __name__ == "__main__":
    create_gui()
