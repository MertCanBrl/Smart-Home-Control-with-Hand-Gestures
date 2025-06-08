import tkinter as tk
from tkinter import Label, Button
import cv2
from PIL import Image, ImageTk
import threading
from curtain_control import curtain_control
from curtain_logger import log_curtain_status

from light_control import light_control
from light_logger import log_light_status

class Kitchen:
    def __init__(self, root, previous_screen=None):
        self.root = root
        self.previous_screen = previous_screen
        self.root.title("Kitchen")

        # Perde Control
        self.curtain_detector = curtain_control()
        self.is_curtain_camera_running = False
        self.curtain_status = "Kapali"

        # Lamba Control
        self.light_detector = light_control()
        self.is_light_camera_running = False
        self.light_status = "Kapali"

        # Back button
        self.back_button = Button(self.root, text="🔙", command=self.go_back, font=("Helvetica", 20))
        self.back_button.place(x=10, y=545, width=50, height=50)

        # Light Controls
        self.light_button = Button(self.root, text="💡 Lamba Kontrol", command=self.toggle_light_camera)
        self.light_button.place(x=125, y=45, width=250, height=50)

        self.light_label = Label(self.root, text=f"Lamba Durumu: {self.light_status}", font=("Helvetica", 12))
        self.light_label.place(x=125, y=105)

        # Curtain Controls
        self.curtain_button = Button(self.root, text="🪟 Perde Kontrol", command=self.toggle_curtain_camera)
        self.curtain_button.place(x=125, y=165, width=250, height=50)

        self.curtain_label = Label(self.root, text=f"Perde Durumu: {self.curtain_status}", font=("Helvetica", 12))
        self.curtain_label.place(x=125, y=225)

        self.camera_canvas = tk.Canvas(self.root, width=400, height=300)
        self.camera_canvas.place(x=200, y=280)

        self.gesture_label = Label(self.root, text="🖐️ = Aç | ✊ = Kapat", font=("Helvetica", 14))
        self.gesture_label.place(x=125, y=240)

    def toggle_light_camera(self):
        if not self.is_light_camera_running:
            self.is_light_camera_running = True
            self.light_thread = threading.Thread(target=self.update_light_camera)
            self.light_thread.daemon = True
            self.light_thread.start()
        else:
            self.is_light_camera_running = False
            self.light_detector.release()

    def toggle_curtain_camera(self):
        if not self.is_curtain_camera_running:
            self.is_curtain_camera_running = True
            self.curtain_thread = threading.Thread(target=self.update_curtain_camera)
            self.curtain_thread.daemon = True
            self.curtain_thread.start()
        else:
            self.is_curtain_camera_running = False
            self.curtain_detector.release()

    def update_curtain_camera(self):
        while self.is_curtain_camera_running:
            is_open, is_close, frame = self.curtain_detector.detect_gestures()

            if is_open and self.curtain_status == "Kapali":
                self.curtain_status = "Acik"
                log_curtain_status("Açık", "Kitchen")

            elif is_close and self.curtain_status == "Acik":
                self.curtain_status = "Kapali"
                log_curtain_status("Kapalı", "Kitchen")

            self.curtain_label.config(text=f"Perde Durumu: {self.curtain_status}")

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (400, 300))
            photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.camera_canvas.create_image(0, 0, image=photo, anchor=tk.NW)
            self.camera_canvas.photo = photo

            self.root.update()

    def update_light_camera(self):
        while self.is_light_camera_running:
            is_on, is_off, frame = self.light_detector.detect_gestures()

            if is_on and self.light_status != "Acik":
                self.light_status = "Acik"
                log_light_status("Açık", "Kitchen")

            elif is_off and self.light_status != "Kapali":
                self.light_status = "Kapali"
                log_light_status("Kapalı", "Kitchen")

            self.light_label.config(text=f"Lamba Durumu: {self.light_status}")

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (400, 300))
            photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.camera_canvas.create_image(0, 0, image=photo, anchor=tk.NW)
            self.camera_canvas.photo = photo

            self.root.update()

    def go_back(self):
        if self.is_curtain_camera_running:
            self.is_curtain_camera_running = False
            self.curtain_detector.release()
        if self.is_light_camera_running:
            self.is_light_camera_running = False
            self.light_detector.release()
        for widget in self.root.winfo_children():
            widget.destroy()
        if self.previous_screen:
            self.previous_screen(self.root)
