from pytesseract import pytesseract, image_to_string
import PIL.ImageFilter
from PIL import Image
import numpy as np
import cv2

from . import TESSERACT_PATH

pytesseract.tesseract_cmd = TESSERACT_PATH


def rotate_image(path):
    image = cv2.imread(path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(thresh > 0))
    angle = cv2.minAreaRect(coords)[-1]
    angle = -(90 + angle) if angle < -45 else -angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return Image.fromarray(rotated)


def extract_text_from_image(image_path):
    im = rotate_image(image_path)
    arr = np.array(im.convert('L'))

    arr = cv2.erode(arr, np.ones((3, 3)), iterations=2)
    arr = cv2.dilate(arr, np.ones((3, 3)), iterations=1)

    # cond = arr > 100
    # arr[cond] = 255
    # arr[~cond] = 0

    h, w = arr.shape
    ratio = 1.25
    arr = cv2.resize(arr, (int(w*ratio), int(h*ratio)))

    im=Image.fromarray(arr)
    res = image_to_string(im, lang='ces')
    return res
