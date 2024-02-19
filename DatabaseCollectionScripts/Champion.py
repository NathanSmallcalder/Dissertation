import sys
import os
import requests
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now you should be able to import the config module
from config import *
from RiotApiCalls import *

import mysql.connector

conn = mysql.connector.connect(user=sql_user, password=sql_password, host=host, database='o1gbu42_StatTracker')
cursor = conn.cursor()
DDRAGON = requests.get("http://ddragon.leagueoflegends.com/cdn/14.3.1/data/en_US/champion.json")
DDRAGON = DDRAGON.json()
DDRAGON = DDRAGON['data']
for item in DDRAGON:
    temp = DDRAGON.get(item)
    itemID = temp['key']
    champName = temp['name']
    try:
        cursor.execute("INSERT INTO `ChampionTbl`(`ChampionId`, `ChampionName`) VALUES (%s, %s)", (itemID, champName,))
        conn.commit()
    except mysql.connector.IntegrityError as e:
        if e.errno == 1062:  # Error number for duplicate entry
            print(f"Skipping duplicate entry for ChampionID {itemID}")
            conn.rollback()  # Rollback the transaction to continue with the next iteration

