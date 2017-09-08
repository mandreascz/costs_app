from fuzzywuzzy import fuzz
import numpy as np
import re
from . import logger



class BaseParser:
    shop_identifiers = []

    def __init__(self, recognized_text):
        self.list_text = [{'line': line, 'parsed': False, 'to_delete': False}
                          for line in recognized_text.splitlines() if line]
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
    simple_goods_pattern = re.compile('^([^\d].*)\s(\d{1,4})\s*,*[\s\d\w%]*$', flags=re.M)
    amount_goods_pattern = re.compile('^(.*)\n([\w,\s]+)[\*©].*\s(\d{1,3}\s*[.,]\s*\d{2,3})[BR8\s]*$', flags=re.M)

    def get_goods_text(self):
        goods_start = ['K.c.', 'Kč', 'Kc', 'K <:', 'lži']
        goods_end = ['CELKEM']
        text_to_remove = ['Z 1. F V N F N 0']
        start_list = []
        end_list = []
        for line in self.list_text:
            if max(map(lambda x: fuzz.token_set_ratio(line['line'], x), text_to_remove)) > 80:
                logger.debug(max(map(lambda x: fuzz.token_set_ratio(line['line'], x), text_to_remove)))
                line['to_delete'] = True
                start_list.append(0)
                end_list.append(0)
                continue
            start_list.append(max(map(lambda x: fuzz.token_set_ratio(line['line'], x), goods_start)))
            end_list.append(max(map(lambda x: fuzz.token_set_ratio(line['line'], x), goods_end)))
        start = np.argmax(start_list)
        end = np.argmax(end_list)
        self.goods_text = self.list_text[start + 1:end]
        self.goods_text = list(filter(lambda x: not x['to_delete'], self.goods_text))
        logger.debug(self.goods_text)

    def parse_goods(self):
        for line in self.goods_text:
            match = re.match(self.simple_goods_pattern, line['line'])
            if match is not None:
                item, price = match.groups()
                line['parsed'] = True
                logger.debug((item, price))

        # Second pass for the two-row goods
        two_rows_goods = list(filter(lambda x: not x['parsed'], self.goods_text))
        for idx, line in enumerate(two_rows_goods):
            if idx >= len(two_rows_goods) - 1:
                break
            match = re.match(self.amount_goods_pattern, "{}\n{}".format(line['line'], two_rows_goods[idx+1]['line']))
            if match is not None:
                item, amount, price = match.groups()
                line['parsed'] = True
                logger.debug((item, amount, price))









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



