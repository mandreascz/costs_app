from fuzzywuzzy import fuzz
import numpy as np
import re
from . import logger



class BaseParser:
    shop_identifiers = []

    def __init__(self, recognized_text):
        self.list_text = [{'line': line, 'parsed': False} for line in recognized_text.splitlines()]
        self.goods_text = None
        self.goods_df = None

    def get_goods_text(self):
        pass

    def parse_goods(self):
        pass

    def get_date(self):
        pass

    def get_total_amount(self):
        pass

    def return_not_parsed(self):
        pass


class TescoParser(BaseParser):
    shop_identifiers = ['TESCO STORES', 'CLUBCARD']
    simple_goods_pattern = re.compile('^([^\d].*)\s(\d{1,4})\s*,[\s\d\w%]*$', flags=re.M)

    def get_goods_text(self):
        goods_start = ['K. c.']
        goods_end = ['CELKEM']
        start_list = []
        end_list = []
        for line in self.list_text:
            start_list.append(fuzz.token_set_ratio(line['line'], goods_start))
            end_list.append(fuzz.token_set_ratio(line['line'], goods_end))
        start = np.argmax(start_list)
        end = np.argmax(end_list)
        self.goods_text = self.list_text[start + 1:end - 1]

    def parse_goods(self):
        for line in self.goods_text:
            match = re.match(self.simple_goods_pattern, line['line'])
            if match is not None:
                item, price = match.groups()
                line['parsed'] = True








class AlbertParser(BaseParser):
    shop_identifiers = ['AHOLD', 'ALBERT']


class LidlParser(BaseParser):
    shop_identifiers = ['LIDL']


class ParserFactory:
    parsers = [TescoParser, AlbertParser, LidlParser]

    @staticmethod
    def find_receipt_type(text):
        score = []
        for parser in ParserFactory.parsers:
            parser_score = []
            for identifier in parser.shop_identifiers:
                parser_score.append(fuzz.token_set_ratio(text, identifier))
            score.append((parser, max(parser_score)))
        logger.debug(score)

        best_matching = max(score, key=lambda x: x[1])
        return best_matching[0](text)



