# Office.py
from tkinter import Label, Button

class OfficeScreen:
    def __init__(self, root, login_screen_class):
        self.root = root
        self.login_screen_class = login_screen_class
        self.root.title("Office Screen")
        self.root.geometry("800x600")
        self.root.resizable(False, False)  # Pencere boyutunu sabit tut


        # Geri butonu
        self.back_button = Button(self.root, text="🔙", command=self.go_back, font=("Helvetica", 20))
        self.back_button.place(x=10, y=545, width=50, height=50)  # Piksel cinsinden konum ve boyut

    def go_back(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.login_screen_class(self.root)