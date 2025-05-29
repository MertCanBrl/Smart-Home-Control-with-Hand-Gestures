import tkinter as tk
from tkinter import Label, Button
from Home.Home import Home
from Office.Office import OfficeScreen

class LoginScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Home Control with Hand Gestures")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        # Hoş geldiniz mesajı
        self.welcome_label = Label(self.root, text="Smart Home Control with Hand Gestures", font=("Helvetica", 20), fg="black")
        self.welcome_label.pack(pady=80)

        # Butonlar
        self.page1_button = Button(self.root, text="Home", command=self.go_to_page1, font=("Helvetica", 16))
        self.page1_button.place(x=166, y=225, width=150, height=250)

        self.page2_button = Button(self.root, text="Office", command=self.go_to_page2, font=("Helvetica", 16))
        self.page2_button.place(x=483, y=225, width=150, height=250)

    def go_to_page1(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        Home(self.root, LoginScreen)

    def go_to_page2(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        OfficeScreen(self.root, LoginScreen)