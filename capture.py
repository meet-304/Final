#!/usr/bin/env python3
"""
Fresh Start - Capture Image
Simple and clean - only essential code
"""

import os
import time
import subprocess
from datetime import datetime

# CONFIG
IR_SENSOR_PIN = 17
OUTPUT_DIR = 'captured_images'
OUTPUT_IMAGE = f'{OUTPUT_DIR}/image.jpg'
DEBOUNCE = 2.0

# Create directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

# IR SENSOR CLASS
class IRSensor:
    def __init__(self, pin):
        self.pin = pin
        try:
            import RPi.GPIO as GPIO
            self.GPIO = GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(pin, GPIO.IN)
            self.ready = True
            print(f"✓ IR Sensor on GPIO {pin}")
        except:
            self.ready = False
            print("⚠ IR Sensor: Demo mode")
    
    def detected(self):
        if self.ready:
            try:
                return self.GPIO.input(self.pin) == 0
            except:
                return False
        return False
    
    def cleanup(self):
        if self.ready:
            try:
                self.GPIO.cleanup()
            except:
                pass

# CAMERA CLASS
class Camera:
    def __init__(self):
        print("✓ Camera ready")
    
    def capture(self, path):
        try:
            cmd = ['rpicam-still', '-o', path, '-n']
            result = subprocess.run(cmd, timeout=10, capture_output=True)
            return result.returncode == 0 and os.path.exists(path)
        except:
            return False

# MAIN
def main():
    print("="*50)
    print("CAPTURE IMAGE")
    print("="*50)
    
    sensor = IRSensor(IR_SENSOR_PIN)
    camera = Camera()
    
    print("\n[Waiting for object...]")
    print("(Ctrl+C to stop)\n")
    
    last_time = 0
    
    try:
        while True:
            if sensor.detected():
                now = time.time()
                if now - last_time > DEBOUNCE:
                    last_time = now
                    
                    print("\n" + "="*50)
                    print("OBJECT DETECTED!")
                    print("="*50)
                    print("\n[Capturing...]")
                    
                    if camera.capture(OUTPUT_IMAGE):
                        print(f"✓ Saved: {OUTPUT_IMAGE}\n")
                        return True
                    else:
                        print("✗ Capture failed\n")
            
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        print("\n\nStopped!")
        sensor.cleanup()
        return False

if __name__ == "__main__":
    main()
