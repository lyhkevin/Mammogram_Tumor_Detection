from glob import glob
import numpy as np
from PIL import Image
from tqdm import tqdm
import shutil
import os

def yolo_to_center_coordinates(x_center, y_center, image_width, image_height):
    x_center = int(x_center * image_width)
    y_center = int(y_center * image_height)
    return x_center, y_center

def crop_centered_box(img, x_center, y_center, width, height):
    # Create a black image of the desired size
    cropped = Image.new('RGB', (width, height), (0, 0, 0))
    # Calculate the top-left coordinates of the cropping box
    start_x = x_center - width // 2
    start_y = y_center - height // 2
    # Calculate the region to be cropped from the original image
    crop_box = (
        max(start_x, 0),
        max(start_y, 0),
        min(start_x + width, img.width),
        min(start_y + height, img.height)
    )
    # Crop the image
    cropped_image = img.crop(crop_box)
    # Calculate where to paste the cropped image on the black background
    paste_position = (
        max(0, -start_x),
        max(0, -start_y)
    )
    # Paste the cropped image onto the black background
    cropped.paste(cropped_image, paste_position)
    return cropped

if __name__ == '__main__':
    subject_paths = glob('dataset/cropped_Surgical/*')
    save_root = 'dataset/Surgical_tumor/'
    for subject_path in tqdm(subject_paths):
        id = subject_path.split('/')[-1]
        print(id)
        views = glob(subject_path + '/*/')
        Left_tumor_size = 0
        Right_tumor_size = 0
        Left_tumor_num = 0
        Right_tumor_num = 0
        for view in views:
            if os.path.exists(view + 'tumor.txt'):
                view_name = view.split('/')[-2]
                with open(view + 'tumor.txt', 'r') as file:
                    line = file.readline().strip()
                    _, x_center, y_center, width, height = map(float, line.split())
                if view_name[0] == 'L':
                    Left_tumor_num = Left_tumor_num + 1
                    Left_tumor_size += width * height
                else:
                    Right_tumor_num = Right_tumor_num + 1
                    Right_tumor_size += width * height
                    
                img = Image.open(view + 'cropped_breast.png').convert('RGB')
                width, height = img.size
                x_center, y_center = yolo_to_center_coordinates(x_center, y_center, width, height)
                cropped = crop_centered_box(img, x_center, y_center, 768, 768)
                os.makedirs(save_root + id + '/tumor/', exist_ok=True)
                os.makedirs(save_root + id + '/original/', exist_ok=True)
                cropped.save(save_root + id + '/tumor/' + view_name + '.png')
                img.save(save_root + id + '/original/' + view_name + '.png')
        
        if Left_tumor_num < 2 and Right_tumor_num < 2:
            if os.path.exists(save_root + id):
                shutil.rmtree(save_root + id)
                print('remove ' + save_root + id)
        else:
            if Left_tumor_num != Right_tumor_num:
                if Left_tumor_num > Right_tumor_num:
                    right_imgs = glob(save_root + id + '/*/R*.png')
                    for right_img in right_imgs:
                        os.remove(right_img)
                else:
                    left_imgs = glob(save_root + id + '/*/L*.png')
                    for left_img in left_imgs:
                        os.remove(left_img)
            else:
                if Left_tumor_size >= Right_tumor_size:
                    right_imgs = glob(save_root + id + '/*/R*.png')
                    for right_img in right_imgs:
                        os.remove(right_img)
                else:
                    left_imgs = glob(save_root + id + '/*/L*.png')
                    for left_img in left_imgs:
                        os.remove(left_img)

