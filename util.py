import cv2
import numpy as np
from typing import Tuple, List

def get_dynamic_limits(bgr_color: List[int]) -> Tuple[np.ndarray, np.ndarray]:
    """Generate dynamic HSV limits from BGR color with adaptive ranges."""
    color = np.uint8([[bgr_color]])
    hsv_color = cv2.cvtColor(color, cv2.COLOR_BGR2HSV)[0][0]
    
    # Dynamic range adjustment based on brightness
    v_value = hsv_color[2]
    s_min = max(80, 255 - v_value)
    v_min = max(80, v_value - 50)
    
    lower_limit = np.array([
        max(0, hsv_color[0] - 15),
        s_min,
        v_min
    ])
    upper_limit = np.array([
        min(179, hsv_color[0] + 15),
        255,
        min(255, v_value + 50)
    ])
    return lower_limit, upper_limit

def optimize_frame(frame: np.ndarray) -> np.ndarray:
    """Optimize frame for faster processing."""
    # Resize to 640x480 for consistent processing speed
    return cv2.resize(frame, (640, 480), interpolation=cv2.INTER_AREA)