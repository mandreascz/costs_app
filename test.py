import app
import logging
import os

logging.basicConfig(level=logging.ERROR)

if __name__ == '__main__':
    images = os.listdir(os.path.join(os.path.abspath('.'), 'receipts', 'tesco'))
    df = None
    total = []
    for im in images:
        text = app.ocr.extract_text_from_image(os.path.join(os.path.abspath('.'), 'receipts', 'tesco', im))
        obj = app.ParserFactory.find_receipt_type(text)
        try:
            d = obj.parse()
            if df is None:
                df = d['data']
            else:
                df = df.append(d['data'])
            total.append(d['total'])
        except Exception as e:
            print(e)
    print(df)
    print(total)

