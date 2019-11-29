import pandas as pd
import numpy as np
import requests
import json

headers = {'Host': 'stats.nba.com','User-Agent': 'Firefox/55.0','Accept': 'application/json, text/plain, */*','Accept-Language': 'en-US,en;q=0.5','Accept-Encoding': 'gzip, deflate','Referer': 'https://stats.nba.com/','x-nba-stats-origin': 'stats','x-nba-stats-token': 'true','DNT': '1',}

df_list = []

cat = ['3+Pointers','2+Pointers','Less+Than+6Ft','Less+Than+10Ft','Greater+Than+15Ft']

yr = '2018-19' # obviously change this to calculate for different seasons... data doesn't go further back than 2013-14 ssn

for x in cat:
    
    url = 'https://stats.nba.com/stats/leaguedashptdefend?College=&Conference=&Country=&DateFrom=&DateTo=&DefenseCategory=' + str(x) + '&Division=&DraftPick=&DraftYear=&GameSegment=&Height=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PerMode=Totals&Period=0&PlayerExperience=&PlayerPosition=&Season=' + str(yr) + '&SeasonSegment=&SeasonType=Regular+Season&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight='

    json = requests.get(url, headers=headers).json()

    data = json['resultSets'][0]['rowSet']
    columns = json['resultSets'][0]['headers']

    df = pd.DataFrame.from_records(data, columns=columns)
    
    if x == '3+Pointers':
        
        df = df[['CLOSE_DEF_PERSON_ID','PLAYER_NAME','PLAYER_LAST_TEAM_ABBREVIATION','FG3M','FG3A']]
        
    elif x == '2+Pointers':
        
        df = df[['CLOSE_DEF_PERSON_ID','PLAYER_NAME','PLAYER_LAST_TEAM_ABBREVIATION','FG2M','FG2A']]
        
    elif x == 'Less+Than+6Ft':
        
        df = df[['CLOSE_DEF_PERSON_ID','PLAYER_NAME','PLAYER_LAST_TEAM_ABBREVIATION','FGM_LT_06','FGA_LT_06']]
    
    elif x == 'Less+Than+10Ft':
        
        df = df[['CLOSE_DEF_PERSON_ID','PLAYER_NAME','PLAYER_LAST_TEAM_ABBREVIATION','FGM_LT_10','FGA_LT_10']]
        
    elif x == 'Greater+Than+15Ft':
        
        df = df[['CLOSE_DEF_PERSON_ID','PLAYER_NAME','PLAYER_LAST_TEAM_ABBREVIATION','FGM_GT_15','FGA_GT_15']]
        
    df.columns = ['player_id','player_name','tm','fgm','fga']
        
    df_list.append(df)
    
db_list = []

for n in range(0,len(df_list)):

    db = df_list[n][['player_id','player_name','tm']]
    
    db_list.append(db)
    
db = pd.concat(db_list).drop_duplicates().reset_index(drop=True)

three = df_list[0]
two = df_list[1]
lt6 = df_list[2]
lt10 = df_list[3]
gt15 = df_list[4]

final = db.copy()

for df in [three,two,lt6,lt10,gt15]:

    final = pd.merge(final,df[['player_id','fgm','fga']],on='player_id',how='outer')

final.columns = ['player_id','player_name','tm','fg3m','fg3a','fg2m','fg2a','lt6m','lt6a','lt10m','lt10a','gt15m','gt15a']

final.fillna(0, inplace=True)

final['gt15m'] -= final.fg3m
final['gt15a'] -= final.fg3a

final['b6t10m'] = final.lt10m - final.lt6m
final['b6t10a'] = final.lt10a - final.lt6a

final['b10t15m'] = final.fg2m - (final.gt15m + final.lt10m)
final['b10t15a'] = final.fg2a - (final.gt15a + final.lt10a)

final['fga'] = final.fg2a + final.fg3a

final = final[['player_id','player_name','tm','lt6m','lt6a','b6t10m','b6t10a','b10t15m','b10t15a','gt15m','gt15a','fg2m','fg2a','fg3m','fg3a','fga']]

final['efg'] = (final.fg2m + (1.5 * final.fg3m)) / final.fga

fg3v = final.fg3m.sum() / final.fg3a.sum()
fg2v = final.fg2m.sum() / final.fg2a.sum()
lt6v = final.lt6m.sum() / final.lt6a.sum()
b6t10v = final.b6t10m.sum() / final.b6t10a.sum()
b10t15v = final.b10t15m.sum() / final.b10t15a.sum()
gt15v = final.gt15m.sum() / final.gt15a.sum()

final['x2pm'] = (final.lt6a * lt6v) + (final.b6t10a * b6t10v) + (final.b10t15a * b10t15v) + (final.gt15a * gt15v)

final['x3pm'] = final.fg3a * fg3v

final['xefg'] = (final.x2pm + (1.5 * final.x3pm)) / final.fga

final['diff'] = final.efg - final.xefg

dxefg = final[['player_name','tm','fga','xefg','efg','diff']]

dxefg = dxefg.sort_values(by='player_name').reset_index(drop=True)
