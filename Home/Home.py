import os
import tkinter as tk
from tkinter import Label, Button
from PIL import Image, ImageTk
from Home.BedRoom import BedRoom
from Home.Kitchen import Kitchen
from Home.LivingRoom import LivingRoom
from Home.ChildRoom import ChildRoom

class Home:
    def __init__(self, root, previous_screen=None):
        self.root = root
        self.previous_screen = previous_screen
        self.root.title("Home Screen")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f4f8")

        current_dir = os.path.dirname(os.path.abspath(__file__))
        picture_dir = os.path.join(current_dir, "..", "Picture")

        # BACK button
        self.back_button = Button(self.root, text="🔙", command=self.go_back, font=("Helvetica", 20))
        self.back_button.place(x=10, y=545, width=50, height=50)

        # Room Definitions
        self.rooms = [
            {"name": "Bedroom", "photo": "bedroomlogo.png", "command": self.open_bedroom},
            {"name": "ChildRoom", "photo": "childroomlogo.png", "command": self.open_childroom},  # Örnek ChildRoom resmi
            {"name": "Living Room", "photo": "livingroomnewlogo.png", "command": self.open_livingroom},
            {"name": "Kitchen", "photo": "kitchenlogo.png", "command": self.open_kitchen}
        ]

        # Grid ayarları
        columns = 2
        rows = 2
        button_width = 300
        button_height = 150
        h_spacing = 80
        v_spacing = 50
        x_start = 70
        y_start = 60

        for index, room in enumerate(self.rooms):
            row = index // columns
            col = index % columns
            x_pos = x_start + col * (button_width + h_spacing)
            y_pos = y_start + row * (button_height + v_spacing + 40)

            # Load image
            image_path = os.path.join(picture_dir, room["photo"])
            try:
                img = Image.open(image_path)
                img = img.resize((button_width, button_height), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"⚠️ Error loading image for {room['name']}: {e}")
                photo = None

            # Room button (image fills entire button)
            room_button = Button(
                self.root,
                image=photo,
                command=room["command"],
                relief="raised",
                bd=3,
                cursor="hand2"
            )
            room_button.image = photo  # Referans kaybetmemek için
            room_button.place(x=x_pos, y=y_pos, width=button_width, height=button_height)

            # Room label (below the button)
            room_label = Label(
                self.root,
                text=room["name"],
                font=("Helvetica", 16, "bold"),
                bg="#f0f4f8",
                fg="#333333"
            )
            room_label.place(x=x_pos, y=y_pos + button_height + 5, width=button_width, height=30)

    def go_back(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        if self.previous_screen:
            self.previous_screen(self.root)

    def open_bedroom(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        BedRoom(self.root, self.previous_screen)

    def open_childroom(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        ChildRoom(self.root, self.previous_screen)

    def open_livingroom(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        LivingRoom(self.root, self.previous_screen)

    def open_kitchen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        Kitchen(self.root, self.previous_screen)