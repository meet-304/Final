#!/usr/bin/env python3
"""
Fresh Start - Detect Logo
Simple and clean - only essential code
"""

import os
import cv2
import numpy as np
import json
import serial
import time
import tensorflow as tf

# CONFIG
INPUT_IMAGE = 'captured_images/image.jpg'
MODEL = 'logo_model.tflite'
CLASSES = 'classes.json'
IMAGE_SIZE = 224
ARDUINO_PORT = "/dev/ttyACM0"
BAUD_RATE = 9600

SERVO_ANGLES = {
    0: 45,
    1: 0,
    2: 135
}

# LOGO DETECTOR
class LogoDetector:
    @staticmethod
    def detect_and_crop(path):
        img = cv2.imread(path)
        if img is None:
            return None
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)
        
        _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=3)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None
        
        c = max(contours, key=cv2.contourArea)
        if cv2.contourArea(c) < 1000:
            return None
        
        x, y, w, h = cv2.boundingRect(c)
        p = 20
        x1, y1 = max(0, x - p), max(0, y - p)
        x2, y2 = min(img.shape[1], x + w + p), min(img.shape[0], y + h + p)
        
        logo = img[y1:y2, x1:x2]
        return cv2.resize(logo, (IMAGE_SIZE, IMAGE_SIZE))

# TFLITE CLASSIFIER
class Classifier:
    def __init__(self):
        self.interp = tf.lite.Interpreter(model_path=MODEL)
        self.interp.allocate_tensors()
        
        self.in_detail = self.interp.get_input_details()
        self.out_detail = self.interp.get_output_details()
        
        with open(CLASSES) as f:
            self.names = json.load(f)['classes']
        
        print(f"✓ Model: {self.names}")
    
    def classify(self, logo):
        logo_rgb = cv2.cvtColor(logo, cv2.COLOR_BGR2RGB)
        logo_norm = logo_rgb.astype(np.float32) / 255.0
        logo_batch = np.expand_dims(logo_norm, axis=0)
        
        self.interp.set_tensor(self.in_detail[0]['index'], logo_batch)
        self.interp.invoke()
        
        output = self.interp.get_tensor(self.out_detail[0]['index'])
        
        idx = np.argmax(output[0])
        conf = float(output[0][idx])
        
        return self.names[idx], conf, idx

# SERVO CONTROLLER
class Servo:
    def __init__(self):
        try:
            self.ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
            time.sleep(2)
            self.ok = True
            print(f"✓ Arduino ready")
        except:
            self.ok = False
            print("⚠ Arduino: Demo mode")
    
    def move(self, angle):
        if self.ok:
            try:
                self.ser.write(f"S{angle}\n".encode())
                self.ser.readline()
            except:
                pass
        print(f"✓ Servo: {angle}°")
    
    def close(self):
        if self.ok:
            try:
                self.ser.close()
            except:
                pass

# MAIN
def main():
    print("="*50)
    print("DETECT LOGO")
    print("="*50)
    
    # CHECK FILES
    print("\n[Checking files...]")
    if not os.path.exists(INPUT_IMAGE):
        print(f"✗ Image not found: {INPUT_IMAGE}")
        return False
    print(f"✓ Image: {INPUT_IMAGE}")
    
    if not os.path.exists(MODEL):
        print(f"✗ Model not found: {MODEL}")
        return False
    print(f"✓ Model: {MODEL}")
    
    if not os.path.exists(CLASSES):
        print(f"✗ Classes not found: {CLASSES}")
        return False
    print(f"✓ Classes: {CLASSES}")
    
    # INIT
    print("\n[Initializing...]")
    detector = LogoDetector()
    try:
        classifier = Classifier()
    except Exception as e:
        print(f"✗ Model error: {e}")
        return False
    
    servo = Servo()
    
    # PROCESS
    print("\n[Processing...]")
    
    print("\n[1/3] Detecting...")
    logo = detector.detect_and_crop(INPUT_IMAGE)
    if logo is None:
        print("✗ Logo not found")
        return False
    print("✓ Logo found")
    
    print("\n[2/3] Classifying...")
    name, conf, idx = classifier.classify(logo)
    print(f"✓ Class: {name} ({conf:.1%})")
    
    print("\n[3/3] Moving servo...")
    angle = SERVO_ANGLES.get(idx, 90)
    servo.move(angle)
    
    print("\n" + "="*50)
    print(f"DONE: {name} ({conf:.1%}) → {angle}°")
    print("="*50)
    
    servo.close()
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
