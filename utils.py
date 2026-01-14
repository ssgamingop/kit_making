import cv2
import numpy as np

def overlay_transparent(background, overlay, x, y):
    """
    Overlays a transparent PNG onto the background at position (x, y).
    """
    bg_h, bg_w, _ = background.shape
    h, w, c = overlay.shape

    if x >= bg_w or y >= bg_h:
        return background

    if x + w > bg_w:
        w = bg_w - x
        overlay = overlay[:, :w]

    if y + h > bg_h:
        h = bg_h - y
        overlay = overlay[:h]

    if c < 4:
        return background

    alpha = overlay[:, :, 3] / 255.0
    
    # 3 channels for BGR
    for c in range(0, 3):
        background[y:y+h, x:x+w, c] = (alpha * overlay[:, :, c] +
                                      (1.0 - alpha) * background[y:y+h, x:x+w, c])

    return background

def draw_transparent_rect(img, pt1, pt2, color, alpha=0.5):
    """
    Draws a transparent rectangle on the image.
    """
    overlay = img.copy()
    cv2.rectangle(overlay, pt1, pt2, color, -1)
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
    return img

def create_kite_mask(shape, center, size, color):
    """
    Creates a kite shape mask.
    """
    mask = np.zeros(shape[:2], dtype=np.uint8)
    cx, cy = center
    
    points = np.array([
        (cx, cy - size),
        (cx + size, cy),
        (cx, cy + size),
        (cx - size, cy)
    ], np.int32)
    
    cv2.fillPoly(mask, [points], 255)
    return mask

def draw_neon_line(img, pt1, pt2, color, thickness=2, glow_radius=10):
    """
    Draws a line with a neon glow effect.
    """
    # Draw glow
    overlay = img.copy()
    cv2.line(overlay, pt1, pt2, color, thickness + glow_radius)
    cv2.addWeighted(overlay, 0.4, img, 0.6, 0, img)
    # Draw core
    cv2.line(img, pt1, pt2, (255, 255, 255), thickness)
    return img
