import numpy as np
import pandas as pd
import re
from glob import glob
import os
from tqdm import tqdm
import shutil

clinical_1 = 'D:/projects/breast_data_preprocessing/benign/raw/乳腺良性2021-1200-已收集完.xlsx'
clinical_2 = 'D:/projects/breast_data_preprocessing/benign/raw/乳腺炎症病变-已收集完-20240119.xlsx'
clinical_1 = pd.read_excel(clinical_1)
clinical_2 = pd.read_excel(clinical_2)
image_root = 'D:/projects/breast_data_preprocessing/benign/processed/MG/detected/image/'
label_root = 'D:/projects/breast_data_preprocessing/benign/processed/MG/detected/label/'
image_save_root = 'D:/projects/breast_data_preprocessing/benign/processed/MG/cropped/image/'
label_save_root = 'D:/projects/breast_data_preprocessing/benign/processed/MG/cropped/label/'
os.makedirs(image_save_root, exist_ok=True)
os.makedirs(label_save_root, exist_ok=True)

image_paths = glob(image_root + '*')
clinical_1['住院号'] = clinical_1['住院号'].astype(str)
clinical_2['住院号'] = clinical_2['住院号'].astype(str)
for image_path in tqdm(image_paths):
    label_path = label_root + image_path.split('\\')[-1].split('.')[0] + '.txt'
    id = re.findall(r'\d+', image_path)[-1]
    id = id.lstrip("0")
    rows_clinical_1 = clinical_1[clinical_1['住院号'] == id]
    rows_clinical_2 = clinical_2[clinical_2['住院号'] == id]
    if rows_clinical_1.shape[0] == 0 and rows_clinical_2.shape[0] == 0:
        continue
    if rows_clinical_1.shape[0] > 0:
        description = rows_clinical_1['诊断描述'].values[0]
        new_id = rows_clinical_1['编号'].values[0]
    else:
        description = rows_clinical_2['医生主要诊断描述'].values[0]
        new_id = rows_clinical_2['编号'].values[0]
    if pd.isna(description):
        description = '无描述'
    view = image_path.split('\\')[-1].split('_')[1].split('.')[0]
    image_save_path = image_save_root + str(new_id) + '_' + view + '_' + description + '.png'
    shutil.copy(image_path, image_save_path)
    if os.path.exists(label_path):
        label_save_path = label_save_root + str(new_id) + '_' + view + '_' + description + '.txt'
        shutil.copy(label_path, label_save_path)
