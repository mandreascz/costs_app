import app
import logging
import os
logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    im_path = os.path.join(os.path.abspath('.'), 'receipts', 'tesco', '13.jpg')
    text = app.ocr.extract_text_from_image(im_path)
    obj = app.ParserFactory.find_receipt_type(text)
    obj.parse()