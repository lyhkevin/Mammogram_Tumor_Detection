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

def extract_number(string):
    pattern = r'\d+'  # Matches one or more digits
    match = re.search(pattern, string)
    if match:
        number = match.group()
        return number

if __name__ == '__main__':
    subject_paths = glob('/backup/Breast_cancer_Jiadong/surgical_cohort/X_1-2770/X-BREAST SURGERY 1-738/X-2D/*') + glob('/backup/Breast_cancer_Jiadong/surgical_cohort/X_1-2770/X-BREAST SURGERY 1-738/X-3D/*')
    print(len(subject_paths))
    save_root = '/backup/Breast_cancer_Jiadong/preprocessing/selected_dicom/'
    subject_paths.sort(key=lambda x: [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', x.split('\\')[-1])])
    for subject_path in tqdm(subject_paths):
        id = subject_path.split('/')[-1]
        id = extract_number(id)
        dcm_paths = glob(os.path.join(subject_path, '**/*.dcm'), recursive=True)
        dcm_3d_paths = glob(os.path.join(subject_path, '**/73400000/*.dcm'), recursive=True)
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