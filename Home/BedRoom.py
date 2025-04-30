import cv2
import mediapipe as mp
import tkinter as tk
from tkinter import Label, Button
from PIL import Image, ImageTk
import zipfile
import os
import numpy as np

from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split

# 📁 Dataset'i zip'ten çıkar ve belleğe yükle
def extract_and_load_dataset(zip_path="test.zip", extract_dir="dataset"):
    # Zip dosyasını varsa tekrar çıkarma
    if not os.path.exists(extract_dir) or not os.listdir(extract_dir):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
    # Klasör adımı (test klasörü varsa onun altından başla)
    root_folders = os.listdir(extract_dir)
    if len(root_folders) == 1 and os.path.isdir(os.path.join(extract_dir, root_folders[0])):
        real_root = os.path.join(extract_dir, root_folders[0])
    else:
        real_root = extract_dir

    data = []
    labels = []
    print(f"extract_dir: {real_root}, klasörler: {os.listdir(real_root)}")
    for label_folder in os.listdir(real_root):
        folder_path = os.path.join(real_root, label_folder)
        if not os.path.isdir(folder_path):
            continue
        print(f"{label_folder} klasörü, içindekiler: {os.listdir(folder_path)}")
        for img_name in os.listdir(folder_path):
            img_path = os.path.join(folder_path, img_name)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                print(f"HATALI/OKUNAMADI: {img_path}")
            else:
                img = cv2.resize(img, (64, 64))
                data.append(img)
                labels.append(int(label_folder))
    print(f"Toplam yüklenen görsel: {len(data)}")
    if len(data) == 0:
        raise Exception("Hiç veri yüklenemedi! Lütfen dataset yolunu ve içeriğini kontrol edin.")
    return np.array(data), np.array(labels)
# 🔬 KNN Modelini Eğit
def train_knn_model(dataset_images, dataset_labels):
    X = dataset_images.reshape(len(dataset_images), -1)  #  (adet, 4096)
    y = dataset_labels
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    model = KNeighborsClassifier(n_neighbors=3)
    model.fit(X_train, y_train)
    print("Model accuracy:", model.score(X_test, y_test))
    return model

# 🪧 Tek kareyi modele göre tahmin et
def predict_hand_sign_knn(current_hand_image, knn_model):
    current_hand_image = cv2.cvtColor(current_hand_image, cv2.COLOR_RGB2GRAY)
    current_hand_image = cv2.resize(current_hand_image, (64, 64))
    X_query = current_hand_image.flatten().reshape(1, -1)
    prediction = knn_model.predict(X_query)[0]
    return prediction

# 🖼 Ana GUI sınıfı
class BedRoom:
    def __init__(self, root, previous_screen=None):
        self.root = root
        self.previous_screen = previous_screen
        self.root.title("Bed Room")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        # Dataset'i yükle
        self.dataset_images, self.dataset_labels = extract_and_load_dataset()

        # KNN modeli eğit
        self.knn_model = train_knn_model(self.dataset_images, self.dataset_labels)

        # MediaPipe Hand Tracking
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands()
        self.mp_draw = mp.solutions.drawing_utils

        self.is_camera_on = False
        self.cap = None

        self.video_label = Label(self.root)
        self.video_label.place(relx=0.0625, rely=0.05, relwidth=0.875, relheight=0.67)

        self.start_button = Button(self.root, text="Open", command=self.start_camera)
        self.start_button.place(relx=0.1, rely=0.75)

        self.stop_button = Button(self.root, text="Stop", command=self.stop_camera)
        self.stop_button.place(relx=0.830, rely=0.75)

        self.back_button = Button(self.root, text="🔙", command=self.go_back, font=("Helvetica", 20))
        self.back_button.place(x=10, y=545, width=50, height=50)

    def start_camera(self):
        if not self.is_camera_on:
            self.cap = cv2.VideoCapture(0)
            self.is_camera_on = True
            self.update_frame()

    def stop_camera(self):
        if self.is_camera_on:
            self.is_camera_on = False
            self.cap.release()
            self.video_label.config(image="")

    def update_frame(self):
        if self.is_camera_on:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                result = self.hands.process(frame_rgb)
                if result.multi_hand_landmarks:
                    for hand_landmarks in result.multi_hand_landmarks:
                        h, w, c = frame.shape
                        x_min, y_min = w, h
                        x_max, y_max = 0, 0
                        for lm in hand_landmarks.landmark:
                            x, y = int(lm.x * w), int(lm.y * h)
                            x_min, y_min = min(x_min, x), min(y_min, y)
                            x_max, y_max = max(x_max, x), max(y_max, y)

                        # El bölgesini biraz geniş al
                        x_min, y_min = max(0, x_min - 20), max(0, y_min - 20)
                        x_max, y_max = min(w, x_max + 20), min(h, y_max + 20)
                        hand_img = frame_rgb[y_min:y_max, x_min:x_max]

                        if hand_img.size != 0:
                            predicted_label = predict_hand_sign_knn(hand_img, self.knn_model)
                            cv2.putText(frame, f"Prediction: {predicted_label}", (30, 400),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

                        # Landmarks çiz
                        self.mp_draw.draw_landmarks(
                            frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                            self.mp_draw.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=3),
                            self.mp_draw.DrawingSpec(color=(255, 255, 255), thickness=2)
                        )

                img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)

            self.root.after(10, self.update_frame)

    def go_back(self):
        self.stop_camera()
        for widget in self.root.winfo_children():
            widget.destroy()
        if self.previous_screen:
            self.previous_screen(self.root)

