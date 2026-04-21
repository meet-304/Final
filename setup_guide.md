# Conveyor Belt Sorting System - Setup Guide

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│           CONVEYOR BELT SORTING SYSTEM                   │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  IR Sensor (GPIO 17) → Object Detection                 │
│        ↓                                                  │
│  Raspberry Pi Camera → Image Capture                     │
│        ↓                                                  │
│  TensorFlow Lite Model → Classification                 │
│        ↓                                                  │
│  Arduino (Serial /dev/ttyACM0) → Servo Control          │
│        ↓                                                  │
│  Servo Motor (PWM Pin 9) → Product Diversion            │
│        ↓                                                  │
│  Streamlit Dashboard → Monitoring & Analytics           │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## Hardware Setup

### 1. GPIO Pin Assignments (Raspberry Pi)

| Component | GPIO Pin | Type | Purpose |
|-----------|----------|------|---------|
| IR Sensor | GPIO 17 (Pin 11) | INPUT | Object detection |
| Ground | Ground (Pin 6/9/14/20/25/30/34/39) | - | Common ground |
| 3.3V Power | 3V3 (Pin 1/17) | OUTPUT | Power supply |
| 5V Power | 5V (Pin 2/4) | OUTPUT | Power supply |

### 2. Wiring IR Sensor to Raspberry Pi

```
IR Sensor (3-pin module):
├─ VCC (Red) → RPi Pin 2 (5V Power)
├─ GND (Black) → RPi Pin 6 (Ground)
└─ OUT (Yellow/White) → RPi Pin 11 (GPIO 17)
```

**Note:** IR sensor output goes LOW when object is detected

### 3. Arduino to Raspberry Pi Connection

**Serial Communication:**
- USB Cable: Raspberry Pi USB port ↔ Arduino Uno R3 USB port
- Default port: `/dev/ttyACM0`
- Baud rate: `9600`
- Protocol: Serial strings in format `S{angle}\n`

### 4. Arduino to Servo Motor Connection

```
Servo Motor (3-pin connector):
├─ Orange/Red (Signal) → Arduino Pin 9 (PWM)
├─ Red (5V) → Arduino 5V
└─ Brown (GND) → Arduino GND
```

### 5. Raspberry Pi Camera Setup

```
Camera Module (Ribbon cable):
├─ Insert ribbon cable into CSI port (between USB and audio jack)
├─ Push connector down firmly
├─ Ensure gold contacts face toward USB ports
```

### 6. Power Supply

- Raspberry Pi: 5V, 2A USB-C power supply (minimum)
- Arduino: Gets 5V from Pi via USB connection
- Servo Motor: Requires separate 5-6V power supply (current capacity: 1-2A)
- **Important:** Use common ground between all components

---

## Software Installation

### Step 1: Update Raspberry Pi

```bash
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y python3-pip python3-dev
```

### Step 2: Install Python Dependencies

```bash
cd /path/to/your/sorting-system
pip3 install -r requirements.txt
```

### Step 3: Enable Camera Interface

```bash
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable → Reboot
```

### Step 4: Verify Serial Connection to Arduino

```bash
# Check if Arduino is detected
ls -la /dev/ttyACM*

# Test serial connection (optional)
minicom -b 9600 -o -D /dev/ttyACM0
# Type 'S90' and press Enter to test servo
# Press Ctrl+A then X to exit
```

### Step 5: Grant GPIO Permissions

```bash
# Run sorting script with sudo for GPIO access
# OR add user to GPIO group:
sudo usermod -a -G gpio $USER
# Log out and log back in
```

---

## Model Preparation

### Requirements for Your TensorFlow Lite Model

1. **Model Format:** `.tflite` file (quantized)
2. **Input Shape:** Model should accept images (check your model's input dimensions)
3. **Output:** Should output 3 class scores
4. **Classes:** In order: `super`, `bat`, `fun`
5. **File Location:** Place `model.tflite` in the project root directory

### How to Convert Your Model to TFlite (if needed)

```python
# If you have a Keras/TensorFlow model:
import tensorflow as tf

# Load your model
model = tf.keras.models.load_model('your_model.h5')

# Convert to TFlite
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

# Save
with open('model.tflite', 'wb') as f:
    f.write(tflite_model)
```

### Verify Model

```python
import tensorflow as tf

interpreter = tf.lite.Interpreter(model_path='model.tflite')
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

print(f"Input shape: {input_details[0]['shape']}")
print(f"Output shape: {output_details[0]['shape']}")
```

---

## Arduino Code Upload

### 1. Install Arduino IDE

```bash
# On your development machine (Windows/Mac/Linux):
# Download from: https://www.arduino.cc/en/software
```

### 2. Upload Servo Control Sketch

1. Open Arduino IDE
2. Open `arduino_servo_control.ino`
3. Select: Tools → Board → Arduino Uno
4. Select: Tools → Port → `/dev/ttyACM0` (or your Arduino port)
5. Click Upload
6. Wait for "Done uploading" message

### 3. Test Arduino Connection

```python
import serial
import time

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)  # Wait for Arduino

# Test different angles
for angle in [0, 90, 180]:
    ser.write(f"S{angle}\n".encode())
    response = ser.readline().decode().strip()
    print(f"Angle: {angle}°, Response: {response}")
    time.sleep(0.5)

ser.close()
```

---

## Configuration Variables

### In `sorting_system.py`

Update these constants based on your setup:

```python
# GPIO PINS
IR_SENSOR_PIN = 17  # Change if using different pin

# CAMERA SETTINGS
CAMERA_RESOLUTION = (640, 480)  # Adjust for your camera
TEST_IMAGE_DIR = "test_images"

# MODEL SETTINGS
MODEL_PATH = "model.tflite"  # Path to your model
CLASS_NAMES = ["super", "bat", "fun"]  # Must match model training

# ARDUINO SETTINGS
ARDUINO_PORT = "/dev/ttyACM0"  # Check with: ls -la /dev/ttyACM*
BAUD_RATE = 9600

# SERVO ANGLES (customize based on physical setup)
SERVO_ANGLES = {
    0: 90,    # super → center (straight)
    1: 180,   # bat → right
    2: 0      # fun → left
}

# DEBOUNCE TIME
DEBOUNCE_TIME = 2.0  # Seconds between detections
```

---

## Running the System

### Terminal 1: Start Main Sorting System

```bash
cd /path/to/sorting-system
python3 sorting_system.py
```

Expected output:
```
Sorting system started. Waiting for objects...
--- Object Detected ---
Capturing image...
Running inference...
Detected: super (confidence: 92.34%)
Sending servo angle: 90°
✓ Object sorted to class: super
```

### Terminal 2: Start Web Dashboard (on Raspberry Pi or another machine)

```bash
cd /path/to/sorting-system
streamlit run dashboard.py --server.port 8501
```

Access dashboard at: `http://raspberry-pi-ip:8501`

---

## File Structure

```
sorting-system/
├── sorting_system.py           # Main sorting script
├── dashboard.py                # Streamlit web interface
├── arduino_servo_control.ino   # Arduino firmware
├── requirements.txt            # Python dependencies
├── model.tflite               # Your trained model
├── inference_log.json         # Auto-generated log
├── test_images/               # Auto-generated folder for images
│   ├── object_20231101_120000.jpg
│   ├── object_20231101_120002.jpg
│   └── ...
└── setup_guide.md             # This file
```

---

## Troubleshooting

### Issue: "No module named 'picamera2'"

```bash
sudo apt-get install -y python3-picamera2
# Or reinstall: pip3 install --upgrade picamera2
```

### Issue: "Cannot connect to Arduino"

```bash
# Check Arduino is detected:
ls -la /dev/ttyACM*

# If /dev/ttyACM0 doesn't exist:
dmesg | tail -20  # Check system logs

# Verify Arduino drivers (on Mac/Windows):
# Install: https://github.com/arduino/ArduinoCore-avr
```

### Issue: "Permission denied" for GPIO

```bash
# Run with sudo:
sudo python3 sorting_system.py

# Or add user to gpio group:
sudo usermod -a -G gpio $USER
sudo usermod -a -G dialout $USER
# Log out and back in
```

### Issue: "Model inference returns None"

```python
# Check model compatibility:
# 1. Verify model accepts 3-channel RGB images
# 2. Check input shape matches preprocessing
# 3. Test model separately:

import tensorflow as tf
import cv2
import numpy as np

interpreter = tf.lite.Interpreter(model_path='model.tflite')
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

print(f"Input: {input_details[0]['shape']}")
print(f"Input type: {input_details[0]['dtype']}")
print(f"Output: {output_details[0]['shape']}")
```

### Issue: Servo doesn't move

```python
# 1. Test with direct angle command:
import serial
ser = serial.Serial('/dev/ttyACM0', 9600)
ser.write(b'S90\n')
print(ser.readline())
ser.close()

# 2. Check Arduino Serial Monitor for responses
# 3. Verify servo is powered (5-6V)
# 4. Test servo with standard Arduino servo example
```

### Issue: IR sensor not detecting

```python
# Test IR sensor directly:
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)

for i in range(20):
    print(f"GPIO 17: {GPIO.input(17)}")
    time.sleep(0.5)

GPIO.cleanup()

# Should print 0 when object detected, 1 otherwise
```

---

## Performance Optimization Tips

1. **Camera Resolution:** Lower resolution = faster processing
   ```python
   CAMERA_RESOLUTION = (320, 240)  # For faster inference
   ```

2. **Model Optimization:** Already using quantized model (good!)

3. **Batch Processing:** Add delay to allow object movement
   ```python
   DEBOUNCE_TIME = 2.5  # Increase if objects too fast
   ```

4. **Servo Speed:** Check servo specs for fastest movement

5. **Conveyor Speed:** Ensure objects spend 1-2 seconds over camera

---

## Data Logging

### Log File Format (`inference_log.json`)

```json
{
  "super": {
    "count": 45,
    "images": [
      {
        "path": "test_images/object_20231101_120000.jpg",
        "timestamp": "2023-11-01T12:00:00.123456"
      }
    ]
  },
  "bat": {
    "count": 32,
    "images": [...]
  },
  "fun": {
    "count": 28,
    "images": [...]
  }
}
```

### Access Statistics

```python
import json

with open('inference_log.json', 'r') as f:
    data = json.load(f)

for class_name, class_data in data.items():
    print(f"{class_name}: {class_data['count']} objects")
```

---

## Next Steps & Enhancements

1. **Add confidence threshold:** Skip low-confidence predictions
2. **Add multiple servo gates:** Control 5-7 different paths
3. **Add weight sensor:** Log product weights
4. **Add error handling:** Retry on failed detection
5. **Add email alerts:** Notify on errors
6. **Add database:** PostgreSQL/MongoDB for long-term logging
7. **Add mobile app:** React Native dashboard
8. **Add ML retraining:** Auto-improve model with new data

---

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review GitHub issues
3. Test components individually
4. Enable debug logging in code

Good luck with your project! 🚀
