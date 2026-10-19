import torch
from ultralytics import YOLO

# Lưu lại hàm load gốc của PyTorch
_original_load = torch.load

# Viết đè một hàm load mới, luôn luôn ép tham số weights_only=False
def patched_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return _original_load(*args, **kwargs)

# Gắn hàm mới thay thế cho hàm load mặc định của hệ thống
torch.load = patched_load
# ------------------------------------------

def main():
    # Load mô hình YOLOv8 phiên bản nano
    model = YOLO('yolov8n.pt')

    # Bắt đầu quá trình huấn luyện
    results = model.train(
        data='manga.yaml',
        epochs=50,
        imgsz=640,
        batch=4,
        workers=1,
        project='models/yolo',
        name='manga_v1',
        device=0  # 
    )

if __name__ == '__main__':
    main()