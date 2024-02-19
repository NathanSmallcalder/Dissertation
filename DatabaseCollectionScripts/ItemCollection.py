import sys
import requests
import mysql.connector
import os

# Append parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import configuration variables and Riot API functions
from config import *

# Establish a connection to the MySQL database
conn = mysql.connector.connect(user=sql_user, password=sql_password, host=host, database='o1gbu42_StatTracker')
cursor = conn.cursor()

try:
    # Fetch item data from Riot API (Data Dragon)
    DDRAGON_ITEMS = requests.get("http://ddragon.leagueoflegends.com/cdn/14.3.1/data/en_US/item.json")
    DDRAGON_ITEMS = DDRAGON_ITEMS.json()
    DDRAGON_ITEMS = DDRAGON_ITEMS['data']

    for item_key, item_data in DDRAGON_ITEMS.items():
        item_name = "https://ddragon.leagueoflegends.com/cdn/14.3.1/img/item/" + item_data['image']['full']
        item_id = int(item_key)
        try:
            cursor.execute("INSERT INTO `ItemTbl`(`ItemID`, `ItemLink`) VALUES (%s, %s)", (item_id, item_name,))
            conn.commit()
        except mysql.connector.IntegrityError as e:
            if e.errno == 1062:  # Error number for duplicate entry
                print(f"Skipping duplicate entry for ItemID {item_id}")
                conn.rollback()  # Rollback the transaction to continue with the next iteration

except Exception as ex:
    print(f"An error occurred: {ex}")

finally:
    # Close the cursor and database connection
    cursor.close()
    conn.close()