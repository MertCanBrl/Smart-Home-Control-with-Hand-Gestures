import tkinter as tk
from tkinter import Label, Button
import threading
import cv2
from PIL import Image, ImageTk

from light_control import light_control
from light_logger import log_light_status
from air_control import air_control
from air_logger import log_air_status

class BedRoom:
    def __init__(self, root, previous_screen=None):
        self.root = root
        self.previous_screen = previous_screen
        self.root.title("Bedroom")

        # Light Control
        self.light_detector = light_control()
        self.is_light_camera_running = False
        self.light_status = "Kapali"

        # Air Conditioner Control
        self.air_detector = air_control()
        self.is_air_camera_running = False
        self.air_status = "Kapali"

        # Back Button
        self.back_button = Button(self.root, text="🔙", command=self.go_back, font=("Helvetica", 20))
        self.back_button.place(x=10, y=545, width=50, height=50)

        # Light Controls
        self.light_button = Button(self.root, text="💡 Lamba Kontrol", command=self.toggle_light_camera)
        self.light_button.place(x=125, y=45, width=250, height=50)

        self.light_label = Label(self.root, text=f"Lamba Durumu: {self.light_status}", font=("Helvetica", 12))
        self.light_label.place(x=125, y=105)

        # Air Conditioner Controls
        self.air_button = Button(self.root, text="❄️ Klima Kontrol", command=self.toggle_air_camera)
        self.air_button.place(x=125, y=170, width=250, height=50)

        self.air_label = Label(self.root, text=f"Klima Durumu: {self.air_status}", font=("Helvetica", 12))
        self.air_label.place(x=125, y=230)

        # Shared Camera Canvas
        self.camera_canvas = tk.Canvas(self.root, width=400, height=300)
        self.camera_canvas.place(x=200, y=300)

        # Gesture Info
        self.gesture_label = Label(
            self.root,
            text="👍 = Lamba Aç | 👎 = Lamba Kapat | 🖐️ = Klima Aç | ✊ = Klima Kapat",
            font=("Helvetica", 14)
        )
        self.gesture_label.place(x=50, y=580)

    def toggle_light_camera(self):
        if not self.is_light_camera_running and not self.is_air_camera_running:
            self.is_light_camera_running = True
            self.light_thread = threading.Thread(target=self.update_light_camera)
            self.light_thread.daemon = True
            self.light_thread.start()
        else:
            self.is_light_camera_running = False
            self.light_detector.release()

    def toggle_air_camera(self):
        if not self.is_air_camera_running and not self.is_light_camera_running:
            self.is_air_camera_running = True
            self.air_thread = threading.Thread(target=self.update_air_camera)
            self.air_thread.daemon = True
            self.air_thread.start()
        else:
            self.is_air_camera_running = False
            self.air_detector.release()

    def update_light_camera(self):
        while self.is_light_camera_running:
            is_on, is_off, frame = self.light_detector.detect_gestures()

            if is_on and self.light_status != "Acik":
                self.light_status = "Acik"
                log_light_status("Açık", "Bedroom")

            elif is_off and self.light_status != "Kapali":
                self.light_status = "Kapali"
                log_light_status("Kapalı", "Bedroom")

            self.light_label.config(text=f"Lamba Durumu: {self.light_status}")

            self.update_camera_frame(frame)

    def update_air_camera(self):
        while self.is_air_camera_running:
            is_on, is_off, frame = self.air_detector.detect_gestures()

            if is_on and self.air_status != "Acik":
                self.air_status = "Acik"
                log_air_status("Açık", "Bedroom")

            elif is_off and self.air_status != "Kapali":
                self.air_status = "Kapali"
                log_air_status("Kapalı", "Bedroom")

            self.air_label.config(text=f"Klima Durumu: {self.air_status}")

            self.update_camera_frame(frame)

    def update_camera_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (400, 300))
        photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
        self.camera_canvas.create_image(0, 0, image=photo, anchor=tk.NW)
        self.camera_canvas.photo = photo
        self.root.update()

    def go_back(self):
        if self.is_light_camera_running:
            self.is_light_camera_running = False
            self.light_detector.release()
        if self.is_air_camera_running:
            self.is_air_camera_running = False
            self.air_detector.release()
        for widget in self.root.winfo_children():
            widget.destroy()
        if self.previous_screen:
            self.previous_screen(self.root)
