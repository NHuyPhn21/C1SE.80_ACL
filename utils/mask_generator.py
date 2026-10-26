import cv2
import numpy as np


def generate_inpainting_mask(image_shape: tuple, bboxes: list, padding: int = 6, kernel_size: int = 3) -> np.ndarray:
   
    height, width = image_shape[:2]
    mask = np.zeros((height, width), dtype=np.uint8)

    for box in bboxes:
        x1, y1, x2, y2 = map(int, box)

        x1_pad = max(0, x1 - padding)
        y1_pad = max(0, y1 - padding)
        x2_pad = min(width, x2 + padding)
        y2_pad = min(height, y2 + padding)

        cv2.rectangle(mask, (x1_pad, y1_pad), (x2_pad, y2_pad), color=255, thickness=-1)

    
    if kernel_size > 0:
        kernel = np.ones((kernel_size, kernel_size), dtype=np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=1)

    return mask