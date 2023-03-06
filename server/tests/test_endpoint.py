import sys
import pytest
import requests

sys.path.append('..')
from config import *
from RiotApiCalls import *

api_key= api_key
db = pymysql.connect(host=host,user='o1gbu42_StatTracker',passwd=sql_password,database =sql_user)
cursor = db.cursor()

