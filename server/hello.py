from flask import Flask, request, render_template
import requests
from flask_mysqldb import MySQL
import mysql.connector

app = Flask(__name__)

app.config['MYSQL_HOST'] = '109.73.175.66'
app.config['MYSQL_USER'] = 'o1gbu42_StatTracker'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'o1gbu42_StatTracker'
API = ''

mysql = MySQL(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('Login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    if request.method == 'GET':
        return "Login via the login Form"
     
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute(''' INSERT INTO info_table VALUES(%s,%s)''',(name,password))
        mysql.connection.commit()
        cursor.close()
        return f"Done!!"

@app.route('/summoner',methods=['GET'])
def getSummoner():
    summonerName = request.args.get('summoner')
    Region = "euw1"
    print(summonerName)
    SummonerInfo = requests.get("https://" + Region + ".api.riotgames.com/lol/summoner/v4/summoners/by-name/" + summonerName + "?api_key=" + API)
    SummonerInfo = SummonerInfo.json()
    id = SummonerInfo['id'] 
    SummonerInfo['profileIconId'] = getImageLink(SummonerInfo['profileIconId'])
    RankedMatches = requests.get("https://" + Region + ".api.riotgames.com/lol/league/v4/entries/by-summoner/" + id + "?api_key=" + API)
    print("https://" + Region + ".api.riotgames.com/lol/league/v4/entries/by-summoner/" + id + "?api_key=" + API)
    Ranked = RankedMatches.json()
    FLEX = Ranked[0]
    SOLO = Ranked[1]

    masteryScore = requests.get("https://" + Region + ".api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/" + id + "?api_key=" + API)
    masteryScore = masteryScore.json()
    getChampImages(masteryScore)
    return render_template('summonerPage.html', SummonerInfo = SummonerInfo,soloRanked = SOLO,flexRanked = FLEX,masteryScore = masteryScore)

def getImageLink(profileIcon):
    profileIcon = str(profileIcon)
    link = 'http://ddragon.leagueoflegends.com/cdn/12.6.1/img/profileicon/' + profileIcon +'.png'
    return link

def getChampImages(masteryScore):
    DDRAGON = requests.get("http://ddragon.leagueoflegends.com/cdn/9.18.1/data/en_US/champion.json")
    DDRAGON = DDRAGON.json()
    DDRAGON = DDRAGON['data']
    for item in DDRAGON:
        temp = DDRAGON.get(item)
        for mastery in masteryScore:
            if int(temp['key']) == int(mastery['championId']):
                mastery['link'] = "https://ddragon.leagueoflegends.com/cdn/12.6.1/img/champion/" + temp['id'] +".png"
            


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(ssl_context='adhoc')