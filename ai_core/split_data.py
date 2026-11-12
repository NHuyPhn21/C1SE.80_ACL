import os
import shutil
import random

def split_dataset(img_dir, lbl_dir, output_dir, split_ratio=0.8):
    # Tạo cấu trúc thư mục đích cho YOLO
    for folder in ['images/train', 'images/val', 'labels/train', 'labels/val']:
        os.makedirs(os.path.join(output_dir, folder), exist_ok=True)

    # Lấy danh sách ảnh
    valid_ext = ['.jpg', '.jpeg', '.png']
    images = [f for f in os.listdir(img_dir) if os.path.splitext(f)[1].lower() in valid_ext]

    # Xáo trộn ngẫu nhiên
    random.shuffle(images)

    # Chia tỉ lệ 80/20
    split_index = int(len(images) * split_ratio)
    train_images = images[:split_index]
    val_images = images[split_index:]

    def copy_files(file_list, split_type):
        count = 0
        for img_name in file_list:
            base_name = os.path.splitext(img_name)[0]
            txt_name = base_name + '.txt'

            src_img = os.path.join(img_dir, img_name)
            # Trỏ đến thư mục chứa file .txt riêng biệt
            src_txt = os.path.join(lbl_dir, txt_name) 

            # Chỉ copy nếu ảnh đó đã được gắn nhãn (có file .txt đi kèm)
            if os.path.exists(src_txt):
                shutil.copy(src_img, os.path.join(output_dir, f'images/{split_type}', img_name))
                shutil.copy(src_txt, os.path.join(output_dir, f'labels/{split_type}', txt_name))
                count += 1
            else:
                print(f"Cảnh báo: Không tìm thấy file nhãn {src_txt} cho ảnh {img_name}")
        return count

    print(f"Đã tìm thấy {len(images)} ảnh. Bắt đầu chia...")
    train_count = copy_files(train_images, 'train')
    val_count = copy_files(val_images, 'val')

    print(f"Hoàn tất! Train: {train_count} ảnh | Val: {val_count} ảnh.")
    print(f"Dữ liệu đã sẵn sàng tại thư mục: {output_dir}")

if __name__ == '__main__':
    # Cấu hình lại đúng với cấu trúc thư mục hiện tại của bạn
    IMG_DIRECTORY = "data/images"
    LBL_DIRECTORY = "data/labels"
    OUTPUT_DIRECTORY = "manga_dataset"
    
    split_dataset(IMG_DIRECTORY, LBL_DIRECTORY, OUTPUT_DIRECTORY)