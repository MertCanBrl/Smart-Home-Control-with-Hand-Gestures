import tkinter as tk
from tkinter import Label, Button
import sqlite3

import threading
import cv2
from PIL import Image, ImageTk

from light_control import light_control
from light_logger import log_light_status

from air_control import air_control
from air_logger import log_air_status

from tv_control import GestureDetection
from tv_logger import log_tv_status

from curtain_control import curtain_control
from curtain_logger import log_curtain_status

from door_control import door_control
from door_logger import log_door_status

class LivingRoom:
    def __init__(self, root, previous_screen=None):
        self.root = root
        self.previous_screen = previous_screen
        self.root.title("Living Room")
        self.root.geometry("850x725")
        self.root.resizable(False, False)

        # Light Control
        self.light_detector = light_control()
        self.is_light_camera_running = False
        self.light_status = self.get_latest_light_status()

        # Air Conditioner Control
        self.air_detector = air_control()
        self.is_air_camera_running = False
        self.air_status = self.get_latest_air_status()

        # TV Control
        self.tv_detector = GestureDetection()
        self.is_tv_camera_running = False
        self.tv_status = self.get_latest_tv_status()

        # Curtain Control
        self.curtain_detector = curtain_control()
        self.is_curtain_camera_running = False
        self.curtain_status = self.get_latest_curtain_status()

        # Door Control
        self.door_detector = door_control()
        self.is_door_camera_running = False
        self.door_status = self.get_latest_door_status()

        # Back Button
        self.back_button = Button(
            self.root, text="🔙",
            command=self.go_back,
            font=("Helvetica", 20)
        )
        self.back_button.place(x=750, y=615, width=50, height=50)

        # Controller Buttons
        button_x = 50
        button_width = 250
        button_height = 50
        spacing = 140
        y_offset = 15

        self.add_control_section("💡 Lamba Kontrol", self.toggle_light_camera,
                                 "Picture/lightonlogo.png", "Lamba Aç",
                                 "Picture/lightofflogo.png", "Lamba Kapat",
                                 button_x, y_offset, button_width, button_height, self.light_status, "Lamba")

        y_offset += spacing
        self.add_control_section("❄️ Klima Kontrol", self.toggle_air_camera,
                                 "Picture/aironlogo.png", "Klima Aç",
                                 "Picture/airofflogo.png", "Klima Kapat",
                                 button_x, y_offset, button_width, button_height, self.air_status, "Klima")

        y_offset += spacing
        self.add_control_section("📺 TV Kontrol", self.toggle_tv_camera,
                                 "Picture/tvonlogo.png", "TV Aç",
                                 "Picture/tvofflogo.png", "TV Kapat",
                                 button_x, y_offset, button_width, button_height, self.tv_status, "TV")

        y_offset += spacing
        self.add_control_section("🪟 Perde Kontrol", self.toggle_curtain_camera,
                                 "Picture/curtainopenlogo.png", "Perde Aç",
                                 "Picture/curtaincloselogo.png", "Perde Kapat",
                                 button_x, y_offset, button_width, button_height, self.curtain_status, "Perde")

        y_offset += spacing
        self.add_control_section("🚪 Kapı Kontrol", self.toggle_door_camera,
                                 "Picture/dooropenlogo.png", "Kapı Aç",
                                 "Picture/doorcloselogo.png", "Kapı Kapat",
                                 button_x, y_offset, button_width, button_height, self.door_status, "Kapı")

        # Camera Canvas
        self.camera_canvas = tk.Canvas(self.root, width=400, height=300)
        self.camera_canvas.place(x=380, y=150)

    def get_latest_light_status(self):
        try:
            connection = sqlite3.connect("LightLogger.db")
            cursor = connection.cursor()
            cursor.execute("""
                   SELECT status
                   FROM LightLog
                   WHERE room = 'Living Room'
                   ORDER BY timestamp DESC
                   LIMIT 1;
               """)
            result = cursor.fetchone()
            return result[0] if result else "Kapalı"
        except Exception as e:
            print(f"Son ışık durumunu çekerken hata oluştu: {e}")
            return "Kapalı"
        finally:
            connection.close()

    def get_latest_door_status(self):
        try:
            connection = sqlite3.connect("DoorLogger.db")
            cursor = connection.cursor()
            cursor.execute("""
                   SELECT status
                   FROM DoorLog
                   WHERE room = 'Living Room'
                   ORDER BY timestamp DESC
                   LIMIT 1;
               """)
            result = cursor.fetchone()
            return result[0] if result else "Kapalı"
        except Exception as e:
            print(f"Son kapı durumunu çekerken hata oluştu: {e}")
            return "Kapalı"
        finally:
            connection.close()

    def get_latest_curtain_status(self):
        try:
            connection = sqlite3.connect("CurtainLogger.db")
            cursor = connection.cursor()
            cursor.execute("""
                   SELECT status
                   FROM CurtainLog
                   WHERE room = 'Living Room'
                   ORDER BY timestamp DESC
                   LIMIT 1;
               """)
            result = cursor.fetchone()
            return result[0] if result else "Kapalı"
        except Exception as e:
            print(f"Son perde durumunu çekerken hata oluştu: {e}")
            return "Kapalı"
        finally:
            connection.close()

    def get_latest_air_status(self):
        try:
            connection = sqlite3.connect("AirLogger.db")
            cursor = connection.cursor()
            cursor.execute("""
                   SELECT status
                   FROM AirLog
                   WHERE room = 'Living Room'
                   ORDER BY timestamp DESC
                   LIMIT 1;
               """)
            result = cursor.fetchone()
            return result[0] if result else "Kapalı"
        except Exception as e:
            print(f"Son klima durumunu çekerken hata oluştu: {e}")
            return "Kapalı"
        finally:
            connection.close()

    def get_latest_tv_status(self):
        try:
            connection = sqlite3.connect("TVLogger.db")
            cursor = connection.cursor()
            cursor.execute("""
                   SELECT status
                   FROM TVLog
                   WHERE room = 'Living Room'
                   ORDER BY timestamp DESC
                   LIMIT 1;
               """)
            result = cursor.fetchone()
            return result[0] if result else "Kapalı"
        except Exception as e:
            print(f"Son TV durumunu çekerken hata oluştu: {e}")
            return "Kapalı"
        finally:
            connection.close()

    def add_control_section(self, button_text, toggle_command,
                            on_image_path, on_text,
                            off_image_path, off_text,
                            x, y, width, height, status, device_name):
        btn = Button(self.root, text=button_text, command=toggle_command)
        btn.place(x=x, y=y, width=width, height=height)

        status_label_name = f"{device_name.lower()}_label"
        status_label = Label(
            self.root,
            text=f"{device_name} Durumu: {status}",
            font=("Helvetica", 12)
        )
        status_label.place(x=x, y=y + height + 5)
        setattr(self, status_label_name, status_label)

        on_image = ImageTk.PhotoImage(Image.open(on_image_path).resize((40, 40)))
        off_image = ImageTk.PhotoImage(Image.open(off_image_path).resize((40, 40)))

        on_label = Label(self.root, image=on_image, text=on_text, compound="top", font=("Helvetica", 10))
        on_label.image = on_image
        on_label.place(x=x, y=y + height + 30)

        off_label = Label(self.root, image=off_image, text=off_text, compound="top", font=("Helvetica", 10))
        off_label.image = off_image
        off_label.place(x=x + 60, y=y + height + 30)

    def toggle_light_camera(self):
        self.stop_other_cameras('light')
        if not self.is_light_camera_running:
            self.is_light_camera_running = True
            threading.Thread(target=self.update_light_camera, daemon=True).start()
        else:
            self.is_light_camera_running = False
            self.light_detector.release()

    def toggle_air_camera(self):
        self.stop_other_cameras('air')
        if not self.is_air_camera_running:
            self.is_air_camera_running = True
            threading.Thread(target=self.update_air_camera, daemon=True).start()
        else:
            self.is_air_camera_running = False
            self.air_detector.release()

    def toggle_tv_camera(self):
        self.stop_other_cameras('tv')
        if not self.is_tv_camera_running:
            self.is_tv_camera_running = True
            threading.Thread(target=self.update_tv_camera, daemon=True).start()
        else:
            self.is_tv_camera_running = False
            self.tv_detector.release()

    def toggle_curtain_camera(self):
        self.stop_other_cameras('curtain')
        if not self.is_curtain_camera_running:
            self.is_curtain_camera_running = True
            threading.Thread(target=self.update_curtain_camera, daemon=True).start()
        else:
            self.is_curtain_camera_running = False
            self.curtain_detector.release()

    def toggle_door_camera(self):
        self.stop_other_cameras('door')
        if not self.is_door_camera_running:
            self.is_door_camera_running = True
            threading.Thread(target=self.update_door_camera, daemon=True).start()
        else:
            self.is_door_camera_running = False
            self.door_detector.release()

    def stop_other_cameras(self, except_camera):
        cameras = ['light', 'air', 'tv', 'curtain', 'door']
        for cam in cameras:
            if except_camera != cam and getattr(self, f'is_{cam}_camera_running'):
                setattr(self, f'is_{cam}_camera_running', False)
                getattr(self, f'{cam}_detector').release()

    def update_light_camera(self):
        while self.is_light_camera_running:
            on, off, frame = self.light_detector.detect_gestures()
            if on and self.light_status != "Açık":
                self.light_status = "Açık"
                log_light_status("Açık", "Living Room")
            elif off and self.light_status != "Kapalı":
                self.light_status = "Kapalı"
                log_light_status("Kapalı", "Living Room")
            self.lamba_label.config(text=f"Lamba Durumu: {self.light_status}")
            self.update_camera_frame(frame)

    def update_air_camera(self):
        while self.is_air_camera_running:
            on, off, frame = self.air_detector.detect_gestures()
            if on and self.air_status != "Açık":
                self.air_status = "Açık"
                log_air_status("Açık", "Living Room")
            elif off and self.air_status != "Kapalı":
                self.air_status = "Kapalı"
                log_air_status("Kapalı", "Living Room")
            self.klima_label.config(text=f"Klima Durumu: {self.air_status}")
            self.update_camera_frame(frame)

    def update_tv_camera(self):
        while self.is_tv_camera_running:
            on, off, frame = self.tv_detector.detect_gestures()
            if on and self.tv_status != "Açık":
                self.tv_status = "Açık"
                log_tv_status("Açık", "Living Room")
            elif off and self.tv_status != "Kapalı":
                self.tv_status = "Kapalı"
                log_tv_status("Kapalı", "Living Room")
            self.tv_label.config(text=f"TV Durumu: {self.tv_status}")
            self.update_camera_frame(frame)

    def update_curtain_camera(self):
        while self.is_curtain_camera_running:
            on, off, frame = self.curtain_detector.detect_gestures()
            if on and self.curtain_status != "Açık":
                self.curtain_status = "Açık"
                log_curtain_status("Açık", "Living Room")
            elif off and self.curtain_status != "Kapalı":
                self.curtain_status = "Kapalı"
                log_curtain_status("Kapalı", "Living Room")
            self.perde_label.config(text=f"Perde Durumu: {self.curtain_status}")
            self.update_camera_frame(frame)

    def update_door_camera(self):
        while self.is_door_camera_running:
            on, off, frame = self.door_detector.detect_gestures()
            if on and self.door_status != "Açık":
                self.door_status = "Açık"
                log_door_status("Açık", "Living Room")
            elif off and self.door_status != "Kapalı":
                self.door_status = "Kapalı"
                log_door_status("Kapalı", "Living Room")
            self.kapı_label.config(text=f"Kapı Durumu: {self.door_status}")
            self.update_camera_frame(frame)

    def update_camera_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (400, 300))
        photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
        self.camera_canvas.create_image(0, 0, image=photo, anchor=tk.NW)
        self.camera_canvas.photo = photo
        self.root.update()

    def go_back(self):
        self.stop_other_cameras(None)
        for widget in self.root.winfo_children():
            widget.destroy()
        if self.previous_screen:
            self.previous_screen(self.root)