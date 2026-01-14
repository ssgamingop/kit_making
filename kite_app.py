import cv2
import numpy as np
from hand_tracking import HandDetector
from ui_components import Button, DraggableObject
from utils import draw_transparent_rect

class KiteApp:
    def __init__(self, use_camera=True):
        if use_camera:
            self.cap = cv2.VideoCapture(0)
            self.cap.set(3, 1280)
            self.cap.set(4, 720)
        else:
            self.cap = None
        
        self.detector = HandDetector(max_hands=1)
        self.prev_hand_pos = None # For smoothing
        self.is_pinch_active = False # State for hysteresis
        
        # State
        self.objects = [] # List of placed objects
        self.current_object = None # Object currently being dragged
        self.kite_color = (0, 200, 255) # Start yellow
        
        # UI Setup
        self.buttons = [
            Button("Stick 1", (20, 100), action_id="stick1"),
            Button("Stick 2", (20, 180), action_id="stick2"),
            Button("Paper", (20, 260), action_id="paper"),
            Button("Screenshot", (20, 530), color=(100, 100, 100), action_id="screenshot"),
            Button("Reset", (20, 600), color=(0, 0, 150), action_id="reset"),
            Button("Exit", (20, 670), color=(0, 0, 0), action_id="exit")
        ]
        
        self.color_buttons = [
            Button("", (1150, 100), size=(50, 50), color=(0, 255, 255), action_id="col_yellow"),
            Button("", (1150, 160), size=(50, 50), color=(0, 0, 255), action_id="col_red"),
            Button("", (1150, 220), size=(50, 50), color=(255, 0, 0), action_id="col_blue"),
            Button("", (1150, 280), size=(50, 50), color=(0, 255, 0), action_id="col_green"),
             Button("", (1150, 340), size=(50, 50), color=(255, 0, 255), action_id="col_purple"),
        ]
        
        self.message = "Welcome! Select a component."
        self.msg_timer = 0
        
        if use_camera:
            cv2.namedWindow("Gravity AR Kite")
            cv2.setMouseCallback("Gravity AR Kite", self.mouse_callback)

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            # Check UI Buttons
            for btn in self.buttons + self.color_buttons:
                if btn.is_hover(x, y):
                    self.handle_button_click(btn.action_id, btn.color)
                    return

            # Place object if dragging
            if self.current_object:
                if self.current_object.type == 'color_blob':
                    # Check collision with "paper" object
                    for obj in self.objects:
                        if obj.type == 'paper':
                             # Basic distance check for simplicity
                             dist = np.linalg.norm(np.array(self.current_object.pos) - np.array(obj.pos))
                             if dist < 100: # If near paper
                                 obj.color = self.current_object.color
                                 self.message = "Colored!"
                                 self.current_object = None
                                 return
                    self.message = "Missed the kite!"
                    self.current_object = None # Discard blob if missed
                else:
                    self.current_object.place()
                    self.objects.append(self.current_object)
                    self.current_object = None
                    self.message = "Placed!"


    def handle_button_click(self, action_id, color):
        if action_id == "exit":
            self.running = False
            
        elif action_id == "screenshot":
            import time
            filename = f"kite_screenshot_{int(time.time())}.png"
            # We need to capture the frame *with* the overlay. 
            # This is tricky because `self.handle_button_click` happens inside the loop but we don't have the final frame here.
            # We will set a flag.
            self.screenshot_pending = True
            self.message = "Cheese! 📸"

        elif action_id == "reset":
            self.objects = []
            self.current_object = None
            self.message = "Reset complete."
            
        elif action_id.startswith("col_"):
            # Spawn a draggable color blob
            if self.current_object:
               self.message = "Place current item first!"
               return
            
            self.current_object = DraggableObject(len(self.objects), "color_blob")
            self.current_object.color = color
            self.message = "Dragging Color..."
                
        elif action_id in ["stick1", "stick2", "paper"]:
            if self.current_object:
                self.message = "Place current item first!"
                return
                
            # Logic check
            has_stick1 = any(o.type == 'stick1' for o in self.objects)
            has_stick2 = any(o.type == 'stick2' for o in self.objects)
            
            if action_id == "stick2" and not has_stick1:
                self.message = "Need Stick 1 first!"
                return
            if action_id == "paper" and not (has_stick1 and has_stick2):
                self.message = "Need both sticks first!"
                return
                
            self.current_object = DraggableObject(len(self.objects), action_id)
            if action_id == 'paper':
                self.current_object.color = self.kite_color
            self.message = f"Placing {action_id}..."

    def process_frame(self, img):
        img = cv2.flip(img, 1)
        img = self.detector.find_hands(img)
        self.detector.find_position(img, draw=False) # Update landmarks list
        raw_hand_pos = self.detector.get_cursor_position()
        
        # Smoothing
        hand_pos = None
        if raw_hand_pos:
            if self.prev_hand_pos is None:
                self.prev_hand_pos = raw_hand_pos
            else:
                # Alpha smoothing: new = alpha * raw + (1-alpha) * prev
                # alpha 0.5 is balanced. 0.2 is very smooth but laggy. 0.8 is responsive but jittery.
                alpha = 0.5 
                px, py = self.prev_hand_pos
                rx, ry = raw_hand_pos
                nx = int(alpha * rx + (1 - alpha) * px)
                ny = int(alpha * ry + (1 - alpha) * py)
                self.prev_hand_pos = (nx, ny)
            
            hand_pos = self.prev_hand_pos
            
            # Pinch Detection (Thumb 4 and Index 8)
            length, _, _ = self.detector.find_distance(4, 8)
            
            # Hysteresis Logic to prevent glitching
            # Harder to trigger (30), harder to lose (50)
            if not self.is_pinch_active and length < 30:
                self.is_pinch_active = True
            elif self.is_pinch_active and length > 50:
                self.is_pinch_active = False
                
            is_pinching = self.is_pinch_active
            
            # Visual feedback for pinch
            if is_pinching:
                cv2.circle(img, hand_pos, 10, (0, 0, 255), -1) # Red cursor when pinching
                # Draw line between fingers to show connection
                x1, y1 = self.detector.lm_list[4][1], self.detector.lm_list[4][2]
                x2, y2 = self.detector.lm_list[8][1], self.detector.lm_list[8][2]
                cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
            else:
                cv2.circle(img, hand_pos, 10, (0, 255, 0), -1) # Green cursor otherwise
            cv2.circle(img, hand_pos, 15, (255, 255, 255), 2)
            
            # Handle Color Grabbing via Pinch
            if is_pinching:
                if not self.current_object:
                    # Check if pinching over a color button
                    for btn in self.color_buttons:
                        if btn.is_hover(hand_pos[0], hand_pos[1]):
                            # SPAWN COLOR BLOB
                            self.current_object = DraggableObject(len(self.objects), "color_blob")
                            btn_id = btn.action_id
                            # Extract color from button (it's the 'color' attr) but we used action_id matching in mouse click
                            # Let's trust the button color or map it
                            self.current_object.color = btn.color
                            self.message = "Pinch & Drag Color!"
                            break
            else:
                # Released Pinch
                if self.current_object and self.current_object.type == 'color_blob':
                    # Drop Logic
                    dropped = False
                    for obj in self.objects:
                        if obj.type == 'paper':
                             dist = np.linalg.norm(np.array(self.current_object.pos) - np.array(obj.pos))
                             if dist < 120: # If near paper
                                 obj.color = self.current_object.color
                                 self.message = "Colored with Style!"
                                 dropped = True
                                 break
                    
                    if not dropped:
                        self.message = "Released Color"
                    
                    self.current_object = None # Destroy blob

        else:
            self.prev_hand_pos = None # Reset if hand lost

        # Draw UI
        draw_transparent_rect(img, (0, 0), (250, 720), (30, 30, 30), 0.6) # Sidebar bg
        
        # Festive Text with Glow
        text = "Happy Makar Sankranti!"
        font = cv2.FONT_HERSHEY_TRIPLEX
        scale = 1.0
        pos = (380, 50)
        # Shadow/Glow
        cv2.putText(img, text, (pos[0]+2, pos[1]+2), font, scale, (0, 0, 0), 4) # Black outline
        cv2.putText(img, text, pos, font, scale, (0, 255, 255), 2) # Yellow text
        
        cv2.putText(img, "From Somyajeet", (pos[0]+150, pos[1]+40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (240, 240, 240), 1)
        
        for btn in self.buttons:
            btn.draw(img)
            
        for btn in self.color_buttons:
             btn.draw(img)
        
        # Update & Draw Objects
        for obj in self.objects:
            obj.draw(img)
            
        if self.current_object:
            self.current_object.update(hand_pos)
            self.current_object.draw(img)
            
        # Message
        cv2.putText(img, self.message, (300, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        
        # Handle Screenshot
        if self.screenshot_pending:
            cv2.imwrite(f"kite_screenshot_{int(cv2.getTickCount())}.jpg", img)
            self.screenshot_pending = False
            self.message = "Saved!"
            
        return img

    def run(self):
        self.running = True
        self.screenshot_pending = False
        
        while self.running:
            success, img = self.cap.read()
            if not success: break
            
            img = self.process_frame(img)
            
            cv2.imshow("Gravity AR Kite", img)
            if cv2.waitKey(1) & 0xFF == 27:
                break
                
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = KiteApp()
    app.run()
