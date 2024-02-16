from glob import glob
import os
import shutil

path = '/public/home/liyh2022/projects/breast_data_preprocessing/benign/processed/MG/cropped/'
image_save_path = '/public/home/liyh2022/projects/breast_data_preprocessing/benign/processed/MG/detected/image/'
label_save_path = '/public/home/liyh2022/projects/breast_data_preprocessing/benign/processed/MG/detected/label/'
os.makedirs(image_save_path, exist_ok=True)
os.makedirs(label_save_path, exist_ok=True)

subjects = os.listdir(path)
for subject in subjects:
    subject_path = os.path.join(path, subject)
    images = glob(subject_path + '/**/cropped_breast.png',recursive=True)
    for image in images:
        view = image.split('/')[-2]
        id = image.split('/')[-3]
        shutil.copy(image, image_save_path + id + '_' + view + '.png')
        if os.path.exists(subject_path + '/' + view + '/tumor.txt'):
            shutil.copy(subject_path + '/' + view + '/tumor.txt', label_save_path + id + '_' + view + '.txt')