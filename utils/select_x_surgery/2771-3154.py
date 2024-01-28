from glob import glob
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import re
import pydicom
import random
from tqdm import tqdm
import json
import PIL.Image as Image
import shutil
import pandas as pd
import numpy as np

def extract_number(string):
    pattern = r'\d+'  # Matches one or more digits
    match = re.search(pattern, string)
    if match:
        number = match.group()
        return number

def dcm2img(dcm,window_center,window_width):
    pixel_array = dcm.pixel_array
    min_value = window_center - window_width / 2
    max_value = window_center + window_width / 2
    clipped_array = np.clip(pixel_array, min_value, max_value)
    scaled_array = (clipped_array - min_value) / (max_value - min_value) * 255
    scaled_array = scaled_array.astype(np.uint8)
    img = Image.fromarray(scaled_array)
    return img

if __name__ == '__main__':
    subject_paths = glob('/backup/Breast_cancer_Jiadong/surgical_cohort/2771-3154/*')
    save_root = '/backup/Breast_cancer_Jiadong/preprocessing/selected_dicom/'
    subject_paths.sort(key=lambda x: [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', x.split('/')[-1])])
    for subject_path in tqdm(subject_paths):
        flag = 0
        id = subject_path.split('/')[-1]
        id = extract_number(id)
        print(id)
        modalites = glob(os.path.join(subject_path, '*'))
        for modality in modalites:
            modality_path = glob(os.path.join(modality, '*'))
            for path in modality_path:
                if path.split('/')[-1] == '0':
                    continue
                dcm_paths = glob(os.path.join(path, '*.dcm'))
                if len(dcm_paths) > 0:
                    break
            if len(dcm_paths) == 0:
                continue
            random_file = random.choice(dcm_paths)
            dcm = pydicom.read_file(random_file)
            if dcm.Modality == 'MG':
                flag = 1
                MG_path = modality
                break
        if flag == 1:
            print(id, 'with MG', MG_path)
        else:
            print(id, 'without MG')
            continue
        subject_path = MG_path
        dcm_paths = glob(os.path.join(subject_path, '**/*.dcm'), recursive=True)
        dcm_3d_paths = glob(os.path.join(subject_path, '**/73400000/*.dcm'), recursive=True) + glob(
            os.path.join(subject_path, '**/73200000/*.dcm'), recursive=True)
        dcm_paths = [x for x in dcm_paths if x not in dcm_3d_paths]
        view_path = {}
        for dcm_path in dcm_paths:
            dcm = pydicom.dcmread(dcm_path, force=True)
            if (0x0008, 0x0068) in dcm:
                presentation = dcm[(0x0008, 0x0068)].value
            if (0x0045, 0x101b) in dcm:
                view = dcm[(0x0045, 0x101b)].value
            if (0x0008, 0x103e) in dcm:
                view = dcm[(0x0008, 0x103e)].value

            views = ['R CC', 'L CC', 'R MLO', 'L MLO', 'RCC', 'LCC', 'RMLO', 'LMLO',
                     'L CC Tomosynthesis Projection', 'R CC Tomosynthesis Projection',
                     'L MLO Tomosynthesis Projection', 'R MLO Tomosynthesis Projection',
                     'R CC C-View', 'L CC C-View', 'R MLO C-View', 'L MLO C-View']
            if view in views and presentation == 'FOR PRESENTATION':
                view_path[view] = dcm_path

        for view in ['L CC', 'L CC C-View', 'LCC', 'L CC Tomosynthesis Projection']:
            if view in view_path:
                os.makedirs(os.path.join(save_root, id), exist_ok=True)
                shutil.copy(view_path[view], os.path.join(save_root, id, 'L CC.dcm'))
                break
        for view in ['R CC', 'R CC C-View', 'RCC', 'R CC Tomosynthesis Projection']:
            if view in view_path:
                os.makedirs(os.path.join(save_root, id), exist_ok=True)
                shutil.copy(view_path[view], os.path.join(save_root, id, 'R CC.dcm'))
                break
        for view in ['L MLO', 'L MLO C-View', 'LMLO', 'L MLO Tomosynthesis Projection']:
            if view in view_path:
                os.makedirs(os.path.join(save_root, id), exist_ok=True)
                shutil.copy(view_path[view], os.path.join(save_root, id, 'L MLO.dcm'))
                break
        for view in ['R MLO', 'R MLO C-View', 'RMLO', 'R MLO Tomosynthesis Projection']:
            if view in view_path:
                os.makedirs(os.path.join(save_root, id), exist_ok=True)
                shutil.copy(view_path[view], os.path.join(save_root, id, 'R MLO.dcm'))
                break