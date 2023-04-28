import os
from data.methods import *
import data.headers

# os.remove('report/temp_file.html')

url = 'https://avito.ru/'
headers = data.headers.headers
file_record = 'test_record_file.html'
grab_to_file(url, headers, file_record)
