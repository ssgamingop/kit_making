import cv2
import numpy as np
import math
from utils import draw_transparent_rect, draw_neon_line

class Button:
    def __init__(self, text, pos, size=(180, 60), color=(40, 40, 40), text_color=(255, 255, 255), action_id=None):
        self.text = text
        self.pos = pos
        self.size = size
        self.color = color
        self.text_color = text_color
        self.action_id = action_id
        self.hover = False

    def draw(self, img):
        x, y = self.pos
        w, h = self.size
        
        # Color based on hover (lighter if hovered)
        color = (min(self.color[0] + 40, 255), min(self.color[1] + 40, 255), min(self.color[2] + 40, 255)) if self.hover else self.color
        
        # Draw background
        cv2.rectangle(img, (x, y), (x + w, y + h), color, -1)
        
        # Draw border
        border_color = (0, 255, 255) if self.hover else (200, 200, 200)
        cv2.rectangle(img, (x, y), (x + w, y + h), border_color, 2)
        
        # Text
        cv2.putText(img, self.text, (x + 20, y + 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.text_color, 2)

    def is_hover(self, x, y):
        bx, by = self.pos
        bw, bh = self.size
        self.hover = (bx < x < bx + bw and by < y < by + bh)
        return self.hover

class DraggableObject:
    def __init__(self, obj_id, obj_type):
        self.id = obj_id
        self.type = obj_type # 'stick1', 'stick2', 'paper'
        self.pos = (0, 0)
        self.placed = False
        self.dragging = True # Starts in dragging mode when created
        self.color = (0, 255, 255) # default yellow for sticks

    def update(self, hand_pos):
        if self.dragging and hand_pos:
            self.pos = hand_pos

    def place(self):
        self.dragging = False
        self.placed = True

    def draw(self, img):
        if self.pos == (0, 0): return

        cx, cy = self.pos
        
        if self.type == 'stick1':
            # Vertical Stick (Manjha/Spine)
            cv2.line(img, (cx, cy - 90), (cx, cy + 90), self.color, 4)
            # Add neon glow
            overlay = img.copy()
            cv2.line(overlay, (cx, cy - 90), (cx, cy + 90), self.color, 8)
            cv2.addWeighted(overlay, 0.4, img, 0.6, 0, img)
            
        elif self.type == 'stick2':
            # Curved/Horizontal Stick (Kamani/Bow)
            # We simulate a curve using polylines for better visual
            pts = []
            width = 100
            curve_h = 30
            for i in range(-width, width + 1, 10):
                # Parabola-ish curve: y = a*x^2
                # normalized x from -1 to 1
                nx = i / width
                ny = - (1 - nx**2) * curve_h # curve up
                pts.append((cx + i, cy + int(ny)))
            
            pts = np.array(pts, np.int32)
            cv2.polylines(img, [pts], False, (255, 0, 255), 4)
            # Glow
            overlay = img.copy()
            cv2.polylines(overlay, [pts], False, (255, 0, 255), 8)
            cv2.addWeighted(overlay, 0.4, img, 0.6, 0, img)

        elif self.type == 'paper':
            # Diamond shape paper
            size = 90
            pts = np.array([
                (cx, cy - size),
                (cx + size, cy),
                (cx, cy + size),
                (cx - size, cy)
            ], np.int32)
            
            # Draw Tail (Wavy Ribbon)
            tail_color = (self.color[0]//2, self.color[1]//2, self.color[2]//2)
            pts_tail = []
            for i in range(15):
                tx = cx + int(15 * math.sin(i * 0.5)) 
                ty = cy + size + (i * 12)
                pts_tail.append((tx, ty))
            
            pts_tail = np.array(pts_tail, np.int32)
            cv2.polylines(img, [pts_tail], False, tail_color, 6)
            
            overlay = img.copy()
            cv2.fillPoly(overlay, [pts], self.color)
            
            # Paper Texture / Pattern (Stripes)
            # Create a localized pattern mask if possible, or just draw lines
            for i in range(-size, size, 20):
                 pt1 = (cx + i, cy - size + abs(i))
                 pt2 = (cx + i, cy + size - abs(i))
                 # Only draw if inside diamond... simplified by clipping or just careful math
                 # Let's just draw faint lines
                 cv2.line(overlay, (cx - size//2, cy - size//2 + i + 50), (cx + size//2, cy + size//2 + i + 50), (255, 255, 255), 1)

            cv2.addWeighted(overlay, 0.7, img, 0.3, 0, img) # Richer paper
            
            # Draw internal structure hints (sticks)
            # Vertical Spine
            cv2.line(img, (cx, cy - size), (cx, cy + size), (40, 40, 40), 3)
            # Horizontal Bow
            cv2.line(img, (cx - size, cy), (cx + size, cy), (40, 40, 40), 2)
            
            cv2.polylines(img, [pts], True, (255, 255, 255), 3)
            
            # Manjha (String) - Thinner and White
            start_pt = (cx, cy + size + 5)
            # Simulate slight curve in string
            mid_pt = (cx - 20, cy + 150)
            end_pt = (cx - 50, cy + 300)
            cv2.line(img, start_pt, mid_pt, (240, 240, 240), 1)
            cv2.line(img, mid_pt, end_pt, (240, 240, 240), 1)
            
            # Side Tassels (Funde) - Classic Indian Kite Feature
            tassel_color = self.color
            # Left Tassel
            lt_pts = np.array([
                (cx - size, cy),
                (cx - size - 15, cy - 10),
                (cx - size - 15, cy + 10)
            ], np.int32)
            cv2.fillPoly(img, [lt_pts], tassel_color)
            
            # Right Tassel
            rt_pts = np.array([
                (cx + size, cy),
                (cx + size + 15, cy - 10),
                (cx + size + 15, cy + 10)
            ], np.int32)
            cv2.fillPoly(img, [rt_pts], tassel_color)

        elif self.type == 'color_blob':
            # Paint bucket splash look
            cv2.circle(img, (cx, cy), 20, self.color, -1)
            cv2.circle(img, (cx, cy), 15, (255, 255, 255), 2)
            # Drips
            cv2.circle(img, (cx - 10, cy + 15), 5, self.color, -1)
            cv2.circle(img, (cx + 8, cy + 20), 4, self.color, -1)
