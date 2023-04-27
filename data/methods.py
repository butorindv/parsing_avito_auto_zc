import sys
import time
import traceback
import lxml
from bs4 import BeautifulSoup
from grab import Grab


def grab_to_file(url, headers, file_record):
    range_for = range(0, 10)
    for i in range_for:
        try:
            g = Grab(log_file=file_record)
            g.setup(headers=headers)
            g.go(url)
            break
        except Exception as error:
            print("Возникла ошибка в методе connect_grab_url(): \"{}\"".format(error))
            print(f'URL = {url}')
            if i >= len(range_for) - 1:
                exit(-1)
            time.sleep(2)
            continue
