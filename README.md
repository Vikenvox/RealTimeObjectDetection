# Real-Time Object Detection System

A high-performance, user-friendly real-time object detection application built with Python, OpenCV, and YOLOv8.

## Features

- **Real-time object detection** using YOLOv8 (nano model for optimal speed)
- **Modern GUI** with dark theme using CustomTkinter
- **Performance optimizations** for minimal lag:
  - Frame skipping for better performance
  - Optimized camera settings
  - Efficient UI updates
- **Interactive controls**:
  - Adjustable confidence threshold
  - Real-time FPS monitoring
  - Object count display
  - Start/Stop functionality
- **Error handling** and status updates

## Requirements

- Python 3.8 or higher
- Webcam/Camera connected to your computer
- Windows 10/11 (optimized for Windows)

## Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Vikenvox/RealTimeObjectDetection.git
   cd RealTimeObjectDetection
   ```

2. **Run the setup script**:
   ```powershell
   python setup.py
   ```
   
   This will:
   - Install all required dependencies
   - Check camera availability
   - Launch the application

3. **Alternative manual installation**:
   ```powershell
   pip install -r requirements.txt
   python enhanced_app.py
   ```

4. **Quick run (Windows)**:
   ```powershell
   # Run with batch file
   run_detection.bat
   
   # Or run with PowerShell script
   .\run_detection.ps1
   ```

## Quick Start

### 🚀 **Recommended: Advanced Version**
```powershell
python advanced_app.py
```
**Features**: GPU acceleration, camera flip toggle, screenshot capability, advanced performance monitoring

### 📊 **Enhanced Version**
```powershell
python enhanced_app.py
```
**Features**: Dark theme, FPS monitoring, confidence control

### 🔧 **Basic Version**
```powershell
python app.py
```
**Features**: Simple object detection with basic GUI

## Usage

1. **Launch the application**:
   - **Recommended**: Run `python advanced_app.py` for best experience
   - Alternative: Run `python enhanced_app.py` or use the setup script

2. **Controls**:
   - Click **"Start Detection"** to begin real-time object detection
   - Adjust the **confidence threshold** slider to filter detections
   - Monitor **FPS** and **object count** in real-time
   - Click **"Stop Detection"** to pause detection

3. **Performance Tips**:
   - Ensure good lighting for better detection accuracy
   - Close other applications using the camera
   - Use a dedicated GPU if available for better performance

## Technical Details

### Performance Optimizations

- **YOLOv8 Nano Model**: Fastest variant for real-time inference
- **Frame Skipping**: Processes every 2nd frame to maintain smoothness
- **Camera Buffer**: Minimized to reduce latency
- **Threading**: Separate threads for detection and UI updates
- **Optimized Resolution**: 640x480 for best speed/quality balance

### File Structure

```
RealTimeObjectDetection/
├── advanced_app.py     # 🚀 Advanced version with GPU support & best performance
├── enhanced_app.py     # Enhanced version with optimizations
├── app.py              # Basic version
├── setup.py            # Setup and installation script
├── requirements.txt    # Python dependencies
├── run_detection.bat   # Windows batch file for quick run
├── run_detection.ps1   # PowerShell script for quick run
├── yolov8n.pt          # YOLOv8 nano model weights
└── README.md          # This file
```

## Dependencies

- **ultralytics**: YOLOv8 model implementation
- **opencv-python**: Computer vision and camera handling
- **customtkinter**: Modern GUI framework
- **PIL (Pillow)**: Image processing
- **numpy**: Numerical operations
- **torch/torchvision**: Deep learning backend

## Troubleshooting

### Camera Issues
- Ensure your camera is not being used by another application
- Check camera permissions in Windows settings
- Try different camera indices if you have multiple cameras

### Performance Issues
- Close unnecessary applications
- Ensure adequate lighting
- Lower the confidence threshold if too many false positives
- Consider using a dedicated GPU

### Installation Issues
- Ensure Python 3.8+ is installed
- Use `pip install --upgrade pip` before installing dependencies
- Run PowerShell as Administrator if permission issues occur

## Features Comparison

| Feature | Basic App | Enhanced App |
|---------|-----------|--------------|
| GUI Framework | Basic CustomTkinter | Advanced CustomTkinter |
| Performance | Standard | Optimized |
| FPS Display | No | Yes |
| Object Count | No | Yes |
| Confidence Control | No | Yes |
| Error Handling | Basic | Comprehensive |
| Threading | Basic | Optimized |
| Camera Settings | Default | Optimized |

## Performance Benchmarks

- **FPS**: 15-30+ (depends on hardware)
- **Latency**: <100ms
- **Memory Usage**: ~200-400MB
- **CPU Usage**: 20-60% (depends on hardware)

## License

This project is for educational and personal use. YOLOv8 is subject to Ultralytics license terms.
