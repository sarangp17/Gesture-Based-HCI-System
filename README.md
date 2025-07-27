# Gesture-Based-Human-Computer-System
A real-time human-computer interaction system using webcam-based hand tracking to control volume, brightness, and mouse movement. Built with OpenCV and Mediapipe, it uses finger distance and hand landmarks to trigger system-level actions.

# ***SAVE ALL THE FILES IN 1 FOLDER ONLY.***
# ***TRY RUNNING ONLY 1 TKINTER FILE.***
# ***MAKE SURE YOU DOWNLOADED ALL THE REQUIRED PYTHON DEPENDENCIES AND LIBRARIES.***





# Gesture-Based Human-Computer Interaction

A real-time hand gesture recognition system that allows users to control **screen brightness**, **volume**, and **mouse movement** using a webcam and simple finger gestures. It utilizes MediaPipe for landmark detection and OpenCV for image processing.

---

 Features

 **Brightness Control** — Adjust screen brightness using **left hand** (thumb and index finger distance)
 **Volume Control** — Change system volume using **right hand** (thumb and pinky distance)
 **Mouse Movement** — Move the cursor using **right hand** (index and middle finger)



 Tech Stack

- Python
- OpenCV
- MediaPipe
- NumPy
- screen_brightness_control
- pycaw
- pyautogui



How It Works

- Webcam captures real-time hand gestures.
- MediaPipe tracks hand landmarks.
- Distance between specific fingers triggers system-level actions:
  - Brightness: Left hand – index ↔ thumb
  - Volume: Right hand – pinky ↔ thumb
  - Mouse: Right hand – cursor follows finger



 Setup Instructions

1. Clone the repository
   

2. Install dependencies

   
   pip install opencv-python mediapipe numpy screen_brightness_control pycaw pyautogui
   

3. Run the script

   
   python main.py
   



 File Overview

* `main.py` — Main logic for camera input and gesture control.
* `Brightness()` — Function to adjust brightness using hand tracking.



 Notes

* Use in a well-lit room for better detection.
* Works best on Windows (brightness control may vary on Linux/macOS).
* Ensure webcam permissions are enabled.



 To-Do

* Add gesture-based clicking
* Add on-screen indicators for actions
* Optimize hand detection in varying lighting



Built by Sarang Palsutkar

