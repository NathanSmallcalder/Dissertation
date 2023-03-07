import json
import requests
sys.path.append('..')
from config import *
from RiotApiCalls import *

import mysql.connector

conn = mysql.connector.connect(user=sql_user, password=sql_password, host=host, database='o1gbu42_StatTracker')
cursor = conn.cursor()
DDRAGON = requests.get("http://ddragon.leagueoflegends.com/cdn/12.6.1/data/en_US/champion.json")
DDRAGON = DDRAGON.json()
DDRAGON = DDRAGON['data']
for item in DDRAGON:
    temp = DDRAGON.get(item)
    itemID = temp['key']
    champName = temp['name']
    cursor.execute("INSERT INTO `ChampionTbl`(`ChampionId`, `ChampionName`)  VALUES (%s , %s)", (itemID, champName,))
    conn.commit()

