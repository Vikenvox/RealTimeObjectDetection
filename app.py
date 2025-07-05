import cv2
import numpy as np
import tkinter as tk
from customtkinter import CTk, CTkButton, CTkLabel, CTkFrame
from PIL import Image, ImageTk
from ultralytics import YOLO
import threading


class ObjectDetectionApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Real-Time Object Detection")
        self.master.geometry("800x600")

        self.cap = cv2.VideoCapture(0)
        self.model = YOLO("yolov8n.pt")  # Load the YOLOv8 model

        self.frame = CTkFrame(master)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.video_label = CTkLabel(self.frame)
        self.video_label.pack()

        self.start_button = CTkButton(self.frame, text="Start", command=self.start_detection)
        self.start_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.stop_button = CTkButton(self.frame, text="Stop", command=self.stop_detection)
        self.stop_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.running = False

    def start_detection(self):
        self.running = True
        self.detect_thread = threading.Thread(target=self.detect_objects)
        self.detect_thread.start()

    def stop_detection(self):
        self.running = False

    def detect_objects(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break

            # Perform object detection
            results = self.model(frame)
            annotated_frame = results[0].plot()

            # Convert frame to ImageTk
            image = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
            image = ImageTk.PhotoImage(image)

            # Display the image
            self.video_label.imgtk = image
            self.video_label.configure(image=image)
            self.video_label.update()

        self.cap.release()
        cv2.destroyAllWindows()


def main():
    root = CTk()
    app = ObjectDetectionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
