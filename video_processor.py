import cv2
import numpy as np
import json
import logging
import time
from threading import Thread, Lock
from util import get_dynamic_limits, optimize_frame
from typing import Dict, Tuple, Optional

class VideoProcessor:
    def __init__(self, config_path: str = "config.json"):
        logging.basicConfig(
            filename="logs/color_tracker.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.load_config(config_path)
        self.cap = None
        self.frame = None
        self.running = False
        self.thread = None
        self.lock = Lock()
        self.fps = 0
        self.last_time = time.time()
        self.object_tracks = {}  # {color: {id: {"centroid": (x, y), "area": area}}}
        self.next_id = 0  # For assigning new IDs

    def load_config(self, config_path: str) -> None:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            self.video_source = config["video_source"]
            self.fallback_source = config.get("fallback_source")
            self.min_contour_area = config["min_contour_area"]
            self.frame_rate_target = config["frame_rate_target"]
            self.colors = config["colors"]
            logging.info("Configuration loaded successfully")
        except Exception as e:
            logging.error(f"Failed to load config: {e}")
            raise

    def start_capture(self) -> None:
        """Start video capture with fallback support."""
        self.cap = cv2.VideoCapture(self.video_source)
        if not self.cap.isOpened() and self.fallback_source:
            logging.warning(f"Primary source failed, using fallback: {self.fallback_source}")
            self.cap = cv2.VideoCapture(self.fallback_source)
        if not self.cap.isOpened():
            raise RuntimeError("Could not open any video source")
        
        self.running = True
        self.thread = Thread(target=self._capture_loop)
        self.thread.start()
        logging.info(f"Started video capture from {self.video_source}")

    def _capture_loop(self) -> None:
        """Continuous frame capture loop."""
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            
            with self.lock:
                self.frame = optimize_frame(frame)
            time.sleep(max(0, 1/self.frame_rate_target - (time.time() - self.last_time)))
            self.fps = 1/(time.time() - self.last_time)
            self.last_time = time.time()

    def stop_capture(self) -> None:
        """Stop video capture and cleanup."""
        self.running = False
        if self.thread:
            self.thread.join()
        if self.cap:
            self.cap.release()
        logging.info("Video capture stopped")

    def _track_object(self, color: str, centroid: tuple, area: float) -> int:
        """Assign or update an ID for a detected object."""
        if color not in self.object_tracks:
            self.object_tracks[color] = {}
        
        tracks = self.object_tracks[color]
        min_dist = float('inf')
        closest_id = None
        
        # Find the closest existing object
        for obj_id, data in tracks.items():
            dist = np.linalg.norm(np.array(centroid) - np.array(data["centroid"]))
            if dist < min_dist and dist < 50:  # 50-pixel threshold for matching
                min_dist = dist
                closest_id = obj_id
        
        # If no match, create a new ID
        if closest_id is None:
            closest_id = self.next_id
            self.next_id += 1
        
        # Update the track
        tracks[closest_id] = {"centroid": centroid, "area": area}
        
        # Clean up old tracks (optional: remove if not seen for a while)
        to_remove = [obj_id for obj_id, data in tracks.items() 
                    if obj_id != closest_id and np.linalg.norm(np.array(centroid) - np.array(data["centroid"])) > 100]
        for obj_id in to_remove:
            tracks.pop(obj_id)
        
        return closest_id

    def process_frame(self) -> Tuple[Optional[np.ndarray], Dict[str, list], Dict[str, float]]:
        """Process frame for multiple color detection with tracking."""
        with self.lock:
            if self.frame is None:
                return None, {}, {}
            frame = self.frame.copy()
        
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        detected_objects = {}
        stats = {}

        for color_name, color_data in self.colors.items():
            lower = np.array(color_data["lower"], dtype=np.uint8)
            upper = np.array(color_data["upper"], dtype=np.uint8)
            bgr = color_data["bgr"]
            
            mask = cv2.inRange(hsv, lower, upper)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5,5), np.uint8))
            
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            objects = []
            total_area = 0
            
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area > self.min_contour_area:
                    x, y, w, h = cv2.boundingRect(cnt)
                    centroid = (x + w//2, y + h//2)  # Center of the object
                    obj_id = self._track_object(color_name, centroid, area)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), bgr, 2)
                    cv2.putText(frame, f"{color_name} #{obj_id} ({int(area)})", 
                              (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, bgr, 2)
                    objects.append({"x": x, "y": y, "w": w, "h": h, "area": area, "id": obj_id})
                    total_area += area
            
            if objects:
                detected_objects[color_name] = objects
                stats[color_name] = {
                    "count": len(objects),
                    "avg_area": total_area / len(objects) if objects else 0
                }

        cv2.putText(frame, f"FPS: {self.fps:.1f}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        return frame, detected_objects, stats