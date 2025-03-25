import cv2
import csv
from datetime import datetime
from video_processor import VideoProcessor
import logging
from util import get_dynamic_limits

# Global variables
latest_frame = None
processor = None
last_color_added = None

def mouse_callback(event, x, y, flags, param):
    global processor, latest_frame, last_color_added
    if event == cv2.EVENT_LBUTTONDOWN and latest_frame is not None:
        bgr_color = latest_frame[y, x].tolist()
        lower, upper = get_dynamic_limits(bgr_color)
        new_color_name = f"Custom_{len(processor.colors)}"
        processor.colors[new_color_name] = {
            "lower": lower.tolist(),
            "upper": upper.tolist(),
            "bgr": bgr_color
        }
        last_color_added = new_color_name
        cv2.circle(latest_frame, (x, y), 10, (255, 255, 255), 2)
        print(f"CLICK DETECTED! Added {new_color_name} with BGR {bgr_color}")
        logging.info(f"Added new color {new_color_name} with BGR {bgr_color}")

def main():
    global processor, latest_frame, last_color_added
    processor = VideoProcessor()
    
    csv_file = "logs/detection_stats.csv"
    with open(csv_file, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Color Counts", "Average Areas"])
    
    try:
        processor.start_capture()
        cv2.namedWindow("Advanced Color Tracker")
        cv2.setMouseCallback("Advanced Color Tracker", mouse_callback)
        
        while True:
            frame, detected_objects, stats = processor.process_frame()
            
            if frame is not None:
                latest_frame = frame.copy()
                
                if last_color_added:
                    cv2.putText(latest_frame, f"Added: {last_color_added}", 
                               (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                if stats:
                    stat_text = " | ".join(f"{color}: {data['count']}" for color, data in stats.items())
                    cv2.putText(latest_frame, f"Objects: {stat_text}", 
                               (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                    with open(csv_file, "a", newline='') as f:
                        writer = csv.writer(f)
                        counts = {color: data["count"] for color, data in stats.items()}
                        avg_areas = {color: round(data["avg_area"], 2) for color, data in stats.items()}
                        writer.writerow([datetime.now(), counts, avg_areas])
                
                cv2.imshow("Advanced Color Tracker", latest_frame)
                
                if detected_objects:
                    logging.info(f"Detected objects: {detected_objects}")
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
    except Exception as e:
        logging.error(f"Error in main loop: {e}")
    finally:
        processor.stop_capture()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()