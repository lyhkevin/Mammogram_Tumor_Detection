import argparse
import os
import sys
from pathlib import Path
import albumentations
import cv2
import torch
import numpy as np
import torch.backends.cudnn as cudnn
from yolo.utils.augmentations import letterbox
from yolo.models.common import DetectMultiBackend
from yolo.utils.general import (non_max_suppression, print_args)
from yolo.utils.plots import Annotator, colors, save_one_box

def Get_Model(weights='./runs/train/exp/weights/best.pt', dnn=False):
    model = DetectMultiBackend(weights, device=torch.device('cuda:0'), dnn=dnn)
    return model

def save_yolo_coordinates(x0, y0, x1, y1, image_width, image_height, output_file):
    # Calculate the center coordinates and dimensions of the detection box
    x_center = (x0 + x1) / (2 * image_width)
    y_center = (y0 + y1) / (2 * image_height)
    box_width = (x1 - x0) / image_width
    box_height = (y1 - y0) / image_height
    with open(output_file, 'w') as f:
        f.write(f'0 {x_center} {y_center} {box_width} {box_height}')

def resize_image(img_arr, bboxes, h, w):
    """
    :param img_arr: original image as a numpy array
    :param bboxes: bboxes as numpy array where each row is 'x_min', 'y_min', 'x_max', 'y_max', "class_id"
    :param h: resized height dimension of image
    :param w: resized weight dimension of image
    :return: dictionary containing {image:transformed, bboxes:['x_min', 'y_min', 'x_max', 'y_max', "class_id"]}
    """
    # create resize transform pipeline
    transform = albumentations.Compose(
        [albumentations.Resize(height=h, width=w, always_apply=True)],
        bbox_params=albumentations.BboxParams(format='pascal_voc'))
    transformed = transform(image=img_arr, bboxes=bboxes)
    return transformed

def adjust_coordinate(x0, y0, x1, y1, x, y):
    if x0 < 0:
        x0 = 0
    if y0 < 0:
        y0 = 0
    if x1 > x:
        x1 = x
    if y1 > y:
        y1 = y
    return x0, y0, x1, y1

def Inference_crop_breast(model, orginal_img, img, img_np, save_path, conf_thres = 0.2, iou_thres = 0.1, classes=None, agnostic_nms = False, max_det = 2):
    with torch.no_grad():
        pred = model(img, augment=False, visualize=False)
        pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)
        x_original, y_original = orginal_img.shape[1], orginal_img.shape[0]
        x_resized, y_resized = img_np.shape[0], img_np.shape[1]
        img_crop = orginal_img.copy()
        for i, det in enumerate(pred):
            for *xyxy, conf, cls in reversed(det):
                x0, y0, x1, y1 = xyxy[0].item(), xyxy[1].item(), xyxy[2].item(), xyxy[3].item()
                x0, y0, x1, y1 = adjust_coordinate(x0, y0, x1, y1, y_resized, x_resized)
                image = resize_image(img_np, [[x0, y0, x1, y1, 0]], y_original, x_original)
                x0, y0, x1, y1 = image['bboxes'][0][0], image['bboxes'][0][1], image['bboxes'][0][2], image['bboxes'][0][3]
                if abs(x0) < abs(x_original - x1):
                    x0 = 0
                else:
                    x1 = x_original
                x0, y0, x1, y1 = int(x0),int(y0),int(x1),int(y1)
                cv2.rectangle(orginal_img, (x0, y0), (x1, y1), (0, 0, 255), 30)
                cv2.imwrite(save_path + 'detect_box.png', orginal_img)
                img_crop = img_crop[y0:y1, x0:x1]
                cv2.imwrite(save_path + 'cropped_breast.png', img_crop)

def Inference_crop_tumor(model, orginal_img, img, img_np, save_path, conf_thres = 0.2, iou_thres = 0, classes=None, agnostic_nms = False, max_det = 2):
    with torch.no_grad():
        pred = model(img, augment=False, visualize=False)
        pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)
        x_original, y_original = orginal_img.shape[1], orginal_img.shape[0]
        x_resized, y_resized = img_np.shape[0], img_np.shape[1]
        img_crop = orginal_img.copy()
        for i, det in enumerate(pred):
            for *xyxy, conf, cls in reversed(det):
                x0, y0, x1, y1 = xyxy[0].item(), xyxy[1].item(), xyxy[2].item(), xyxy[3].item()
                x0, y0, x1, y1 = adjust_coordinate(x0, y0, x1, y1, y_resized, x_resized)
                image = resize_image(img_np, [[x0, y0, x1, y1, 0]], y_original, x_original)
                x0, y0, x1, y1 = image['bboxes'][0][0], image['bboxes'][0][1], image['bboxes'][0][2], image['bboxes'][0][3]
                x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
                cv2.rectangle(orginal_img, (x0, y0), (x1, y1), (0, 0, 255), 30)
                cv2.imwrite(save_path + 'detect_tumor.png', orginal_img)
                img_crop = img_crop[y0:y1, x0:x1]
                save_yolo_coordinates(x0, y0, x1, y1, x_original, y_original, save_path + 'tumor.txt')
                cv2.imwrite(save_path + 'tumor.png', img_crop)