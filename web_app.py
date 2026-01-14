import cv2
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import threading

# Import our Kite App logic
from kite_app import KiteApp

st.set_page_config(page_title="AR Kite Maker", layout="wide")

st.title("🪁 AR Kite Maker")
st.markdown("Use hand gestures to build your kite! Drag and drop components.")

class KiteTransformer(VideoTransformerBase):
    def __init__(self):
        self.app = KiteApp(use_camera=False)
        self.app.screenshot_pending = False # Manage state here if needed
        
    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        
        # Process frame using our existing logic
        img = self.app.process_frame(img)
        
        return img

# WebRTC Streamer
webrtc_streamer(key="kite-ar", video_transformer_factory=KiteTransformer)

st.markdown("### Instructions")
st.markdown("- **Select Tool**: Click sidebar buttons (on video if implemented, or we might need to map HTML buttons to Python state).")
st.warning("Note: In this web demo, mouse interactions on the video stream might be limited compared to the local desktop app. The desktop app is recommended for full 'Click on Video' features.")
