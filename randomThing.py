import pandas as pd
import numpy as np

df = pd.read_csv('C:\\Users\\cheem\\Downloads\\shots_data.csv')

def cornerCheck(x,y):
    if (x >= 22.0 or x <= -22.0) and y <= 7.8:
        return 1
    else:
        return 0
    
def nonCornerCheck(x,y):
    if (np.sqrt(x**2+y**2) > 23.75) and y > 7.8:
        return 1
    else:
        return 0
    
def efgPct(two,fga,fgm):
    if two == 1:
        return fgm/fga
    else:
        return (1.5*fgm)/fga
    
df['cornerThree'] = np.vectorize(cornerCheck)(df.x,df.y)
df['nonCornerThree'] = np.vectorize(nonCornerCheck)(df.x,df.y)
df['twoPt'] = np.where((df.cornerThree == 0) & (df.nonCornerThree == 0),1,0)

gpby = df[['team','fgmade','cornerThree','nonCornerThree',
           'twoPt']].groupby(['team','cornerThree','nonCornerThree','twoPt'])
fin = gpby.agg(['count','sum']).reset_index(drop=False)
fin.columns = fin.columns.get_level_values(0)
fin.columns = ['team','cornerThree','nonCornerThree','twoPt','fga','fgm']

fin['efg_pct'] = np.vectorize(efgPct)(fin.twoPt,fin.fga,fin.fgm)
fin['pct_fga'] = fin.fga/280
