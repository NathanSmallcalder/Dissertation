import requests
from config import api_key
import pandas as pd
import time
from RiotApiCalls import *
API = api_key

class SummonerInGame:
  def __init__(self, SummonerName, Rank, WinRate,AvgGold,AvgDmg,AvgDmgTaken):
    self.SummonerName = SummonerName
    self.Rank = Rank
    self.WinRate = WinRate
    self.AvgGold = AvgGold
    self.AvgDmg = AvgDmg
    self.AvgDmgTaken = AvgDmgTaken

Summoners = []

LiveGame = requests.get("https://euw1.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/RUhQYj8Cq9Ku5VtGIpmI_nve_3rM_Z7S5sk6o02D4pzSfBI?api_key=RGAPI-546ff69b-0cba-44ac-b79d-be1472f09bc1")
LiveGame = LiveGame.json()
LiveGame = LiveGame['participants']

iee = 0
#summonerIds = ['w927rRqvSIdwiS4iv5bY56zeVEn3NXnerUGo0-kYABIOllc', '3UHPhx4eAIoGJCsS0keO2kxL2HXSJQhcShAbtr6cofLONoM', 'gqXDXHImviJYX3oBcG6rj-tZGhHrgVkS3vIXr26u8OrDeUuo', 'AivoJB0ZQhcN5sGvdkmuOzITKKcV_oEQzGuLrTvBCmAGJ0k', '45I3QWkUQ5KRVDFaQ7vKtbwKCgHTLVfGe7O-N81g82oppWzhfLBzyoRtwA', '-OkH0i45xv6kyCde4xHCHBzlRHQwaXJ0dAhYBMjKETQZBLgo', 'QonyulL8sEsR1SOI4WnXo1Zm10syKeMT6UQXBQLEJiCNMauTTkxDY4pDpw', 'Lojb4vx9QJuC1AVrYkkPNgG_MBgv7OrxUbqvjDeusgrfgWw', 'rKffW9fiYiO30Y0-1_E__gDyUnjP8iA6lILHqioxCSDFEBtZ', 'G3DXKkdLb1IrQlF53kpFZmFCGvnXffdC4ksjlTCto510pgNE']
summonerIds = []
while iee < 10:
    summonerIds.append(LiveGame[iee]['summonerId'])
    iee = iee +1
print(summonerIds)
Region = "euw1"

for summonerId in summonerIds:
    puuid = requests.get("https://euw1.api.riotgames.com/lol/summoner/v4/summoners/" +summonerId + "?api_key=RGAPI-546ff69b-0cba-44ac-b79d-be1472f09bc1")
    puuid = puuid.json()
    name = puuid['name']
    puuid = puuid['puuid']
    print(name)
    print(puuid)

    Rank = "Unranked"
    MatchIDs = getMatchIds(Region,puuid)

    time.sleep(5)
    ##GetMatch
    Last5Games = getMatches(Region, MatchIDs, puuid)
    MeanData = getMatchTimeline(Region, summonerId, puuid, Last5Games)
    champion = []
    WinRate = 0
    for rows in Last5Games:
      if rows['win'] == True:
        WinRate = WinRate + 1
      
    print(Last5Games)
    WinRate = WinRate / 5
    print(WinRate)

    print(MeanData)

    avgGoldPerMin = MeanData['avgGoldPerMin'].pop()
    totalDamageTakenPerMin = MeanData['totalDamageTakenPerMin'].pop()
    totalDamageTakenPerMin = MeanData['totalDamageTakenPerMin'].pop()
    summ = SummonerInGame(Rank, WinRate, avgGoldPerMin,totalDamageTakenPerMin,totalDamageTakenPerMin)
    Summoners.append(summ)
    print(summ)
    time.sleep(10)
  
