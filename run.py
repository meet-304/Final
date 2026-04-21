#!/usr/bin/env python3
"""
Fresh Start - Master Controller
Simple and clean orchestration
"""

import os
import subprocess
import time

# CONFIG
CAPTURE = 'capture.py'
DETECT = 'detect.py'

print("="*50)
print("MASTER CONTROLLER")
print("="*50)

# CHECK FILES
print("\n[Checking...]")
if not os.path.exists(CAPTURE):
    print(f"✗ {CAPTURE} not found")
    exit(1)
print(f"✓ {CAPTURE}")

if not os.path.exists(DETECT):
    print(f"✗ {DETECT} not found")
    exit(1)
print(f"✓ {DETECT}")

print("\n[Ready!]")
print("Ctrl+C to stop\n")

# MAIN LOOP
try:
    while True:
        print("\n" + "="*50)
        print("Step 1: CAPTURE")
        print("="*50)
        
        # Run capture
        result = subprocess.run(['python', CAPTURE])
        
        if result.returncode != 0:
            print("\n⚠ Capture failed")
            time.sleep(1)
            continue
        
        print("\n" + "="*50)
        print("Step 2: DETECT")
        print("="*50)
        
        # Run detect
        result = subprocess.run(['python', DETECT])
        
        if result.returncode == 0:
            print("\n✓ Detection done!")
        else:
            print("\n⚠ Detection failed")
        
        print("\n" + "="*50)
        print("Ready for next...")
        print("="*50)
        time.sleep(2)

except KeyboardInterrupt:
    print("\n\nStopped!")
