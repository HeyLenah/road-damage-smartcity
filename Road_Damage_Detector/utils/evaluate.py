import matplotlib.pyplot as plt
import pandas as pd

def plot_learning_curve(csv_path):
    results = pd.read_csv(csv_path)
    results.columns = results.columns.str.strip()
    plt.figure(figsize=(10, 6))
    plt.plot(results['epoch'], results['train/box_loss'], label='Train Box Loss')
    plt.plot(results['epoch'], results['val/box_loss'], label='Val Box Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('YOLOv8 Learning Curve')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def show_metrics(model):
    metrics = model.val()
    print("\nEvaluation Metrics:")
    print("Precision:", metrics.box.mp)
    print("Recall:", metrics.box.mr)
    print("mAP@0.5:", metrics.box.map50)
    print("mAP@0.5:0.95:", metrics.box.map)
