#!/usr/bin/env python3
"""
Data Augmentation Script - Generate Synthetic Data from Existing Images
Uses:
- Affine Transformations (rotation, shear, translation)
- Brightness/Contrast adjustments
- Blur and Noise
- Creates 10x dataset from original images!
"""

import os
import cv2
import numpy as np
import albumentations as A
from pathlib import Path

# ==================== CONFIG ====================
DATASET_DIR = '/Users/mac/Documents/IPPR Project/AutoSort/data'
OUTPUT_DIR = 'logo_dataset'
AUGMENTATIONS_PER_IMAGE = 12  # Create 10 versions per original image

print("="*60)
print("DATA AUGMENTATION - GENERATE SYNTHETIC IMAGES")
print("="*60)

# ==================== AUGMENTATION PIPELINE ====================
def create_augmenters():
    """Create multiple augmentation strategies"""
    
    augmenters = [
        # Augmenter 1: Affine + Brightness
        A.Compose([
            A.Affine(scale=(0.8, 1.2), p=1.0),  # Scale 80-120%
            A.RandomBrightnessContrast(brightness_limit=0.3, contrast_limit=0.3, p=1.0),
            A.Blur(blur_limit=3, p=0.5),
        ]),
        
        # Augmenter 2: Rotation + Brightness
        A.Compose([
            A.Rotate(limit=30, p=1.0),  # ±30 degrees
            A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=1.0),
        ]),
        
        # Augmenter 3: Shear + Noise
        A.Compose([
            A.Affine(shear=(-20, 20), p=1.0),  # Shear transform
            A.GaussNoise(p=0.3),
            A.RandomBrightnessContrast(brightness_limit=0.15, p=1.0),
        ]),
        
        # Augmenter 4: Perspective + Brightness
        A.Compose([
            A.Perspective(scale=(0.05, 0.1), p=1.0),
            A.RandomBrightnessContrast(brightness_limit=0.25, p=1.0),
            A.Blur(blur_limit=2, p=0.3),
        ]),
        
        # Augmenter 5: Horizontal Flip + Brightness
        A.Compose([
            A.HorizontalFlip(p=1.0),
            A.RandomBrightnessContrast(brightness_limit=0.2, p=1.0),
        ]),
        
        # Augmenter 6: Vertical Flip + Rotation
        A.Compose([
            A.VerticalFlip(p=1.0),
            A.Rotate(limit=15, p=1.0),
            A.RandomBrightnessContrast(brightness_limit=0.2, p=1.0),
        ]),
        
        # Augmenter 7: Elastic Transform + Brightness
        A.Compose([
            A.ElasticTransform(alpha=1, sigma=50, alpha_affine=50, p=1.0),
            A.RandomBrightnessContrast(brightness_limit=0.1, p=1.0),
        ]),
        
        # Augmenter 8: Color Jitter
        A.Compose([
            A.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2, hue=0.1, p=1.0),
            A.Rotate(limit=20, p=0.7),
        ]),
        
        # Augmenter 9: Slight Rotation + Strong Brightness
        A.Compose([
            A.Rotate(limit=10, p=1.0),
            A.RandomBrightnessContrast(brightness_limit=0.4, contrast_limit=0.3, p=1.0),
        ]),
        
        # Augmenter 10: Affine + Noise + Brightness
        A.Compose([
            A.Affine(scale=(0.9, 1.1), translate_percent=(-0.1, 0.1), p=1.0),
            A.GaussNoise(p=0.4),
            A.RandomBrightnessContrast(brightness_limit=0.2, p=1.0),
            A.Blur(blur_limit=2, p=0.3),
        ]),
    ]
    
    return augmenters

# ==================== AUGMENTATION FUNCTION ====================
def augment_image(image, augmenter, aug_num):
    """Apply augmentation to single image"""
    try:
        augmented = augmenter(image=image)
        return augmented['image']
    except Exception as e:
        print(f"  Error in augmentation {aug_num}: {e}")
        return image

# ==================== MAIN AUGMENTATION ====================
def augment_dataset():
    """Augment entire dataset"""
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    augmenters = create_augmenters()
    
    print(f"\n[INFO] Augmenters created: {len(augmenters)}")
    print(f"[INFO] Will create {AUGMENTATIONS_PER_IMAGE} versions per image")
    
    # Process each class
    total_original = 0
    total_augmented = 0
    
    for class_name in sorted(os.listdir(DATASET_DIR)):
        class_dir = os.path.join(DATASET_DIR, class_name)
        
        if not os.path.isdir(class_dir):
            continue
        
        output_class_dir = os.path.join(OUTPUT_DIR, class_name)
        os.makedirs(output_class_dir, exist_ok=True)
        
        print(f"\n[PROCESSING] {class_name}")
        
        class_original = 0
        class_augmented = 0
        
        # Process each image in class
        for filename in sorted(os.listdir(class_dir)):
            if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue
            
            image_path = os.path.join(class_dir, filename)
            
            try:
                # Load image
                img = cv2.imread(image_path)
                if img is None:
                    print(f"  ✗ Failed to load: {filename}")
                    continue
                
                # Save original
                base_name = os.path.splitext(filename)[0]
                original_output = os.path.join(output_class_dir, f"{base_name}_original.jpg")
                cv2.imwrite(original_output, img)
                class_original += 1
                class_augmented += 1
                
                # Generate augmented versions
                for aug_num in range(AUGMENTATIONS_PER_IMAGE):
                    augmenter = augmenters[aug_num % len(augmenters)]
                    aug_img = augment_image(img, augmenter, aug_num)
                    
                    # Save augmented image
                    aug_name = f"{base_name}_aug_{aug_num}.jpg"
                    aug_path = os.path.join(output_class_dir, aug_name)
                    cv2.imwrite(aug_path, aug_img)
                    class_augmented += 1
                
                print(f"  ✓ {filename}: +{AUGMENTATIONS_PER_IMAGE} versions")
            
            except Exception as e:
                print(f"  ✗ Error processing {filename}: {e}")
        
        print(f"  Class Summary:")
        print(f"    Original images: {class_original}")
        print(f"    Total after augmentation: {class_augmented}")
        
        total_original += class_original
        total_augmented += class_augmented
    
    print(f"\n{'='*60}")
    print(f"AUGMENTATION COMPLETE!")
    print(f"{'='*60}")
    print(f"\nDataset Summary:")
    print(f"  Original images: {total_original}")
    print(f"  Total images after augmentation: {total_augmented}")
    print(f"  Multiplication factor: {total_augmented / total_original:.1f}x")
    print(f"\nAugmented dataset saved to: {OUTPUT_DIR}/")
    print(f"\nNext step:")
    print(f"  Update train_tensorflow.py:")
    print(f"    DATASET_DIR = '{OUTPUT_DIR}'  # Use augmented dataset")
    print(f"  Then run: python train_tensorflow.py")

# ==================== MAIN ====================
if __name__ == "__main__":
    # Check if original dataset exists
    if not os.path.exists(DATASET_DIR):
        print(f"ERROR: {DATASET_DIR} not found!")
        print(f"Create it first and add images to {DATASET_DIR}/SUPER/, etc.")
        exit(1)
    
    # Count images
    total_images = 0
    for class_name in os.listdir(DATASET_DIR):
        class_dir = os.path.join(DATASET_DIR, class_name)
        if os.path.isdir(class_dir):
            count = len([f for f in os.listdir(class_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            total_images += count
            print(f"Found: {count} images in {class_name}/")
    
    if total_images == 0:
        print("ERROR: No images found in dataset!")
        exit(1)
    
    print(f"\nTotal images to augment: {total_images}")
    print(f"Will create: {total_images * AUGMENTATIONS_PER_IMAGE} total images\n")
    
    response = input("Continue with augmentation? (y/n): ")
    if response.lower() == 'y':
        augment_dataset()
    else:
        print("Cancelled.")
