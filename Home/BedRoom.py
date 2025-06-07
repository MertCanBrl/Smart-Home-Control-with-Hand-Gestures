import tkinter as tk
from tkinter import Label, Button
import threading
import cv2
from PIL import Image, ImageTk

from light_control import light_control
from light_logger import log_light_status

from air_control import air_control
from air_logger import log_air_status

from tv_control import GestureDetection
from tv_logger import log_tv_status

class BedRoom:
    def __init__(self, root, previous_screen=None):
        self.root = root
        self.previous_screen = previous_screen
        self.root.title("Bedroom")
        self.root.geometry("800x650")
        self.root.resizable(False, False)

        # Light Control
        self.light_detector = light_control()
        self.is_light_camera_running = False
        self.light_status = "Kapalı"

        # Air Conditioner Control
        self.air_detector = air_control()
        self.is_air_camera_running = False
        self.air_status = "Kapalı"

        # TV Control (GestureDetection)
        self.tv_detector = GestureDetection()
        self.is_tv_camera_running = False
        self.tv_status = "Kapalı"

        # Back Button
        self.back_button = Button(
            self.root,
            text="🔙",
            command=self.go_back,
            font=("Helvetica", 20)
        )
        self.back_button.place(x=10, y=595, width=50, height=50)

        # Light Controls
        self.light_button = Button(
            self.root,
            text="💡 Lamba Kontrol",
            command=self.toggle_light_camera
        )
        self.light_button.place(x=125, y=45, width=250, height=50)

        self.light_label = Label(
            self.root,
            text=f"Lamba Durumu: {self.light_status}",
            font=("Helvetica", 12)
        )
        self.light_label.place(x=125, y=105)

        # Air Conditioner Controls
        self.air_button = Button(
            self.root,
            text="❄️ Klima Kontrol",
            command=self.toggle_air_camera
        )
        self.air_button.place(x=125, y=170, width=250, height=50)

        self.air_label = Label(
            self.root,
            text=f"Klima Durumu: {self.air_status}",
            font=("Helvetica", 12)
        )
        self.air_label.place(x=125, y=230)

        # TV Controls
        self.tv_button = Button(
            self.root,
            text="📺 TV Kontrol",
            command=self.toggle_tv_camera
        )
        self.tv_button.place(x=125, y=295, width=250, height=50)

        self.tv_label = Label(
            self.root,
            text=f"TV Durumu: {self.tv_status}",
            font=("Helvetica", 12)
        )
        self.tv_label.place(x=125, y=355)

        # Shared Camera Canvas
        self.camera_canvas = tk.Canvas(self.root, width=400, height=300)
        self.camera_canvas.place(x=200, y=400)

        # Gesture Info
        self.gesture_label = Label(
            self.root,
            text="👍 = Lamba Aç | 👎 = Lamba Kapat | 🖐️ = Klima Aç | ✊ = Klima Kapat | 🤟 = TV Aç | 🖖 = TV Kapat",
            font=("Helvetica", 14)
        )
        self.gesture_label.place(x=50, y=360)

    def toggle_light_camera(self):
        # Klima veya TV açık mı? Kapatalım
        if self.is_air_camera_running:
            self.is_air_camera_running = False
            self.air_detector.release()
            self.air_label.config(text=f"Klima Durumu: {self.air_status}")
        if self.is_tv_camera_running:
            self.is_tv_camera_running = False
            self.tv_detector.release()
            self.tv_label.config(text=f"TV Durumu: {self.tv_status}")

        if not self.is_light_camera_running:
            self.is_light_camera_running = True
            self.light_thread = threading.Thread(target=self.update_light_camera)
            self.light_thread.daemon = True
            self.light_thread.start()
        else:
            self.is_light_camera_running = False
            self.light_detector.release()

    def toggle_air_camera(self):
        # Işık veya TV açık mı? Kapatalım
        if self.is_light_camera_running:
            self.is_light_camera_running = False
            self.light_detector.release()
            self.light_label.config(text=f"Lamba Durumu: {self.light_status}")
        if self.is_tv_camera_running:
            self.is_tv_camera_running = False
            self.tv_detector.release()
            self.tv_label.config(text=f"TV Durumu: {self.tv_status}")

        if not self.is_air_camera_running:
            self.is_air_camera_running = True
            self.air_thread = threading.Thread(target=self.update_air_camera)
            self.air_thread.daemon = True
            self.air_thread.start()
        else:
            self.is_air_camera_running = False
            self.air_detector.release()

    def toggle_tv_camera(self):
        # 1) Eğer ışık veya klima kamerası açıksa kapat
        if self.is_light_camera_running:
            self.is_light_camera_running = False
            self.light_detector.release()
            self.light_label.config(text=f"Lamba Durumu: {self.light_status}")
        if self.is_air_camera_running:
            self.is_air_camera_running = False
            self.air_detector.release()
            self.air_label.config(text=f"Klima Durumu: {self.air_status}")

        # 2) TV zaten çalışıyor mu? Evet -> durdur; Hayır -> başlat
        if not self.is_tv_camera_running:
            self.is_tv_camera_running = True
            self.tv_thread = threading.Thread(target=self.update_tv_camera)
            self.tv_thread.daemon = True
            self.tv_thread.start()
        else:
            self.is_tv_camera_running = False
            self.tv_detector.release()

    def update_light_camera(self):
        while self.is_light_camera_running:
            is_on, is_off, frame = self.light_detector.detect_gestures()

            if is_on and self.light_status != "Açık":
                self.light_status = "Açık"
                log_light_status("Açık", "Bedroom")
            elif is_off and self.light_status != "Kapalı":
                self.light_status = "Kapalı"
                log_light_status("Kapalı", "Bedroom")

            self.light_label.config(text=f"Lamba Durumu: {self.light_status}")
            self.update_camera_frame(frame)

    def update_air_camera(self):
        while self.is_air_camera_running:
            air_on, air_off, frame = self.air_detector.detect_gestures()

            if air_on and self.air_status != "Açık":
                self.air_status = "Açık"
                log_air_status("Açık", "Bedroom")
            elif air_off and self.air_status != "Kapalı":
                self.air_status = "Kapalı"
                log_air_status("Kapalı", "Bedroom")

            self.air_label.config(text=f"Klima Durumu: {self.air_status}")
            self.update_camera_frame(frame)

    def update_tv_camera(self):
        while self.is_tv_camera_running:
            is_ok, is_dislike, frame = self.tv_detector.detect_gestures()

            if is_ok and self.tv_status != "Açık":
                self.tv_status = "Açık"
                log_tv_status("Açık", "Bedroom")
            elif is_dislike and self.tv_status != "Kapalı":
                self.tv_status = "Kapalı"
                log_tv_status("Kapalı", "Bedroom")

            self.tv_label.config(text=f"TV Durumu: {self.tv_status}")
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
        if self.is_tv_camera_running:
            self.is_tv_camera_running = False
            self.tv_detector.release()

        for widget in self.root.winfo_children():
            widget.destroy()
        if self.previous_screen:
            self.previous_screen(self.root)
