import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
from ultralytics import YOLO
import threading
import time
from collections import deque


class OptimizedObjectDetectionApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Enhanced Real-Time Object Detection")
        self.master.geometry("1200x800")
        
        # Set appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Initialize variables
        self.cap = None
        self.model = None
        self.running = False
        self.detection_thread = None
        self.fps_counter = deque(maxlen=30)
        self.last_frame_time = time.time()
        
        # Performance settings
        self.confidence_threshold = 0.5
        self.frame_skip = 2  # Process every nth frame for better performance
        self.frame_counter = 0
        
        self.setup_ui()
        self.load_model()
        
    def setup_ui(self):
        # Main container
        self.main_frame = ctk.CTkFrame(self.master)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control panel
        self.control_frame = ctk.CTkFrame(self.main_frame)
        self.control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Start/Stop buttons
        self.start_button = ctk.CTkButton(
            self.control_frame, 
            text="Start Detection", 
            command=self.start_detection,
            width=120,
            height=40
        )
        self.start_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.stop_button = ctk.CTkButton(
            self.control_frame, 
            text="Stop Detection", 
            command=self.stop_detection,
            width=120,
            height=40,
            state="disabled"
        )
        self.stop_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # FPS label
        self.fps_label = ctk.CTkLabel(
            self.control_frame, 
            text="FPS: 0",
            font=("Arial", 14, "bold")
        )
        self.fps_label.pack(side=tk.LEFT, padx=20, pady=5)
        
        # Detection count label
        self.detection_label = ctk.CTkLabel(
            self.control_frame, 
            text="Objects: 0",
            font=("Arial", 14, "bold")
        )
        self.detection_label.pack(side=tk.LEFT, padx=20, pady=5)
        
        # Confidence threshold slider
        self.confidence_frame = ctk.CTkFrame(self.control_frame)
        self.confidence_frame.pack(side=tk.RIGHT, padx=5, pady=5)
        
        self.confidence_label = ctk.CTkLabel(
            self.confidence_frame, 
            text="Confidence:"
        )
        self.confidence_label.pack(side=tk.LEFT, padx=5)
        
        self.confidence_slider = ctk.CTkSlider(
            self.confidence_frame,
            from_=0.1,
            to=1.0,
            number_of_steps=9,
            command=self.update_confidence
        )
        self.confidence_slider.set(0.5)
        self.confidence_slider.pack(side=tk.LEFT, padx=5)
        
        self.confidence_value_label = ctk.CTkLabel(
            self.confidence_frame,
            text="0.5"
        )
        self.confidence_value_label.pack(side=tk.LEFT, padx=5)
        
        # Video display frame
        self.video_frame = ctk.CTkFrame(self.main_frame)
        self.video_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.video_label = ctk.CTkLabel(self.video_frame, text="Camera feed will appear here")
        self.video_label.pack(expand=True)
        
        # Status bar
        self.status_frame = ctk.CTkFrame(self.main_frame)
        self.status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame, 
            text="Ready - Click 'Start Detection' to begin",
            font=("Arial", 12)
        )
        self.status_label.pack(side=tk.LEFT, padx=5, pady=5)
        
    def load_model(self):
        try:
            self.status_label.configure(text="Loading YOLO model...")
            self.master.update()
            self.model = YOLO("yolov8n.pt")  # Fast nano model for real-time
            self.status_label.configure(text="Model loaded successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load model: {str(e)}")
            self.status_label.configure(text="Error loading model")
    
    def update_confidence(self, value):
        self.confidence_threshold = float(value)
        self.confidence_value_label.configure(text=f"{value:.1f}")
    
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
            
            self.running = True
            self.detection_thread = threading.Thread(target=self.detection_loop, daemon=True)
            self.detection_thread.start()
            
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            self.status_label.configure(text="Detection running...")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start detection: {str(e)}")
    
    def stop_detection(self):
        self.running = False
        if self.cap:
            self.cap.release()
        
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.status_label.configure(text="Detection stopped")
        self.fps_label.configure(text="FPS: 0")
        self.detection_label.configure(text="Objects: 0")
    
    def detection_loop(self):
        while self.running:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                # Skip frames for better performance
                self.frame_counter += 1
                if self.frame_counter % self.frame_skip != 0:
                    continue
                
                # Perform detection
                results = self.model(frame, conf=self.confidence_threshold, verbose=False)
                
                # Count detections
                detection_count = len(results[0].boxes) if results[0].boxes is not None else 0
                
                # Draw bounding boxes and labels
                annotated_frame = results[0].plot()
                
                # Calculate FPS
                current_time = time.time()
                fps = 1 / (current_time - self.last_frame_time)
                self.fps_counter.append(fps)
                avg_fps = sum(self.fps_counter) / len(self.fps_counter)
                self.last_frame_time = current_time
                
                # Update UI in main thread
                self.master.after(0, self.update_ui, annotated_frame, avg_fps, detection_count)
                
            except Exception as e:
                print(f"Detection error: {e}")
                break
        
        if self.cap:
            self.cap.release()
    
    def update_ui(self, frame, fps, detection_count):
        try:
            # Resize frame for display
            height, width = frame.shape[:2]
            max_width, max_height = 800, 600
            
            if width > max_width or height > max_height:
                scale = min(max_width/width, max_height/height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                frame = cv2.resize(frame, (new_width, new_height))
            
            # Convert to RGB and then to ImageTk
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            tk_image = ImageTk.PhotoImage(pil_image)
            
            # Update video display
            self.video_label.configure(image=tk_image)
            self.video_label.image = tk_image  # Keep a reference
            
            # Update labels
            self.fps_label.configure(text=f"FPS: {fps:.1f}")
            self.detection_label.configure(text=f"Objects: {detection_count}")
            
        except Exception as e:
            print(f"UI update error: {e}")
    
    def on_closing(self):
        self.stop_detection()
        self.master.destroy()


def main():
    root = ctk.CTk()
    app = OptimizedObjectDetectionApp(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    root.mainloop()


if __name__ == "__main__":
    main()
