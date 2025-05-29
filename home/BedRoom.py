import tkinter as tk
from tkinter import Label, Button
import threading
import cv2
from PIL import Image, ImageTk

from light_control import light_control
from light_logger import log_light_status

class BedRoom:
    def __init__(self, root, previous_screen=None):
        self.root = root
        self.previous_screen = previous_screen
        self.root.title("Bedroom")

        self.gesture_detector = light_control()
        self.is_camera_running = False
        self.light_status = "Kapali"

        self.back_button = Button(self.root, text="🔙", command=self.go_back, font=("Helvetica", 20))
        self.back_button.place(x=10, y=545, width=50, height=50)

        self.light_button = Button(self.root, text="💡 Lamba Kontrol", command=self.toggle_camera)
        self.light_button.place(x=125, y=45, width=250, height=50)

        self.light_label = Label(self.root, text=f"Lamba Durumu: {self.light_status}", font=("Helvetica", 12))
        self.light_label.place(x=125, y=105)

        self.camera_canvas = tk.Canvas(self.root, width=400, height=300)
        self.camera_canvas.place(x=200, y=200)

        self.gesture_label = Label(self.root, text="👍 = Lamba Aç | 👎 = Lamba Kapat", font=("Helvetica", 14))
        self.gesture_label.place(x=125, y=150)

    def toggle_camera(self):
        if not self.is_camera_running:
            self.is_camera_running = True
            self.camera_thread = threading.Thread(target=self.update_camera)
            self.camera_thread.daemon = True
            self.camera_thread.start()
        else:
            self.is_camera_running = False
            self.gesture_detector.release()

    def update_camera(self):
        while self.is_camera_running:
            is_on, is_off, frame = self.gesture_detector.detect_gestures()

            if is_on and self.light_status != "Acik":
                self.light_status = "Acik"
                log_light_status("Açık", "Bedroom")

            elif is_off and self.light_status != "Kapali":
                self.light_status = "Kapali"
                log_light_status("Kapalı", "Bedroom")

            self.light_label.config(text=f"Lamba Durumu: {self.light_status}")

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (400, 300))
            photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.camera_canvas.create_image(0, 0, image=photo, anchor=tk.NW)
            self.camera_canvas.photo = photo

            self.root.update()

    def go_back(self):
        if self.is_camera_running:
            self.is_camera_running = False
            self.gesture_detector.release()
        for widget in self.root.winfo_children():
            widget.destroy()
        if self.previous_screen:
            self.previous_screen(self.root)
