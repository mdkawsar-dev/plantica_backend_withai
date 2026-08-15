"""
Plant Disease Predictor - EfficientNetV2 & Plant Masking Supported
গাছের নাম ও পাতার ইমেজ ইনপুট নিয়ে মডেল প্রেডিকশন এবং ফিল্টারিং সম্পন্ন করে।
"""
import json
import os
import numpy as np
from PIL import Image


class PlantDiseasePredictor:
    _instance = None
    model = None
    classes = []
    plant_class_map = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PlantDiseasePredictor, cls).__new__(cls)
            cls._load_resources()
        return cls._instance

    @classmethod
    def _load_resources(cls):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(base_dir, 'ml_models', 'best_model.keras')
        classes_path = os.path.join(base_dir, 'ml_models', 'classes.json')

        # ১. Keras Model Load (compile=False দিলে কাস্টম মেট্রিক সংক্রান্ত কোনো এরর দেবে না)
        if os.path.exists(model_path):
            try:
                import keras
                cls.model = keras.saving.load_model(model_path, compile=False, safe_mode=False)
                print("Successfully loaded EfficientNetV2 Plantica Model.")
            except Exception as e1:
                try:
                    import tensorflow as tf
                    cls.model = tf.keras.models.load_model(model_path, compile=False)
                    print("Successfully loaded EfficientNetV2 Plantica Model via tf.keras.")
                except Exception as e2:
                    print(f"Error loading model: {e1} | {e2}")
                    cls.model = None
        else:
            print(f"Model not found at: {model_path}")
            cls.model = None

        # ২. classes.json থেকে CLASSES এবং PLANT_CLASS_MAP লোড
        if os.path.exists(classes_path):
            try:
                with open(classes_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    cls.classes = data.get("classes", [])
                    cls.plant_class_map = data.get("plant_class_map", {})
                print(f"Loaded {len(cls.classes)} classes and {len(cls.plant_class_map)} plant map entries.")
            except Exception as e:
                print(f"Error loading classes.json: {e}")

    def predict_image(self, image_file, plant_name=None, target_size=(224, 224)):
        """
        ইনপুট ইমেজ এবং অপশনাল plant_name নিয়ে রোগ সনাক্ত করে।
        Returns: (raw_label: str, confidence: float)
        """
        if not self.model:
            raise Exception("Model is not loaded properly.")

        # ১. ছবি লোড ও রিসাইজ
        img = Image.open(image_file).convert('RGB')
        img = img.resize(target_size, Image.LANCZOS)

        # ২. 0-255 float32-তে কনভার্ট (এখানে / 255.0 করা যাবে না, preprocess_input হ্যান্ডেল করবে)
        img_array = np.array(img, dtype=np.float32)

        # ৩. EfficientNetV2 Preprocessing (Standard: [-1, 1] range)
        try:
            from tensorflow.keras.applications.efficientnet_v2 import preprocess_input
            img_array = preprocess_input(img_array)
        except Exception:
            try:
                from keras.applications.efficientnet_v2 import preprocess_input
                img_array = preprocess_input(img_array)
            except Exception:
                img_array = (img_array - 128.0) / 128.0

        img_array = np.expand_dims(img_array, axis=0)

        # ৪. মডেল প্রেডিকশন (Raw Logits / Probabilities)
        predictions = self.model.predict(img_array, verbose=0)[0].copy()

        # ৫. Plant Masking Logic (যদি ইউজার গাছের নাম যেমন 'টমেটো', 'লেবু' বা 'tomato' পাঠায়)
        if plant_name and self.plant_class_map:
            matched_key = None
            clean_input = plant_name.lower().strip()

            # বাংলা বা ইংরেজি নাম অনুযায়ী plant_class_map-এর সাথে মেলানো
            for key in self.plant_class_map.keys():
                k_clean = key.lower().strip()
                if k_clean == clean_input or k_clean in clean_input or clean_input in k_clean:
                    matched_key = key
                    break

            # যদি গাছের নাম মিলে যায়, তবে শুধু ওই গাছের সম্পর্কিত রোগের ক্লাসগুলো ফিল্টার করা
            if matched_key and matched_key in self.plant_class_map:
                allowed_indices = self.plant_class_map[matched_key]
                if allowed_indices:
                    masked_preds = np.full_like(predictions, -1e9)
                    masked_preds[allowed_indices] = predictions[allowed_indices]
                    predictions = masked_preds

        # ৬. Argmax & Softmax Probability
        predicted_idx = int(np.argmax(predictions))

        # Softmax Probability বের করা
        exp_preds = np.exp(predictions - np.max(predictions))
        probabilities = exp_preds / np.sum(exp_preds)
        confidence = float(probabilities[predicted_idx]) * 100

        # ৭. ক্লাসের নাম বের করা
        raw_label = self.classes[predicted_idx] if predicted_idx < len(self.classes) else f"Class_{predicted_idx}"

        return raw_label, round(confidence, 1)

    def is_ready(self):
        return self.model is not None and len(self.classes) > 0
