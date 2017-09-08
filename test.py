import app
import logging
logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    im_path = '/home/andrej/REPOS/costs_app/receipts/11.jpg'
    text = app.ocr.extract_text_from_image(im_path)
    obj = app.ParserFactory.find_receipt_type(text)
    obj.get_goods_text()
    obj.parse_goods()