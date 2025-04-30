import cv2
import numpy as np
import mediapipe as mp
import os
import zipfile
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split


class GestureDetection:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6,
            max_num_hands=1
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.cap = cv2.VideoCapture(0)

        self.dataset_images, self.dataset_labels = self.extract_and_load_dataset("archive.zip")
        self.knn_model = self.train_knn_model(self.dataset_images, self.dataset_labels)

    def extract_and_load_dataset(self, zip_path, extract_dir="dataset"):
        dataset_root = os.path.join(extract_dir, "leapGestRecog")

        # Zipten çıkar (klasör yoksa)
        if not os.path.exists(dataset_root):
            if not os.path.exists(extract_dir):
                os.makedirs(extract_dir)
            print(f"Zip dosyası çıkartılıyor: {zip_path}")
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
            except Exception as e:
                raise Exception(f"Zip dosyası açılırken hata oluştu: {str(e)}")

        if not os.path.exists(dataset_root):
            raise Exception(f"{dataset_root} bulunamadı! Çıkartma işlemi başarısız veya klasör adı yanlış.")

        data = []
        labels = []

        # KİŞİ KLASÖRLERİNİ Tara (00, 01, ..., 09)
        for person_dir in os.listdir(dataset_root):
            person_path = os.path.join(dataset_root, person_dir)
            if not os.path.isdir(person_path):
                continue

            # gesture klasörlerini tara (01_palm, ..., 07_ok, 10_down, ...)
            for gesture_dir in os.listdir(person_path):
                gesture_path = os.path.join(person_path, gesture_dir)
                if not os.path.isdir(gesture_path):
                    continue

                if gesture_dir.lower() == "07_ok":
                    label = "ok"
                elif gesture_dir.lower() == "10_down":
                    label = "down"
                else:
                    continue

                for img_file in os.listdir(gesture_path):
                    if img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        img_path = os.path.join(gesture_path, img_file)
                        try:
                            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                            if img is not None:
                                img = cv2.resize(img, (64, 64))
                                data.append(img)
                                labels.append(label)
                        except Exception as e:
                            print(f"Resim yüklenirken hata: {img_path} - {str(e)}")

        print(f"Toplam yüklenen görsel: {len(data)}")
        if len(data) == 0:
            raise Exception("Hiç uygun resim bulunamadı! Lütfen veri setini kontrol edin.")

        return np.array(data), np.array(labels)

    def train_knn_model(self, dataset_images, dataset_labels):
        X = dataset_images.reshape(len(dataset_images), -1)
        y = dataset_labels
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

        model = KNeighborsClassifier(n_neighbors=3)
        model.fit(X_train, y_train)

        accuracy = model.score(X_test, y_test)
        print(f"Model doğruluk oranı: {accuracy * 100:.2f}%")

        return model

    def detect_gestures(self):
        success, img = self.cap.read()
        if not success:
            return None, None, img

        img = cv2.flip(img, 1)  # <-- AYNA ETKİSİ BURADA!

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)

        is_ok = False
        is_dislike = False

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                h, w, c = img.shape
                x_min, y_min = w, h
                x_max, y_max = 0, 0

                for lm in hand_landmarks.landmark:
                    x, y = int(lm.x * w), int(lm.y * h)
                    x_min, y_min = min(x_min, x), min(y_min, y)
                    x_max, y_max = max(x_max, x), max(y_max, y)

                padding = 20
                x_min = max(0, x_min - padding)
                y_min = max(0, y_min - padding)
                x_max = min(w, x_max + padding)
                y_max = min(h, y_max + padding)

                if x_max > x_min and y_max > y_min:
                    hand_img = img_rgb[y_min:y_max, x_min:x_max]
                    gesture = self.predict_gesture(hand_img)
                    if gesture == "ok":
                        is_ok = True
                        cv2.putText(img, "TV Aciliyor!", (10, 30), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
                        cv2.rectangle(img, (0, 0), (w, h), (0, 255, 0), 2)
                    elif gesture == "down":
                        is_dislike = True
                        cv2.putText(img, "TV Kapaniyor!", (10, 30), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)
                        cv2.rectangle(img, (0, 0), (w, h), (0, 0, 255), 2)

                    cv2.putText(img, f"Tahmin: {gesture}", (10, h - 20), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)

        return is_ok, is_dislike, img

    def predict_gesture(self, hand_image):
        hand_image = cv2.cvtColor(hand_image, cv2.COLOR_RGB2GRAY)
        hand_image = cv2.resize(hand_image, (64, 64))
        X_query = hand_image.flatten().reshape(1, -1)
        prediction = self.knn_model.predict(X_query)[0]
        return prediction

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()