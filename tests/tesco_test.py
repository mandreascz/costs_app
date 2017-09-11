import pytest
import app
import os


@pytest.mark.parametrize('image_name,expected_total',
                         [('1.jpg', 37), ('2.jpg', 41), ('3.jpg', 310)])
def test_tescohandler(image_name, expected_total):
    image_path = os.path.join(os.path.abspath('.'), 'receipts', 'tesco', image_name)
    text = app.ocr.extract_text_from_image(image_path)
    obj = app.ParserFactory.find_receipt_type(text).parse()
    assert abs(obj.total_amount-expected_total)/expected_total*100 <= 5
    assert abs(obj._total_sum_goods-expected_total)/expected_total*100 <= 5