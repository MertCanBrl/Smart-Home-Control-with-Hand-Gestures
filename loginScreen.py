import os
import tkinter as tk
from tkinter import Label, Button
from PIL import Image, ImageDraw, ImageFont, ImageTk
from Home.Home import Home

class LoginScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Home Control with Hand Gestures")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f4f8")


        current_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(current_dir, "textFont", "neuropolitical rg.ttf")


        try:
            custom_font = ImageFont.truetype(font_path, size=28)
        except Exception as e:
            print("Font yüklenirken hata oluştu:", e)
            custom_font = ImageFont.load_default()

        text = "Welcome to Smart Home Control\nwith Hand Gestures"
        img_width, img_height = 700, 120
        img = Image.new("RGBA", (img_width, img_height), (240, 244, 248, 255))  # bg #f0f4f8
        draw = ImageDraw.Draw(img)

        bbox = draw.multiline_textbbox((0, 0), text, font=custom_font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]

        draw.multiline_text(
            ((img_width - w) / 2, (img_height - h) / 2),
            text,
            font=custom_font,
            fill="#333333",
            align="center"
        )

        self.text_image = ImageTk.PhotoImage(img)

        self.welcome_label = Label(self.root, image=self.text_image, bg="#f0f4f8")
        self.welcome_label.place(relx=0.5, rely=0.05, anchor="n")


        image_path = os.path.join(current_dir, "Picture", "loginScreen.png")
        original_logo = tk.PhotoImage(file=image_path)
        self.logo_image = original_logo.subsample(2, 2)
        self.logo_label = Label(self.root, image=self.logo_image, bg="#f0f4f8")
        self.logo_label.place(relx=0.5, rely=0.48, anchor="center")


        self.page1_button = Button(
            self.root,
            text="🏠 Home",
            command=self.go_to_page1,
            font=("Segoe UI", 16, "bold"),
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            activeforeground="white",
            relief="raised",
            bd=3,
            cursor="hand2"
        )
        self.page1_button.place(relx=0.5, rely=0.8, anchor="center", width=180, height=60)

        self.page1_button.bind("<Enter>", lambda e: self.page1_button.config(bg="#45a049"))
        self.page1_button.bind("<Leave>", lambda e: self.page1_button.config(bg="#4CAF50"))

    def go_to_page1(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        Home(self.root, LoginScreen)
