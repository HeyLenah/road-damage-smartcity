# -*- coding: utf-8 -*-
"""RoadDamage_Detection.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1CpG4Ck2l3XcGYXAA2wKVvVyUMBvThKMR

#Import Necessary libraries
"""

import os
import numpy as np
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import random
import matplotlib.image as mpimg
import shutil
import cv2

!nvidia-smi

"""#Loading Dataset + Train/test split"""

!pip install roboflow

from roboflow import Roboflow
rf = Roboflow(api_key="KcK8P8DwDoIznWH04X4F")
project = rf.workspace("rdetect").project("road-damage-detection-ndadw")
version = project.version(1)
dataset = version.download("yolov8")

"""**Train/Test split**"""

def re_split_exact(root_path, label_ext=".txt"):
    print("🔄 Re-splitting dataset to 70% train, 20% valid, 10% test...")

    tmp_images = os.path.join(root_path, "tmp_all", "images")
    tmp_labels = os.path.join(root_path, "tmp_all", "labels")
    os.makedirs(tmp_images, exist_ok=True)
    os.makedirs(tmp_labels, exist_ok=True)

    for split in ["train", "valid", "test"]:
        for img in os.listdir(os.path.join(root_path, split, "images")):
            shutil.copy(os.path.join(root_path, split, "images", img), os.path.join(tmp_images, img))
            lbl = os.path.splitext(img)[0] + label_ext
            lbl_path = os.path.join(root_path, split, "labels", lbl)
            if os.path.exists(lbl_path):
                shutil.copy(lbl_path, os.path.join(tmp_labels, lbl))

    all_images = sorted(os.listdir(tmp_images))
    random.shuffle(all_images)

    total = len(all_images)
    train_count = 1117 # 70%
    valid_count = 319   # 20%
    test_count  = total - train_count - valid_count

    splits = {
        "train": all_images[:train_count],
        "valid": all_images[train_count:train_count + valid_count],
        "test":  all_images[train_count + valid_count:]
    }

    for split in ["train", "valid", "test"]:
        shutil.rmtree(os.path.join(root_path, split), ignore_errors=True)

    # Create new splits
    for split, files in splits.items():
        img_out = os.path.join(root_path, split, "images")
        lbl_out = os.path.join(root_path, split, "labels")
        os.makedirs(img_out, exist_ok=True)
        os.makedirs(lbl_out, exist_ok=True)

        for img in files:
            base = os.path.splitext(img)[0]
            shutil.copy(os.path.join(tmp_images, img), os.path.join(img_out, img))
            lbl_file = base + label_ext
            lbl_path = os.path.join(tmp_labels, lbl_file)
            if os.path.exists(lbl_path):
                shutil.copy(lbl_path, os.path.join(lbl_out, lbl_file))

    # Clean temp
    shutil.rmtree(os.path.join(root_path, "tmp_all"))
    print(f"✅ Done! 70/20/10 exact split: {train_count} train, {valid_count} valid, {test_count} test.")


re_split_exact("/content/Road-Damage-Detection-1")

def check_split_ratios(base_path):
    def count_split(split):
        img_dir = os.path.join(base_path, split, "images")
        lbl_dir = os.path.join(base_path, split, "labels")
        imgs = os.listdir(img_dir) if os.path.exists(img_dir) else []
        lbls = os.listdir(lbl_dir) if os.path.exists(lbl_dir) else []
        return len(imgs), len(lbls)

    train_imgs, train_lbls = count_split("train")
    valid_imgs, valid_lbls = count_split("valid")
    test_imgs, test_lbls = count_split("test")

    total = train_imgs + valid_imgs + test_imgs

    print("📊 Final Split Ratios:")
    print(f"Train: {train_imgs} images ({train_imgs / total:.2%}), {train_lbls} labels")
    print(f"Valid: {valid_imgs} images ({valid_imgs / total:.2%}), {valid_lbls} labels")
    print(f"Test : {test_imgs} images ({test_imgs / total:.2%}), {test_lbls} labels")
    print(f"Total: {total} images")


check_split_ratios("/content/Road-Damage-Detection-1")

"""#EDA

**Image size**
"""

path = dataset.location

for split in ['train', 'valid', 'test']:
    img_dir = os.path.join(path, split, 'images')
    first_img = os.listdir(img_dir)[0]
    img_path = os.path.join(img_dir, first_img)

    with Image.open(img_path) as img:
        width, height = img.size

    print(f"{split.capitalize()} first image size: {width}x{height}")

"""**Number and Ratio for Train/Valid/Test**"""

def count_images(split, path):
    img_dir = os.path.join(path, split, "images")
    return len(os.listdir(img_dir))

train_count = count_images("train", dataset.location)
valid_count = count_images("valid", dataset.location)
test_count  = count_images("test", dataset.location)

total = train_count + valid_count + test_count

train_ratio = train_count / total
valid_ratio = valid_count / total
test_ratio  = test_count / total

print(f"Train: {train_count} images ({train_ratio:.2%})")
print(f"Valid: {valid_count} images ({valid_ratio:.2%})")
print(f"Test:  {test_count} images ({test_ratio:.2%})")
print(total)

"""**Inspect Sample Annotations**"""

path= '/content/Road-Damage-Detection-1/train/images'
image_files = [f for f in os.listdir(path) if f.endswith(('jpg', 'png', 'jpeg'))]

num_samples = 6
sample_images = random.sample(image_files, num_samples)


plt.figure(figsize=(15, 8))

for i, img_filename in enumerate(sample_images):
    img_path = os.path.join(path, img_filename)
    img = mpimg.imread(img_path)


    plt.subplot(2, 3, i + 1)
    plt.imshow(img)
    plt.axis('off')

plt.suptitle('Sample', fontsize=20)

plt.show()

def plot_yolo_annotation(image_path, label_path, class_names=None):
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w, _ = img.shape

    with open(label_path, 'r') as f:
        lines = f.readlines()

    for line in lines:
        parts = line.strip().split()
        class_id = int(parts[0])
        x_center, y_center, box_w, box_h = map(float, parts[1:])

        # Convert YOLO format to pixel coordinates
        x1 = int((x_center - box_w / 2) * w)
        y1 = int((y_center - box_h / 2) * h)
        x2 = int((x_center + box_w / 2) * w)
        y2 = int((y_center + box_h / 2) * h)

        label = class_names[class_id] if class_names else str(class_id)
        cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 2)
        cv2.putText(img, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)

    plt.figure(figsize=(8, 8))
    plt.imshow(img)
    plt.axis('off')
    plt.title(os.path.basename(image_path))
    plt.show()


image_path = "/content/Road-Damage-Detection-1/train/images/img-100_jpg.rf.5c42e028489b43fe370f913bf0e84328.jpg"
label_path = "/content/Road-Damage-Detection-1/train/labels/img-100_jpg.rf.5c42e028489b43fe370f913bf0e84328.txt"
class_names = ["pothole"]


plot_yolo_annotation(image_path, label_path, class_names)

# Image Counts
labels = ['Train', 'Valid', 'Test']
counts = [train_count, valid_count, test_count]
plt.figure(figsize=(8, 6))
plt.bar(labels, counts, color=['skyblue', 'lightgreen', 'lightcoral'])
plt.title('Number of Images per Split')
plt.xlabel('Data Split')
plt.ylabel('Number of Images')
plt.grid(axis='y', linestyle='--')
plt.show()

# Image Ratios
ratios = [train_ratio, valid_ratio, test_ratio]
labels_ratio = [f'Train ({train_ratio:.1%})', f'Valid ({valid_ratio:.1%})', f'Test ({test_ratio:.1%})']
colors = ['skyblue', 'lightgreen', 'lightcoral']
explode = (0.05, 0.05, 0.05)

plt.figure(figsize=(8, 8))
plt.pie(ratios, labels=labels_ratio, colors=colors, autopct='%1.1f%%', startangle=140, explode=explode)
plt.title('Ratio of Images per Split')
plt.axis('equal')
plt.show()

def get_all_image_files(path):
    all_images = []
    for split in ['train', 'valid', 'test']:
        img_dir = os.path.join(path, split, "images")
        try:
            files = [os.path.join(img_dir, f) for f in os.listdir(img_dir) if os.path.isfile(os.path.join(img_dir, f))]
            all_images.extend(files)
        except FileNotFoundError:
            print(f"Warning: Directory not found: {img_dir}")
    return all_images

image_files = get_all_image_files(dataset.location)
print(f"Total number of image files found: {len(image_files)}")

# Distribution of Image Sizes
image_sizes = []
for img_path in image_files:
    try:
        with Image.open(img_path) as img:
            width, height = img.size
            image_sizes.append((width, height))
    except Exception as e:
        print(f"Error opening image {img_path}: {e}")

if image_sizes:
    widths, heights = zip(*image_sizes)

    plt.figure(figsize=(8, 6))
    sns.histplot(widths, bins=30, kde=True, color='skyblue')
    plt.title('Distribution of Image Widths')
    plt.xlabel('Width (pixels)')
    plt.ylabel('Frequency')
    plt.show()

    plt.figure(figsize=(8, 6))
    sns.histplot(heights, bins=30, kde=True, color='lightgreen')
    plt.title('Distribution of Image Heights')
    plt.xlabel('Height (pixels)')
    plt.ylabel('Frequency')
    plt.show()

    plt.figure(figsize=(8, 6))
    sns.scatterplot(x=widths, y=heights, alpha=0.6)
    plt.title('Image Dimensions Scatter Plot')
    plt.xlabel('Width (pixels)')
    plt.ylabel('Height (pixels)')
    plt.grid(True)
    plt.show()
else:
    print("No images were successfully processed to analyze sizes.")

"""#Baseline"""



"""#Training"""



"""#Evaluation

"""

