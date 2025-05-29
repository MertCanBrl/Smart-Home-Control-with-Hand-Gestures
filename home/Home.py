import tkinter as tk
from tkinter import Label, Button
from Home.BedRoom import BedRoom
from Home.Kitchen import Kitchen
from Home.LivingRoom import LivingRoom


class Home:
    def __init__(self, root, previous_screen=None):
        self.root = root
        self.previous_screen = previous_screen
        self.root.title("Home Screen")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        # Back button
        self.back_button = Button(self.root, text="🔙", command=self.go_back, font=("Helvetica", 20))
        self.back_button.place(x=10, y=545, width=50, height=50)  # Piksel cinsinden konum ve boyut

        # Bed Room button
        self.bedroom_button = Button(self.root, text="🛏️Bed Room", command=self.open_bedroom)
        self.bedroom_button.place(x=115, y=175, width=250, height=50)  # Piksel cinsinden konum ve boyut

        # Kitchen button
        self.kitchen_button = Button(self.root, text="Kitchen", command=self.open_kitchen)
        self.kitchen_button.place(x=435, y=175, width=250, height=50)  # Piksel cinsinden konum ve boyut

        # Living Room button
        self.livingroom_button = Button(self.root, text="Living Room", command=self.open_livingroom)
        self.livingroom_button.place(x=255, y=335, width=250, height=50)  # Piksel cinsinden konum ve boyut


    def go_back(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        if self.previous_screen:
            self.previous_screen(self.root)


    def open_bedroom(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        BedRoom(self.root, self.previous_screen)

    def open_kitchen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        Kitchen(self.root, self.previous_screen)

    def open_livingroom(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        LivingRoom(self.root, self.previous_screen)