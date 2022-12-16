from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import requests
import secrets
from config import *

app = Flask(__name__)
key = secrets.token_urlsafe(16)
key = secrets.token_hex(16)

app.config['SECRET_KEY'] = 'key'
app.config['MYSQL_HOST'] = host 
app.config['MYSQL_USER'] = sql_user
app.config['MYSQL_PASSWORD'] = sql_password
app.config['MYSQL_DB'] = 'o1gbu42_StatTracker'
API = api_key

mysql = MySQL(app)

@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute('SELECT * FROM Account WHERE AccountName = % s AND Password = % s', (username, password, ))
        
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['AccountName'] = account['AccountName']
            msg = 'Logged in successfully !'
            return render_template('index.html', msg = msg)
        else:
            msg = 'Incorrect username / password !'
        
    return render_template('Login.html', msg = msg)

@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password'  in request.form:
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
   
        
        cursor.execute('SELECT * FROM Account WHERE AccountName = % s', (username,))

        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password:
            msg = 'Please fill out the form !'
        else:
            cursor.execute("INSERT INTO `Account`(`AccountName`, `Password`) VALUES (%s , %s)", (username, password,))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    return render_template('signup.html', msg = msg)


@app.route('/summoner',methods=['GET','POST'])
def getSummoner():
    summonerName = request.args.get('summoner')
    Region = request.args.get('region')

    SummonerInfo = requests.get("https://" + Region + ".api.riotgames.com/lol/summoner/v4/summoners/by-name/" + summonerName + "?api_key=" + API)
    SummonerInfo = SummonerInfo.json()

    RankedMatches = requests.get("https://" + Region + ".api.riotgames.com/lol/league/v4/entries/by-summoner/" + SummonerInfo['id'] + "?api_key=" + API)
    Ranked = RankedMatches.json()

    FLEX = Ranked[0]
    SOLO = Ranked[1]

    getImageLink(SummonerInfo)
    RankedImages(FLEX)
    RankedImages(SOLO)
    masteryScore = requests.get("https://" + Region + ".api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/" + SummonerInfo['id'] + "?api_key=" + API)
    masteryScore = masteryScore.json()
    getChampImages(masteryScore)
    return render_template('summonerPage.html', SummonerInfo = SummonerInfo,soloRanked = SOLO,flexRanked = FLEX,masteryScore = masteryScore)

#Gets Profile Image
def getImageLink(SummonerInfo):
    profileIcon = str(SummonerInfo['profileIconId'])
    SummonerInfo['profileIconId'] = 'http://ddragon.leagueoflegends.com/cdn/12.6.1/img/profileicon/' + profileIcon +'.png'
   
#Gets ChampionImage URLS into masteryScore JSON file
def getChampImages(masteryScore):
    DDRAGON = requests.get("http://ddragon.leagueoflegends.com/cdn/12.6.1/data/en_US/champion.json")
    DDRAGON = DDRAGON.json()
    DDRAGON = DDRAGON['data']
    for item in DDRAGON:
        temp = DDRAGON.get(item)
        for mastery in masteryScore:
            if int(temp['key']) == int(mastery['championId']):
                mastery['link'] = "https://ddragon.leagueoflegends.com/cdn/12.6.1/img/champion/" + temp['id'] +".png"
            
def RankedImages(RankedMode):
    RankedMode['ImageUrl'] = "https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-shared-components/global/default/" + RankedMode['tier'].lower() + ".png"
    

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(ssl_context='adhoc')