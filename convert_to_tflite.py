#!/usr/bin/env python3
"""
Convert SavedModel to TFLite for RPi
TensorFlow 2.12.0
"""

import tensorflow as tf
import os

MODEL_PATH = '/Users/mac/Documents/IPPR Project/AutoSort/logo_model_optimized.h5'
TFLITE_PATH = 'logo_model.tflite'

print("="*60)
print("CONVERTING TO TFLITE")
print("="*60)

print("\n[STEP 1] Loading model...")
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    print("✓ Loaded successfully")
except Exception as e:
    print(f"✗ Error loading model: {e}")
    exit(1)

print("\n[STEP 2] Converting to TFLite...")
try:
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.target_spec.supported_ops = [
        tf.lite.OpsSet.TFLITE_BUILTINS,
        tf.lite.OpsSet.SELECT_TF_OPS
    ]
    
    tflite_model = converter.convert()
    print("✓ Converted successfully")
except Exception as e:
    print(f"✗ Error converting: {e}")
    exit(1)

print(f"\n[STEP 3] Saving to {TFLITE_PATH}...")
try:
    with open(TFLITE_PATH, 'wb') as f:
        f.write(tflite_model)
    
    size_mb = os.path.getsize(TFLITE_PATH) / 1024 / 1024
    print(f"✓ Saved successfully: {size_mb:.1f} MB")
except Exception as e:
    print(f"✗ Error saving: {e}")
    exit(1)

print("\n" + "="*60)
print("CONVERSION COMPLETE!")
print("="*60)
print(f"\nFiles ready for RPi:")
print(f"  1. {TFLITE_PATH} (the model)")
print(f"  2. classes.json (class names)")
print(f"\nNext step:")
print(f"  scp {TFLITE_PATH} pi@raspberrypi.local:~/")
print(f"  scp classes.json pi@raspberrypi.local:~/")
