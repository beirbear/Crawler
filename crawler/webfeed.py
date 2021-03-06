import urllib3
import time
import random
import os
from bs4 import BeautifulSoup

class Settrade(object):

    def __init__(self):
        self.__symbols = None
        self.__holidays = None
        self.__domain = 'http://www.settrade.com'
        self.__storage = '/home/beir_bear/storage/settrade/' + self.__get_today_date()

    def __get_address(self, symbol):
        return 'http://www.settrade.com/C04_01_stock_quote_p1.jsp?txtSymbol={0}&ssoPageId=9&selectPage='.format(symbol)

    def __get_file_name(self, symbol):
        return symbol + '.html'

    def __get_consensus_string(self):
        return 'IAA Consensus'

    def __get_today_date(self):
        return time.strftime("%Y-%m-%d")

    def __download(self, url, trial=0):
        http = urllib3.PoolManager()
        r = http.request('GET', url)

        if r.status == 200:
            return r.data.decode('tis-620', 'ignore')

        else:
            if trial < 5:
                time.sleep(random.random() * 10)
                return self.__download(url, trial + 1)
            else:
                return None

    def __dump_content(self, content, file_name):
        if not os.path.isdir(self.__storage):
            os.mkdir(self.__storage)

        with open(self.__storage + '/' + file_name, 'wt') as t:
            t.write(content)

    def __is_today_holiday(self):
        with open('crawler/configuration/holidays.txt', 'rt') as t:
            tmp = t.readlines()

            if time.strftime("%Y%m%d") in tmp:
                return True

            return False

    def download_all(self):

        # Check for week day
        import datetime
        if datetime.datetime.now().isoweekday() not in range(1, 6):
            print("Today is a weekend.")
            exit()

        # Check for holiday
        if self.__is_today_holiday():
            print("Today is a holiday.")
            exit()

        print("Downloading stock symbols")
        self.get_stock_symbol()

        for i, symbol in enumerate(self.__symbols):
            symbol = symbol.strip()
            print("[{1}/{2}]Downloading symbol {0}".format(symbol, i+1, len(self.__symbols)))
            res = self.__download(self.__get_address(symbol))
            if res:
                self.__dump_content(res, self.__get_file_name(symbol))
                if res.find(self.__get_consensus_string()) > 0:
                    # Extract link to consensus
                    soup = BeautifulSoup(res, 'html.parser')
                    tmp = soup.find_all("ul", {"class": "nav nav-tabs nav-tabs-stt nav-tabs-many"})
                    for line in tmp[0].find_all("a"):
                        if line.string == self.__get_consensus_string():
                            consensus = self.__download(self.__domain + line['href'])
                            self.__dump_content(consensus, self.__get_file_name(symbol + '.ccs'))

                # time.sleep(random.random() * 10)

    def get_stock_symbol(self):
        while not self.update_stock_symbols():
            time.sleep(10)

    def update_stock_symbols(self):

        def get_link(symbol):
            return 'http://www.settrade.com/C18_Search_Symbol.jsp?txtBrokerId=IPO&selectPage=1&requestPage=%2FC18_Search_Symbol.jsp%3FtxtBrokerId%3DIPO%26selectPage%3D1&txtAlphabet={0}'.format(symbol)

        symbols_list = []
        for char in ['num', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
            content = self.__download(get_link(char))
            if content:
                res = BeautifulSoup(content, 'html.parser').find_all("table", {"id": "stock-list", "class": "table table-info table-hover"})
                tmp = BeautifulSoup(str(res), 'html.parser').find_all("a", {"class": "colorGreen"})
                for item in tmp:
                    if item['href'].find("txtSymbol=") > 0:
                        symbols_list += [item.text.strip().replace(" ", "").replace("&", "%26").replace(";", "")]

            else:
                print("Cannot update symbol")
                return False

        from random import shuffle
        shuffle(symbols_list)
        self.__symbols = symbols_list
        return True
