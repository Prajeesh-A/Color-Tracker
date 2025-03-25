

# 🎨 Advanced Color Tracker  

A **real-time color detection and tracking system** using OpenCV. This project detects, tracks, and logs objects of specific colors from a video source (webcam or file). It also allows **dynamic color addition** by clicking on the video feed.  

## 🏆 Features  
✅ **Real-time object detection & tracking**  
✅ **Mouse-based dynamic color addition**  
✅ **Configurable color detection thresholds**  
✅ **Object tracking with unique IDs**  
✅ **Logging of detected objects (CSV & logs)**  
✅ **Multi-threaded video processing for smooth performance**  

---

## 📌 Table of Contents  
- [Installation](#installation)  
- [Configuration](#configuration)  
- [Usage](#usage)  
- [Project Structure](#project-structure)  
- [How It Works](#how-it-works)  
- [Future Enhancements](#future-enhancements)  
- [License](#license)  

---

## 🔧 Installation  

1️⃣ **Clone the repository**  
```bash
git clone https://github.com/Prajeesh-A/Color Tracker.git  
cd Color Tracker
```  

2️⃣ **Install dependencies**  
```bash
pip install -r requirements.txt  
```  

---

## ⚙️ Configuration  

Modify `config.json` to adjust settings:  
```json
{
    "video_source": "http://192.168.1.35:4747/video",
    "fallback_source": "test_video.mp4",
    "min_contour_area": 500,
    "frame_rate_target": 30,
    "colors": {
        "Red": {"lower": [0, 120, 70], "upper": [10, 255, 255], "bgr": [0, 0, 255]},
        "Green": {"lower": [40, 40, 40], "upper": [80, 255, 255], "bgr": [0, 255, 0]}
    }
}
```  
🔹 **video_source** → Primary video feed (Webcam, IP camera, or file)  
🔹 **fallback_source** → Backup video file in case the main source fails  
🔹 **min_contour_area** → Minimum size for detecting objects  
🔹 **frame_rate_target** → FPS limit for smoother processing  
🔹 **colors** → Color detection thresholds  

---

## 🎬 Usage  

Run the main script:  
```bash
python main.py  
```  

### 🎮 Controls  
🖱 **Click on a color** in the video to add it dynamically  
🔴 **Press `q`** to quit the application  

---

## 📂 Project Structure  

```
📦 your-repository
├── 📄 main.py             # Main entry point (GUI & event handling)
├── 📄 video_processor.py  # Video capture & color detection
├── 📄 util.py             # Helper functions (color conversion, frame optimization)
├── 📄 config.json         # Configuration settings
├── 📂 logs/               # Stores logs & detection stats
└── 📂 assets/             # (Optional) Sample videos or images
```  

---

## 🛠 How It Works  

1️⃣ **Video Capture**  
- The system reads a video stream (webcam/IP camera/file).  
- Frames are resized & optimized for processing.  

2️⃣ **Color Detection**  
- The frame is converted to **HSV color space**.  
- Predefined color thresholds (from `config.json`) are applied.  
- The system detects objects using **contour detection**.  

3️⃣ **Object Tracking**  
- Each detected object is **assigned an ID**.  
- Objects are tracked over multiple frames using **centroid tracking**.  

4️⃣ **Logging & Visualization**  
- Object detection stats are stored in **CSV logs**.  
- **Bounding boxes & labels** are drawn on the video feed.  

---

## 🔮 Future Enhancements  
🚀 **Adaptive color calibration** – Automatically adjust color thresholds  
🚀 **Object classification** – Identify specific objects (e.g., apples, bananas)  
🚀 **Web dashboard** – View tracking results in a browser  
🚀 **Cloud integration** – Upload stats to a remote database  

---

## 📝 License  

This project is licensed under the **MIT License**.  

📧 **Developed by [Prajeesh A]** | 🌍 **[Your Website](prajeesh-a.github.io)**  

---
