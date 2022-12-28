from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import requests
import secrets
from config import *
from RiotApiCalls import *
import pandas as pd
import matplotlib.pyplot as plt 
import numpy as np

app = Flask(__name__)
key = secrets.token_urlsafe(16)
key = secrets.token_hex(16)

app.config['SECRET_KEY'] = 'key'
app.config['MYSQL_HOST'] = host 
app.config['MYSQL_USER'] = sql_user
app.config['MYSQL_PASSWORD'] = sql_password
app.config['MYSQL_DB'] = 'o1gbu42_StatTracker'

mysql = MySQL(app)

#Login
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

#Register
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

#Summoner Routing
@app.route('/summoner',methods=['GET','POST'])
def getSummoner():
    summonerName = request.args.get('summoner')
    Region = request.args.get('region')
    SummonerInfo = getSummonerDetails(Region,summonerName)
    RankedDetails = getRankedStats(Region,SummonerInfo['id'])
    FLEX = RankedDetails[0]
    SOLO = RankedDetails[1]
    getImageLink(SummonerInfo)
    RankedImages(FLEX)
    RankedImages(SOLO)
    masteryScore = getMasteryStats(Region,SummonerInfo['id'])

    data = getMatchData(Region, SummonerInfo['id'], SummonerInfo['puuid'])


    print(data[1]['GameDuration'])

    MeanData = getMatchTimeline(Region, SummonerInfo['id'], SummonerInfo['puuid'],data)
    return render_template('summonerPage.html', SummonerInfo = SummonerInfo,
    soloRanked = SOLO,flexRanked = FLEX,masteryScore = masteryScore,data=data, MeanData = MeanData)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(ssl_context='adhoc')