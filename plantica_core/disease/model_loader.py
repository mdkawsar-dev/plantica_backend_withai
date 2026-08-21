"""
Plant Disease Predictor - EfficientNetV2 & Plant Masking Supported
গাছের নাম ও পাতার ইমেজ ইনপুট নিয়ে মডেল প্রেডিকশন এবং ফিল্টারিং সম্পন্ন করে।
"""
import io
import json
import os
import zipfile
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

        # ১. Keras Model Load
        if os.path.exists(model_path):
            try:
                import keras
                cls.model = keras.saving.load_model(model_path, compile=False, safe_mode=False)
                print("Successfully loaded EfficientNetV2 Plantica Model.")
            except Exception as e1:
                try:
                    # Keras cross-version config compatibility fallback
                    with open(model_path, 'rb') as f:
                        zin = zipfile.ZipFile(f)
                        config = json.loads(zin.read('config.json').decode('utf-8'))

                    def _sanitize(d):
                        if isinstance(d, dict):
                            d.pop('quantization_config', None)
                            for v in d.values():
                                _sanitize(v)
                        elif isinstance(d, list):
                            for item in d:
                                _sanitize(item)

                    _sanitize(config)
                    out_buf = io.BytesIO()
                    with zipfile.ZipFile(model_path, 'r') as zin:
                        with zipfile.ZipFile(out_buf, 'w') as zout:
                            for item in zin.infolist():
                                buf = zin.read(item.filename)
                                if item.filename == 'config.json':
                                    buf = json.dumps(config).encode('utf-8')
                                zout.writestr(item, buf)
                    out_buf.seek(0)
                    import keras
                    cls.model = keras.saving.load_model(out_buf, compile=False, safe_mode=False)
                    print("Successfully loaded EfficientNetV2 Plantica Model (with sanitized config).")
                except Exception as e2:
                    try:
                        import tensorflow as tf
                        cls.model = tf.keras.models.load_model(model_path, compile=False)
                        print("Successfully loaded EfficientNetV2 Plantica Model via tf.keras.")
                    except Exception as e3:
                        print(f"Error loading model: {e1} | {e2} | {e3}")
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

        # ২. EfficientNetV2 Input: float32 in [0, 255] range (internal Rescaling layer handles normalization)
        img_array = np.array(img, dtype=np.float32)
        img_array = np.expand_dims(img_array, axis=0)

        # ৩. মডেল প্রেডিকশন (Probabilities)
        raw_predictions = self.model.predict(img_array, verbose=0)[0].copy()

        top_idx = int(np.argmax(raw_predictions))
        non_plant_sum = float(np.sum(raw_predictions[:257]))
        plant_sum = float(np.sum(raw_predictions[257:]))

        # ৪. Non-Plant Object / Background Detection (Caltech-256 classes 0..256)
        # যদি মডেল কোনো গাড়ি, মানুষ, জীবজন্তু বা অপ্রাসঙ্গিক অবজেক্ট সনাক্ত করে:
        if top_idx < 257 or (non_plant_sum > 0.65 and plant_sum < 0.35):
            non_plant_conf = max(float(raw_predictions[top_idx]) * 100, float(non_plant_sum) * 100, 80.0)
            non_plant_conf = min(99.0, non_plant_conf)
            return "Non_Plant_Object", round(non_plant_conf, 1)

        # ৫. Plant Masking Logic (যদি ইউজার গাছের নাম যেমন 'টমেটো', 'লেবু', 'বেগুন' বা 'tomato' পাঠায়)
        matched_indices = None
        if plant_name and str(plant_name).strip() not in ['', 'গাছের নাম জানা নেই', 'গাছ', 'unknown', 'None']:
            clean_input = str(plant_name).lower().strip()
            for key, indices in self.plant_class_map.items():
                k_clean = str(key).lower().strip()
                if k_clean == clean_input or k_clean in clean_input or clean_input in k_clean:
                    # Filter to only plant class indices (>= 257)
                    valid_plant_indices = [idx for idx in indices if idx >= 257]
                    if valid_plant_indices:
                        matched_indices = valid_plant_indices
                        break

        if matched_indices and len(matched_indices) > 0:
            sub_probs = raw_predictions[matched_indices]
            sub_sum = np.sum(sub_probs)
            if sub_sum > 0:
                sub_norm = sub_probs / sub_sum
                best_sub_idx = int(np.argmax(sub_norm))
                predicted_idx = matched_indices[best_sub_idx]
                confidence = float(sub_norm[best_sub_idx]) * 100
            else:
                predicted_idx = matched_indices[0]
                confidence = 50.0
        else:
            # গাছের নাম না দিলে plant classes (257..386)-এর মধ্যে সেরা রোগটি বেছে নেওয়া
            plant_probs = raw_predictions[257:]
            best_plant_offset = int(np.argmax(plant_probs))
            predicted_idx = 257 + best_plant_offset
            if plant_sum > 0:
                confidence = float(raw_predictions[predicted_idx] / plant_sum) * 100
            else:
                confidence = float(raw_predictions[predicted_idx]) * 100

        # ৬. ক্লাসের নাম বের করা
        raw_label = self.classes[predicted_idx] if predicted_idx < len(self.classes) else f"Class_{predicted_idx}"
        confidence = max(10.0, min(99.5, confidence))

        return raw_label, round(confidence, 1)

    def is_ready(self):
        return self.model is not None and len(self.classes) > 0

