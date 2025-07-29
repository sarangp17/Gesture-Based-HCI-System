

# Gesture-Based Human-Computer Interaction System

A real-time gesture-controlled interface that transforms your webcam into an intuitive input device for managing **volume**, **screen brightness**, and **mouse movement** — all through **hand gestures**. This system offers a touchless control mechanism using computer vision and hand landmark tracking. It provides an accessible and practical alternative to traditional input hardware, useful in accessibility solutions, presentations, and hands-free environments.

---

## How the System Works (Backend Perspective)

This system combines **MediaPipe** and **OpenCV** to detect and analyze hand gestures in real time. Here's how it functions behind the scenes:

1. **Video Frame Capture**
   The system uses OpenCV to read frames from the webcam. Each frame is passed through the pipeline for processing.

2. **Hand Landmark Detection with MediaPipe**
   MediaPipe detects up to 21 landmarks for each hand in every frame. These landmarks include fingertip positions, joints, and the wrist. Landmark data is used to determine the gesture being made.

3. **Gesture Interpretation and Mapping**

   * **Brightness Control (Left Hand)**:
     The distance between the thumb tip and index fingertip is calculated and mapped to screen brightness using the `screen_brightness_control` library.
   * **Volume Control (Right Hand)**:
     The distance between the thumb tip and pinky tip is used to control system volume using `pycaw`, which interacts with Windows Core Audio APIs.
   * **Mouse Movement (Right Hand)**:
     The position of the index and middle fingertips is mapped to screen coordinates and updated in real time using `pyautogui`. Movements are smoothed to enhance user experience.

4. **Command Execution**
   Once the gestures are interpreted, the system sends the appropriate commands to the OS to change volume, brightness, or cursor position.

5. **(Optional) GUI with Tkinter**
   If enabled, a Tkinter-based GUI can provide a visual interface, but only one such file should be run at a time to avoid conflicts.

---

## Features

* Screen Brightness Control via **left hand** (thumb–index finger distance)
* System Volume Control via **right hand** (thumb–pinky distance)
* Real-time Mouse Movement via **right hand** (index–middle finger tracking)
* Smooth and real-time gesture tracking
* Modular codebase for easy extension and integration

---

## Technical Stack

* Python
* OpenCV
* MediaPipe
* NumPy
* pyautogui
* screen\_brightness\_control
* pycaw

---

## Novelty

This project goes beyond basic gesture recognition in the following ways:

* Combines **three distinct system-level controls** (brightness, volume, and mouse) into **a single unified hand gesture interface**.
* Uses **both hands separately** for different functionalities, increasing accuracy and reducing gesture collisions.
* Achieves **real-time, non-intrusive control** without relying on specialized hardware — only a standard webcam is needed.
* Designed to be **platform-light**, requiring no external servers or cloud-based APIs.
* Easily extendable for future controls like **clicking, media playback, slide navigation**, or **custom gesture mapping**.

---

## Setup Instructions

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/Gesture-Based-Human-Computer-System
   cd Gesture-Based-Human-Computer-System
   ```

2. Install dependencies:

   ```bash
   pip install opencv-python mediapipe numpy pyautogui pycaw screen_brightness_control
   ```

3. Run the main script:

   ```bash
   python main.py
   ```

---

## File Overview

* `main.py`: Core logic for webcam input, gesture detection, and system-level control
* `brightness.py`: Brightness adjustment based on left-hand gestures
* `volume.py`: Volume control logic using right-hand gestures
* `mouse.py`: Mouse movement via right-hand finger tracking
* `utils.py`: Helper functions such as distance calculation and frame smoothing

---

## Notes

* Use in a well-lit environment for optimal accuracy
* Works best on **Windows** (brightness and volume control libraries are Windows-specific)
* Ensure webcam access is enabled and no other apps are using it
* Save **all files in a single folder**
* Run **only one Tkinter file** at a time if using GUI

---

## To-Do

* Add gesture-based clicking and right-clicking
* Display on-screen indicators for gesture status
* Improve robustness in low-light or cluttered backgrounds
* Add support for multi-monitor setups
* Add custom user-defined gesture mappings

---

## By-

**Sarang Palsutkar**

---

