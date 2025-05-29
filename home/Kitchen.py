import tkinter as tk
from tkinter import Label, Button
from Home.BedRoom import BedRoom

class Kitchen:
    def __init__(self, root, previous_screen=None):
        self.root = root
        self.previous_screen = previous_screen
        self.root.title("Home Screen")
        self.root.geometry("800x600")
        self.root.resizable(False, False)