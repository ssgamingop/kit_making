# 🪁 AR Kite Project

A Python-based Augmented Reality application that lets you build and fly (sort of!) a custom kite using hand gestures and computer vision. Created for **Makar Sankranti**.

## ✨ Features

- **Hybrid Control System**:
  - **🖐️ Hand Tracking**: Move kite components (sticks, paper) using your index finger. Includes **smoothing** for jitter-free precision.
  - **🖱️ Mouse Interaction**: Click to select tools and place items. No more "pinch glitches" for critical actions!
  - **👌 Pinch Gesture**: **Pinch (Thumb + Index)** to grab colors directly from the palette and drag them to your kite.

- **Realistic Visuals**:
  - **Neon Glow** effects on sticks.
  - **Curved Bow** (Kamani) stick implementation.
  - **Textured Paper** with internal structure hints.
  - **Dynamic Tail** (Wavy ribbon) and **Manjha** (String).
  - **Festive Text** overlay.

- **Web Support**: Includes a `Streamlit` version to run the app in a web browser.

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Webcam
- Dependencies (listed in `requirements.txt`)

### Installation

1. Navigate to the project directory:
   ```bash
   cd ARKiteProject
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

### 🏃‍♂️ How to Run

#### Desktop App (Recommended)
For the smoothest experience and best performance:
```bash
python kite_app.py
```

#### Web App
To run in your browser:
```bash
streamlit run web_app.py
```

## 🎮 Controls

| Action | Control |
|--------|---------|
| **Select Tool** | **Left Click** on the sidebar button (Stick 1, Stick 2, Paper). |
| **Move Item** | Move your **Index Finger** in front of the camera. The item snaps to your finger. |
| **Place Item** | **Left Click** anywhere on the screen/camera feed to lock the item in place. |
| **Pick Color** | **Pinch (Thumb + Index)** over a color button in the palette to grab a color blob. |
| **Color Kite** | Drag the pinched color blob to the kite paper and **Release Pinch** to paint it. |
| **Screenshot** | Click the **Screenshot** button to save an image of your creation. |
| **Reset** | Click **Reset** to start over. |

## 📂 Project Structure

- `kite_app.py`: Main desktop application logic.
- `web_app.py`: Streamlit wrapper for web deployment.
- `hand_tracking.py`: MediaPipe wrapper for hand detection and gesture logic.
- `ui_components.py`: Classes for draggable objects (Sticks, Paper) and UI Buttons.
- `utils.py`: Helper functions for graphics and overlays.

## 🛠️ Built With

- **OpenCV**: Computer Vision and Rendering.
- **MediaPipe**: Hand Tracking.
- **Streamlit**: Web Application Framework.
- **NumPy**: Math and Logic.

---
*Happy Makar Sankranti!* 🪁
