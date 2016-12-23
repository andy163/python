#!user/bin/python#
# -*- coding: utf-8 -*-
import requests
response = requests.urlopen('https://www.python.org')
print(response.read().decode('utf-8'))