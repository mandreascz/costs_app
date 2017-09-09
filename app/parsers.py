from fuzzywuzzy import fuzz
import numpy as np
import re
import pandas as pd
from . import logger


class BaseParser:
    shop_identifiers = []

    def __init__(self, recognized_text):
        self.list_text = [{'line': line, 'parsed': False, 'to_delete': False}
                          for line in recognized_text.splitlines() if line]
        self.goods_text = None
        self.good_df = None
        self.date = None
        self.total_amount = None

    def parse(self):
        pass

    def get_goods_text(self):
        pass

    def parse_goods(self):
        pass

    def get_date(self):
        pass

    def get_total_amount(self):
        pass

    @property
    def not_parsed(self):
        return [x['line'] for x in self.goods_text if not x['parsed']]

    @staticmethod
    def get_numbers(s):
        return float(s.replace(" ", "").replace(',', '.'))


class TescoParser(BaseParser):
    shop_identifiers = ['TESCO STORES', 'CLUBCARD']
    total_amount_pattern = re.compile('(\d{1,4}\s?[,.]\s?\d{2})')
    simple_goods_pattern = re.compile('^(\D[\w\sÀ-ÿ.,/%"—]*[^,])\s(\d{1,4}\s?[.,]?\d{0,2})[\s\w%]*$', flags=re.M | re.I)
    two_line_goods_pattern = re.compile('^(.*)\n([\w,\s]+)[\*©r].*\s(\d{1,3}\s*[.,]\s*\d{2,3})[BR8\s]$', flags=re.M)

    def parse(self):
        self.get_goods_text()
        self.get_total_amount()
        self.parse_goods()
        for l in self.not_parsed:
            print(l)

    def get_goods_text(self):
        goods_start = ['K.c.', 'Kč', 'Kc', 'K <:', 'lži', '!(Cš']
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
        self.goods_text = self.list_text[start + 1:end + 1]
        self.goods_text = list(filter(lambda x: not x['to_delete'], self.goods_text))
        logger.debug(self.goods_text)

    def parse_goods(self):
        goods_list = []

        # First pass for the two-row goods
        for idx, line in enumerate(self.goods_text):
            if idx >= len(self.goods_text) - 1:
                break
            if line['parsed'] or self.goods_text[idx + 1]['parsed']:
                continue
            match = re.match(self.two_line_goods_pattern, "{}\n{}".format(line['line'], self.goods_text[idx + 1]['line']))
            if match is not None:
                item, amount, price = match.groups()
                line['parsed'] = True
                self.goods_text[idx + 1]['parsed'] = True
                goods_list.append({'Item': item, 'Amount': amount, 'Price': self.get_numbers(price)})

        for line in self.goods_text:
            if line['parsed']:
                continue
            match = re.match(self.simple_goods_pattern, line['line'])
            if match is not None:
                item, price = match.groups()
                line['parsed'] = True
                goods_list.append({'Item': item, 'Amount': None, 'Price': self.get_numbers(price)})
        df = pd.DataFrame(goods_list)
        logger.debug("Goods generated %s", df)

    def get_total_amount(self):
        match = re.search(self.total_amount_pattern, self.goods_text[-1]['line'])
        if match:
            total_amount = match.group()
            self.total_amount = self.get_numbers(total_amount)
        self.goods_text.pop()


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



