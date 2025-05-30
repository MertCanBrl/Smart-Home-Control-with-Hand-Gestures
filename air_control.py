import cv2
import numpy as np
import mediapipe as mp
import os
import zipfile
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.optimizers import Adam
from collections import deque, Counter


class air_control:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6,
            max_num_hands=1
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.cap = cv2.VideoCapture(0)

        self.label_map = {"c": 0, "index": 1}
        self.label_map_rev = {v: k for k, v in self.label_map.items()}

        self.dataset_images, self.dataset_labels = self.extract_and_load_dataset("archive.zip")
        self.cnn_model = self.train_cnn_model(self.dataset_images, self.dataset_labels)
        self.recent_predictions = deque(maxlen=5)

    def extract_and_load_dataset(self, zip_path, extract_dir="dataset"):
        dataset_root = os.path.join(extract_dir, "leapGestRecog")

        if not os.path.exists(dataset_root):
            if not os.path.exists(extract_dir):
                os.makedirs(extract_dir)
            print(f"Zip dosyası çıkartılıyor: {zip_path}")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)

        data = []
        labels = []

        for person_dir in os.listdir(dataset_root):
            person_path = os.path.join(dataset_root, person_dir)
            if not os.path.isdir(person_path):
                continue

            for gesture_dir in os.listdir(person_path):
                gesture_path = os.path.join(person_path, gesture_dir)
                if not os.path.isdir(gesture_path):
                    continue

                if gesture_dir.lower() == "09_c":
                    label = "c"
                elif gesture_dir.lower() == "06_index":
                    label = "index"
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
                                labels.append(self.label_map[label])
                        except Exception as e:
                            print(f"Hata: {img_path} - {str(e)}")

        print(f"Toplam görsel yüklendi: {len(data)}")
        return np.array(data), np.array(labels)

    def train_cnn_model(self, dataset_images, dataset_labels):
        X = dataset_images.astype("float32") / 255.0
        X = X.reshape(-1, 64, 64, 1)
        y = to_categorical(dataset_labels, num_classes=2)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

        model = Sequential([
            Conv2D(32, (3, 3), activation='relu', input_shape=(64, 64, 1)),
            MaxPooling2D((2, 2)),
            Conv2D(64, (3, 3), activation='relu'),
            MaxPooling2D((2, 2)),
            Flatten(),
            Dense(64, activation='relu'),
            Dense(2, activation='softmax')
        ])

        model.compile(optimizer=Adam(), loss='categorical_crossentropy', metrics=['accuracy'])
        model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_test, y_test))

        loss, accuracy = model.evaluate(X_test, y_test)
        print(f"CNN doğruluk oranı: {accuracy * 100:.2f}%")

        return model

    def detect_gestures(self):
        success, img = self.cap.read()
        if not success:
            return None, None, img

        img = cv2.flip(img, 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)

        h, w, _ = img.shape
        gesture = None

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                x_min, y_min = w, h
                x_max, y_max = 0, 0
                for lm in hand_landmarks.landmark:
                    x, y = int(lm.x * w), int(lm.y * h)
                    x_min = min(x_min, x)
                    y_min = min(y_min, y)
                    x_max = max(x_max, x)
                    y_max = max(y_max, y)

                padding = 20
                x_min = max(0, x_min - padding)
                y_min = max(0, y_min - padding)
                x_max = min(w, x_max + padding)
                y_max = min(h, y_max + padding)

                if x_max > x_min and y_max > y_min:
                    hand_img = img_rgb[y_min:y_max, x_min:x_max]
                    gesture = self.predict_gesture(hand_img)
                    self.recent_predictions.append(gesture)

        if len(self.recent_predictions) == 5:
            most_common = Counter(self.recent_predictions).most_common(1)[0][0]
        else:
            most_common = None

        air_on = most_common == "index"
        air_off = most_common == "c"

        if air_on:
            cv2.putText(img, "air conditioner Acildi!", (10, 30), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
            cv2.rectangle(img, (0, 0), (w, h), (0, 255, 0), 2)
        elif air_off:
            cv2.putText(img, "air conditioner Kapandi!", (10, 30), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)
            cv2.rectangle(img, (0, 0), (w, h), (0, 0, 255), 2)

        return air_on, air_off, img

    def predict_gesture(self, hand_image):
        try:
            gray_img = cv2.cvtColor(hand_image, cv2.COLOR_RGB2GRAY)
            gray_img = cv2.resize(gray_img, (64, 64))
            gray_img = gray_img.astype("float32") / 255.0
            gray_img = gray_img.reshape(1, 64, 64, 1)
            prediction = self.cnn_model.predict(gray_img, verbose=0)
            class_index = np.argmax(prediction)
            return self.label_map_rev[class_index]
        except Exception as e:
            print(f"Tahmin hatası: {str(e)}")
            return "unknown"

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()

