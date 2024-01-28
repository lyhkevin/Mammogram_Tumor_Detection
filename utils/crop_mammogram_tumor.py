import pydicom
from PIL import Image
from glob import glob
from yolo.inference import *

def dcm_to_png(dcm_path):
    dcm = pydicom.dcmread(dcm_path,force=True)
    if 'PixelData' in dcm:
        if hasattr(dcm, 'WindowCenter'):
            if type(dcm.WindowCenter) == pydicom.multival.MultiValue:
                img = histogramTransfer(dcm)
            else:
                img = (dcm.pixel_array / dcm.pixel_array.max() * 255).astype('uint8')
            img = Image.fromarray(img)
        return img
    else:
        print('dcm_path, do not have pixel data')
        return None

def histogramTransfer(dcm):
    data = np.array(dcm.pixel_array, dtype=np.int16)
    bin_size = 10
    hist_range = data.max() - data.min()
    hist, bin_edges = np.histogram(data.astype(np.uint), bins=int(hist_range / bin_size))
    hist_diff = np.diff(hist)
    start_i = int(500 / bin_size)
    hist_min = int(hist[start_i])
    hist_max = int(hist[-1])
    footlength = int(hist_range / 5)
    for i in range(start_i, len(hist) - int(footlength / bin_size)):
        if hist[i] > 50 * bin_size and np.median(
                hist[i:i + int(footlength / bin_size)]) > 100 * bin_size and np.median(
            hist_diff[i - 1:i + 1]) > 10:
            hist_min = int(bin_edges[i])
            break
        footlength = int(hist_range / 10)
        for i in range(len(hist) - 1, start_i + int(footlength / bin_size), -1):
            if np.median(hist[i - int(footlength / bin_size):i]) > 30 * bin_size and hist_diff[i - 1] < 0:
                hist_max = int(bin_edges[i])
                break
    # normalize the image
    data_png = (data - hist_min) / (hist_max - hist_min) * 255
    data_png[data_png < 0] = 0
    data_png[data_png > 255] = 255
    return data_png

if __name__ == '__main__':
    dcm_paths = glob('./dataset/Surgical/*/*.dcm', recursive=True)
    base_save_path = './dataset/cropped_Surgical/'
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    crop_breast_model = Get_Model('./yolo/yolo_weight/crop_breast.pt').to(device)
    crop_tumor_model = Get_Model('./yolo/yolo_weight/crop_tumor.pt').to(device)
    for dcm_path in dcm_paths:
        id = dcm_path.split('/')[-2]
        print(id)
        file_name = os.path.basename(dcm_path)
        file_name = file_name.split('.')[0]
        img = dcm_to_png(dcm_path)
        if img == None:
            print(file_name, 'is not a valid dcm file')
            continue
        img = img.convert('RGB')
        save_path = base_save_path + id + '/' + file_name + '/'
        os.makedirs(save_path, exist_ok=True)
        img.save(save_path + 'original.png')
        #crop breast
        input_original = cv2.imread(save_path + 'original.png')
        input_np = cv2.resize(input_original, (640, 640))
        input_np = np.array(input_np)
        input = input_np.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
        input = np.ascontiguousarray(input)
        input = torch.from_numpy(input).unsqueeze(0).to(device)
        input = input.float()
        input /= 255
        Inference_crop_breast(model = crop_breast_model, orginal_img = input_original, img = input, img_np = input_np, conf_thres = 0.01, save_path = save_path, max_det = 1)

        # # # crop tumor
        input_original = cv2.imread(save_path + '/cropped_breast.png')
        input_np, _, wh = letterbox(input_original, 640, stride=32, auto=True)
        input = input_np.transpose((2, 0, 1))[::-1]
        input = np.ascontiguousarray(input)
        input = torch.from_numpy(input).unsqueeze(0).to(device)
        input = input.float()
        input /= 255
        Inference_crop_tumor(model = crop_tumor_model, orginal_img = input_original, img = input, img_np = input_np, conf_thres = 0.1, save_path = save_path, max_det = 1)
