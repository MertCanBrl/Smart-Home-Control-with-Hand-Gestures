import tkinter as tk
from tkinter import Label, Button
import cv2
from PIL import Image, ImageTk
import threading
from tv_control import GestureDetection
from tv_logger import log_tv_status  # En üste ekle

class LivingRoom:
    def __init__(self, root, previous_screen=None):
        self.root = root
        self.previous_screen = previous_screen
        self.root.title("Living Room")

        self.gesture_detector = GestureDetection()
        self.is_camera_running = False
        self.tv_status = "Kapali"


        self.back_button = Button(self.root, text="🔙", command=self.go_back, font=("Helvetica", 20))
        self.back_button.place(x=10, y=545, width=50, height=50)

        self.tv_button = Button(self.root, text="📺 TV Kontrol", command=self.toggle_camera)
        self.tv_button.place(x=125, y=45, width=250, height=50)

        self.tv_label = Label(self.root, text=f"TV Durumu: {self.tv_status}", font=("Helvetica", 12))
        self.tv_label.place(x=125, y=105)

        self.camera_canvas = tk.Canvas(self.root, width=400, height=300)
        self.camera_canvas.place(x=200, y=200)

        self.gesture_label = Label(self.root, text="👍 = TV Aç | 👎 = TV Kapat", font=("Helvetica", 14))
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
            is_ok, is_dislike, frame = self.gesture_detector.detect_gestures()

            if is_ok and self.tv_status == "Kapali":
                self.tv_status = "Acik"
                log_tv_status("Açık", "Living Room")

            elif is_dislike and self.tv_status == "Acik":
                self.tv_status = "Kapali"
                log_tv_status("Kapalı", "Living Room")

            self.tv_label.config(text=f"TV Durumu: {self.tv_status}")

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
