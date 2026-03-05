from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import cv2
import mediapipe as mp
import joblib
import numpy as np
import base64
import os

app = Flask(__name__)
CORS(app)

# -------- Load trained model --------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")

model = joblib.load(MODEL_PATH)

# -------- MediaPipe setup --------
import mediapipe as mp
from mediapipe.tasks.python import vision
from mediapipe.tasks.python import core
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

CONFIDENCE_THRESHOLD = 0.55   # slightly lower for better stability

<<<<<<< HEAD

# -------- Prediction API --------
@app.route("/")
def home():
    return render_template("index.html")

=======
# -------- Prediction API --------3
@app.route("/")
def home():
    return "AI Mudra Recognition API is running"
>>>>>>> 3f9e5ce824ea9561f350482e50d8f9cbd2a86e5f
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json["image"]

        # Decode base64 image
        img_bytes = base64.b64decode(data.split(",")[1])
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame is None:
            return jsonify({"label": "No Hand"})

        # Convert for MediaPipe
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        if not result.multi_hand_landmarks:
            return jsonify({"label": "No Hand"})

        for hand in result.multi_hand_landmarks:
            row = []

            # Normalize landmarks relative to wrist (point 0)
            base_x = hand.landmark[0].x
            base_y = hand.landmark[0].y

            for lm in hand.landmark:
                row.extend([lm.x - base_x, lm.y - base_y])

            # Safety check
            if len(row) != 42:
                return jsonify({"label": "No Hand"})

            # Predict probabilities
            probs = model.predict_proba([row])[0]
            best = np.argmax(probs)

            if probs[best] >= CONFIDENCE_THRESHOLD:
                return jsonify({
                    "label": model.classes_[best],
                    "confidence": float(probs[best])
                })

        return jsonify({"label": "Unknown"})

    except Exception as e:
        print("Error:", e)
        return jsonify({"label": "Error"})

# -------- Run server --------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
