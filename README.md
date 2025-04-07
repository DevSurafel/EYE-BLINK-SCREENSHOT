# 👁️ Blink + Gesture Control App

A real-time computer vision application that detects **blinks** and **hand gestures** using your webcam, enabling you to take screenshots or start/stop screen recordings with natural actions like **double blinking** or showing **three fingers**!

This project uses **MediaPipe**, **OpenCV**, and **PyAutoGUI** to provide a hands-free user interaction system.

---

## 🧠 Features

- ✅ **Double blink detection** – Takes a screenshot and saves it to your desktop.
- ✋ **Three-finger gesture detection** – Starts/stops screen recording.
- 📦 Real-time landmark tracking for **face mesh** and **hand landmarks**.
- 📢 Notifies and speaks actions performed (macOS) or prints in console (Windows).
- 📸 Shows real-time webcam preview with annotations.

---

## 📋 Requirements

- Python 3.7+
- pip (Python package manager)

Install the required libraries:

```bash
pip install opencv-python mediapipe pyautogui numpy
```

> For **macOS**, `ffmpeg` is required for screen recording. Install it using:
```bash
brew install ffmpeg
```

> For **Windows**, you’ll need to install and set up `ffmpeg`. [Download from here](https://ffmpeg.org/download.html) and add the path to your system environment variables.

---

## 💻 How It Works

### 👁️ Blink Detection (Screenshot)

- The app detects a **double blink** (two blinks within 1 second).
- When detected:
  - Takes a screenshot with `pyautogui`.
  - Saves it to the desktop.
  - macOS: Shows a desktop notification, plays a sound, and speaks out loud.
  - Windows: Screenshot saved; notification/sound/speech not yet implemented but can be extended.

### ✋ Three-Finger Gesture (Screen Recording)

- When **three fingers** are held up for 1 second:
  - Starts screen recording using `ffmpeg`.
  - Show three fingers again to stop recording.
  - Recording saved to desktop.

---

## 🖥️ Platform Support

| Feature               | macOS                             | Windows                            |
|----------------------|------------------------------------|-------------------------------------|
| Blink detection       | ✅                                 | ✅                                  |
| Hand gesture control  | ✅                                 | ✅                                  |
| Screenshot            | ✅ `pyautogui`                     | ✅ `pyautogui`                      |
| Screen recording      | ✅ via `ffmpeg + avfoundation`     | ✅ via `ffmpeg + gdigrab` (edit code) |
| Notifications         | ✅ `osascript`                     | ❌ (use `plyer` or `win10toast`)   |
| Text-to-speech        | ✅ `say`                           | ❌ (use `pyttsx3` or `winspeech`)  |
| Sound effects         | ✅ `afplay`                        | ❌ (use `playsound` or `winsound`) |

> You can modify the script to support Windows notifications and speech using packages like:
- `plyer` or `win10toast` for desktop notifications
- `pyttsx3` for text-to-speech
- `playsound` or `winsound` for audio feedback

---

## 🚀 Run the App

```bash
python your_script_name.py
```

Press `ESC` to exit the app.

---

## 🛠️ Optional Improvements for Windows Users

To make the app fully functional on Windows, replace:

- `show_notification()` → with `plyer.notification.notify()` or `win10toast`
- `speak_message()` → with `pyttsx3.init().say()`
- `play_sound()` → with `playsound` or `winsound.Beep`

For screen recording input, update the `ffmpeg` command:
```bash
# Windows-friendly ffmpeg input (example)
ffmpeg -f gdigrab -framerate 30 -i desktop output.mp4
```

---

## 📸 Demo

*Coming Soon

---

## 🧑‍💻 Author
Surafel Diriba   
Feel free to fork or reach out!

---

## 📄 License

MIT License – use, modify, and distribute freely.
