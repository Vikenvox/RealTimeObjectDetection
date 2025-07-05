import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
from ultralytics import YOLO
import threading
import time
import torch
from collections import deque
from queue import Queue, Empty
import logging


class AdvancedObjectDetectionApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Advanced Real-Time Object Detection")
        self.master.geometry("1400x900")
        
        # Set appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Initialize variables
        self.cap = None
        self.model = None
        self.running = False
        self.detection_thread = None
        self.ui_update_thread = None
        
        # Performance monitoring
        self.fps_counter = deque(maxlen=30)
        self.last_frame_time = time.time()
        self.processed_frames = 0
        self.total_frames = 0
        
        # Threading queues for better performance
        self.frame_queue = Queue(maxsize=3)
        self.result_queue = Queue(maxsize=3)
        
        # Settings
        self.confidence_threshold = 0.5
        self.iou_threshold = 0.45
        self.max_detections = 100
        self.frame_skip = 1
        self.flip_camera = True  # Start with flipped camera (most common need)
        
        # Device detection
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # Detection history
        self.detection_history = []
        
        self.setup_ui()
        self.load_model()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def setup_ui(self):
        # Main container
        self.main_frame = ctk.CTkFrame(self.master)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top control panel
        self.top_control_frame = ctk.CTkFrame(self.main_frame)
        self.top_control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Device info
        device_info = f"Device: {self.device.upper()}"
        if self.device == 'cuda':
            device_info += f" ({torch.cuda.get_device_name(0)})"
        
        self.device_label = ctk.CTkLabel(
            self.top_control_frame,
            text=device_info,
            font=("Arial", 12, "bold")
        )
        self.device_label.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Start/Stop buttons
        self.start_button = ctk.CTkButton(
            self.top_control_frame,
            text="🚀 Start Detection",
            command=self.start_detection,
            width=150,
            height=40,
            font=("Arial", 12, "bold")
        )
        self.start_button.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.stop_button = ctk.CTkButton(
            self.top_control_frame,
            text="⏹️ Stop Detection",
            command=self.stop_detection,
            width=150,
            height=40,
            font=("Arial", 12, "bold"),
            state="disabled"
        )
        self.stop_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Performance metrics
        self.metrics_frame = ctk.CTkFrame(self.top_control_frame)
        self.metrics_frame.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # FPS display
        self.fps_label = ctk.CTkLabel(
            self.metrics_frame,
            text="FPS: 0",
            font=("Arial", 14, "bold")
        )
        self.fps_label.grid(row=0, column=0, padx=5, pady=2)
        
        # Detection count
        self.detection_label = ctk.CTkLabel(
            self.metrics_frame,
            text="Objects: 0",
            font=("Arial", 14, "bold")
        )
        self.detection_label.grid(row=0, column=1, padx=5, pady=2)
        
        # Processing efficiency
        self.efficiency_label = ctk.CTkLabel(
            self.metrics_frame,
            text="Efficiency: 0%",
            font=("Arial", 14, "bold")
        )
        self.efficiency_label.grid(row=1, column=0, columnspan=2, padx=5, pady=2)
        
        # Settings panel
        self.settings_frame = ctk.CTkFrame(self.main_frame)
        self.settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Confidence threshold
        self.confidence_frame = ctk.CTkFrame(self.settings_frame)
        self.confidence_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        ctk.CTkLabel(self.confidence_frame, text="Confidence:").pack(side=tk.LEFT, padx=5)
        self.confidence_slider = ctk.CTkSlider(
            self.confidence_frame,
            from_=0.1,
            to=0.9,
            number_of_steps=8,
            command=self.update_confidence,
            width=100
        )
        self.confidence_slider.set(0.5)
        self.confidence_slider.pack(side=tk.LEFT, padx=5)
        
        self.confidence_value_label = ctk.CTkLabel(
            self.confidence_frame,
            text="0.5"
        )
        self.confidence_value_label.pack(side=tk.LEFT, padx=5)
        
        # IOU threshold
        self.iou_frame = ctk.CTkFrame(self.settings_frame)
        self.iou_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        ctk.CTkLabel(self.iou_frame, text="IOU:").pack(side=tk.LEFT, padx=5)
        self.iou_slider = ctk.CTkSlider(
            self.iou_frame,
            from_=0.1,
            to=0.9,
            number_of_steps=8,
            command=self.update_iou,
            width=100
        )
        self.iou_slider.set(0.45)
        self.iou_slider.pack(side=tk.LEFT, padx=5)
        
        self.iou_value_label = ctk.CTkLabel(
            self.iou_frame,
            text="0.45"
        )
        self.iou_value_label.pack(side=tk.LEFT, padx=5)
        
        # Max detections
        self.max_det_frame = ctk.CTkFrame(self.settings_frame)
        self.max_det_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        ctk.CTkLabel(self.max_det_frame, text="Max Objects:").pack(side=tk.LEFT, padx=5)
        self.max_det_var = tk.StringVar(value="100")
        self.max_det_entry = ctk.CTkEntry(
            self.max_det_frame,
            textvariable=self.max_det_var,
            width=60
        )
        self.max_det_entry.pack(side=tk.LEFT, padx=5)
        self.max_det_entry.bind('<Return>', self.update_max_detections)
        
        # Camera flip toggle button
        flip_status = "ON" if self.flip_camera else "OFF"
        self.flip_button = ctk.CTkButton(
            self.settings_frame,
            text=f"🔄 Flip: {flip_status}",
            command=self.toggle_camera_flip,
            width=110,
            height=30
        )
        self.flip_button.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Screenshot button
        self.screenshot_button = ctk.CTkButton(
            self.settings_frame,
            text="📸 Screenshot",
            command=self.take_screenshot,
            width=100,
            height=30
        )
        self.screenshot_button.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Video display frame
        self.video_frame = ctk.CTkFrame(self.main_frame)
        self.video_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.video_label = ctk.CTkLabel(
            self.video_frame,
            text="🎥 Camera feed will appear here\n\nClick 'Start Detection' to begin",
            font=("Arial", 16)
        )
        self.video_label.pack(expand=True)
        
        # Status bar
        self.status_frame = ctk.CTkFrame(self.main_frame)
        self.status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="🟢 Ready - Enhanced with GPU acceleration support",
            font=("Arial", 12)
        )
        self.status_label.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Model info
        self.model_info_label = ctk.CTkLabel(
            self.status_frame,
            text="Model: Loading...",
            font=("Arial", 10)
        )
        self.model_info_label.pack(side=tk.RIGHT, padx=5, pady=5)
        
    def load_model(self):
        try:
            self.status_label.configure(text="🔄 Loading YOLO model...")
            self.master.update()
            
            # Load model and move to appropriate device
            self.model = YOLO("yolov8n.pt")
            if self.device == 'cuda':
                self.model.to('cuda')
            
            self.status_label.configure(text=f"✅ Model loaded successfully on {self.device.upper()}")
            self.model_info_label.configure(text=f"Model: YOLOv8n ({self.device.upper()})")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load model: {str(e)}")
            self.status_label.configure(text="❌ Error loading model")
            self.logger.error(f"Model loading error: {e}")
    
    def update_confidence(self, value):
        self.confidence_threshold = float(value)
        self.confidence_value_label.configure(text=f"{value:.2f}")
    
    def update_iou(self, value):
        self.iou_threshold = float(value)
        self.iou_value_label.configure(text=f"{value:.2f}")
    
    def update_max_detections(self, event=None):
        try:
            self.max_detections = int(self.max_det_var.get())
        except ValueError:
            self.max_det_var.set("100")
            self.max_detections = 100
    
    def toggle_camera_flip(self):
        """Toggle camera flip horizontally"""
        self.flip_camera = not self.flip_camera
        flip_status = "ON" if self.flip_camera else "OFF"
        self.flip_button.configure(text=f"🔄 Flip: {flip_status}")
        self.status_label.configure(text=f"🔄 Camera flip: {flip_status}")
    
    def start_detection(self):
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                messagebox.showerror("Error", "Cannot open camera")
                return
            
            # Optimize camera settings for better performance
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Clear queues
            while not self.frame_queue.empty():
                self.frame_queue.get()
            while not self.result_queue.empty():
                self.result_queue.get()
            
            self.running = True
            self.processed_frames = 0
            self.total_frames = 0
            
            # Start threads
            self.detection_thread = threading.Thread(target=self.detection_loop, daemon=True)
            self.ui_update_thread = threading.Thread(target=self.ui_update_loop, daemon=True)
            
            self.detection_thread.start()
            self.ui_update_thread.start()
            
            # Clear the initial text when detection starts
            self.video_label.configure(text="")
            
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            self.status_label.configure(text="🔴 Detection running...")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start detection: {str(e)}")
            self.logger.error(f"Detection start error: {e}")
    
    def stop_detection(self):
        self.running = False
        if self.cap:
            self.cap.release()
        
        # Clear queues
        while not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
            except Empty:
                break
        while not self.result_queue.empty():
            try:
                self.result_queue.get_nowait()
            except Empty:
                break
        
        # Remove image completely - just black background
        self.video_label.configure(
            image="",  # Remove image completely
            text=""   # No text either
        )
        self.video_label.image = None  # Clear image reference completely
        
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.status_label.configure(text="⏹️ Detection stopped")
        self.fps_label.configure(text="FPS: 0")
        self.detection_label.configure(text="Objects: 0")
        self.efficiency_label.configure(text="Efficiency: 0%")
    
    def detection_loop(self):
        """Main detection loop running in separate thread"""
        while self.running:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                self.total_frames += 1
                
                # Add frame to queue (non-blocking)
                try:
                    self.frame_queue.put_nowait(frame)
                except:
                    # Queue is full, skip this frame
                    continue
                
                # Process frame if queue not empty
                try:
                    frame_to_process = self.frame_queue.get_nowait()
                    
                    # Apply camera flip if enabled
                    if self.flip_camera:
                        frame_to_process = cv2.flip(frame_to_process, 1)  # Horizontal flip
                    
                    # Perform detection with optimized settings
                    results = self.model(
                        frame_to_process,
                        conf=self.confidence_threshold,
                        iou=self.iou_threshold,
                        max_det=self.max_detections,
                        verbose=False,
                        device=self.device
                    )
                    
                    self.processed_frames += 1
                    
                    # Count detections
                    detection_count = len(results[0].boxes) if results[0].boxes is not None else 0
                    
                    # Store detection data
                    detection_data = {
                        'timestamp': time.time(),
                        'count': detection_count,
                        'frame': frame_to_process,
                        'results': results
                    }
                    
                    # Add to history (keep last 10)
                    self.detection_history.append(detection_data)
                    if len(self.detection_history) > 10:
                        self.detection_history.pop(0)
                    
                    # Add result to queue
                    try:
                        self.result_queue.put_nowait(detection_data)
                    except:
                        # Queue is full, skip this result
                        pass
                        
                except Empty:
                    # No frame to process
                    time.sleep(0.01)
                    continue
                
            except Exception as e:
                self.logger.error(f"Detection error: {e}")
                break
        
        if self.cap:
            self.cap.release()
    
    def ui_update_loop(self):
        """UI update loop running in separate thread"""
        while self.running:
            try:
                # Get result from queue
                detection_data = self.result_queue.get(timeout=0.1)
                
                # Calculate FPS
                current_time = time.time()
                fps = 1 / (current_time - self.last_frame_time)
                self.fps_counter.append(fps)
                avg_fps = sum(self.fps_counter) / len(self.fps_counter)
                self.last_frame_time = current_time
                
                # Calculate efficiency
                efficiency = (self.processed_frames / max(self.total_frames, 1)) * 100
                
                # Update UI in main thread
                self.master.after(0, self.update_ui, detection_data, avg_fps, efficiency)
                
            except Empty:
                continue
            except Exception as e:
                self.logger.error(f"UI update error: {e}")
                break
    
    def update_ui(self, detection_data, fps, efficiency):
        try:
            frame = detection_data['frame']
            results = detection_data['results']
            detection_count = detection_data['count']
            
            # Draw bounding boxes and labels
            annotated_frame = results[0].plot()
            
            # Resize frame for display
            height, width = annotated_frame.shape[:2]
            max_width, max_height = 900, 600
            
            if width > max_width or height > max_height:
                scale = min(max_width/width, max_height/height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                annotated_frame = cv2.resize(annotated_frame, (new_width, new_height))
            
            # Convert to RGB and then to ImageTk
            rgb_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            tk_image = ImageTk.PhotoImage(pil_image)
            
            # Update video display
            self.video_label.configure(image=tk_image)
            self.video_label.image = tk_image  # Keep a reference
            
            # Update labels
            self.fps_label.configure(text=f"FPS: {fps:.1f}")
            self.detection_label.configure(text=f"Objects: {detection_count}")
            self.efficiency_label.configure(text=f"Efficiency: {efficiency:.1f}%")
            
        except Exception as e:
            self.logger.error(f"UI update error: {e}")
    
    def take_screenshot(self):
        """Take a screenshot of current detection"""
        if self.detection_history:
            try:
                latest_detection = self.detection_history[-1]
                results = latest_detection['results']
                annotated_frame = results[0].plot()
                
                # Save screenshot
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"detection_screenshot_{timestamp}.png"
                cv2.imwrite(filename, annotated_frame)
                
                self.status_label.configure(text=f"📸 Screenshot saved: {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save screenshot: {str(e)}")
    
    def on_closing(self):
        self.stop_detection()
        self.master.destroy()


def main():
    root = ctk.CTk()
    app = AdvancedObjectDetectionApp(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    root.mainloop()


if __name__ == "__main__":
    main()
