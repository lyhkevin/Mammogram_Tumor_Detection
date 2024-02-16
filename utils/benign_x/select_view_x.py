import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import re
import pydicom
import random
from tqdm import tqdm
import PIL.Image as Image
import shutil
import pandas as pd
from glob import glob
import re
import json

def get_number(folder_path):
    longest_number = ''
    numbers = re.findall(r'\d+', folder_path)
    for number in numbers:
        if len(number) > len(longest_number):
            longest_number = number
    return longest_number

if __name__ == '__main__':
    path_1 = '/public/home/liyh2022/projects/breast_data_preprocessing/benign/raw/benign_1489/MG/*'
    path_2 = '/public/home/liyh2022/projects/breast_data_preprocessing/benign/raw/inflammation_405/MG/*'
    subject_paths = glob(path_1) + glob(path_2)
    save_root = '/public/home/liyh2022/projects/breast_data_preprocessing/benign/processed/MG/select_view/'
    os.makedirs(save_root, exist_ok=True)
    subject_paths.sort(key=lambda x: [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', x.split('\\')[-1])])
    for subject_path in tqdm(subject_paths):
        id = get_number(subject_path)
        if not os.path.exists(save_root + id):
            print(id)
            dcm_paths = glob(os.path.join(subject_path, '*/*.dcm'), recursive=False)
            view_path = {}
            for dcm_path in dcm_paths:
                dcm = pydicom.dcmread(dcm_path, force=True)
                presentation, series_description, clinical_view = None, None, None
                if (0x0008, 0x0068) in dcm:
                    presentation = dcm[(0x0008, 0x0068)].value
                if (0x0008, 0x103e) in dcm:
                    series_description = dcm[(0x0008, 0x103e)].value
                if (0x0045, 0x101b) in dcm:
                    clinical_view = dcm[(0x0045, 0x101b)].value
                    
                if clinical_view is not None:
                    view = clinical_view
                else:
                    view = series_description
                    
                views = ['R CC', 'L CC', 'R MLO', 'L MLO', 'RCC', 'LCC', 'RMLO', 'LMLO',
                        'L CC Tomosynthesis Projection', 'R CC Tomosynthesis Projection',
                        'L MLO Tomosynthesis Projection', 'R MLO Tomosynthesis Projection',
                        'R CC C-View', 'L CC C-View', 'R MLO C-View', 'L MLO C-View']
                if view in views and presentation == 'FOR PRESENTATION':
                    view_path[view] = dcm_path
            print(view_path)
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