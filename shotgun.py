import matplotlib.pyplot as plot
import pandas as pd
import numpy as np

df = pd.read_csv("pbp.csv")
df = df[['game_date', 'yards_gained','play_type','shotgun']]

# creates table that will store frequency of the shotgun formation for each season
shotgun_history = pd.DataFrame(columns =['frequency']) 

# the 'for loop' will iteratively calculate the frequency of the shotgun formation for each season and add it to the previously created table
for yr in ['2009','2010','2011','2012','2013','2014','2015','2016','2017','2018']:
    
    ndf = df[(df.game_date.str.contains(yr))]
    
    frequency = sum(ndf.shotgun == 1) / (sum(ndf.shotgun == 1) + sum(ndf.shotgun == 0))
    
    shotgun_history.loc[yr] = [frequency]
    
# creates table that will store the average passing efficiency for each season while in and out of the shotgun formation
pass_eff = pd.DataFrame(columns =['shotgun_ypa', 'non_shotgun_ypa'])

# the 'for loop' will iteratively calculate the passing efficiency for each season while in and out of the shotgun formation and add it to the previously created table
for yr in ['2009','2010','2011','2012','2013','2014','2015','2016','2017','2018']:

    df = df[['game_date', 'yards_gained','play_type','shotgun']]

    pass_yes_shotgun_df = df[(df.game_date.str.contains(yr)) & (df.play_type == 'pass') & (df.shotgun == 1)]
    pass_no_shotgun_df = df[(df.game_date.str.contains(yr)) & (df.play_type == 'pass') & (df.shotgun == 0)]

    shotgun_ypa = pass_yes_shotgun_df.yards_gained.mean()
    non_shotgun_ypa = pass_no_shotgun_df.yards_gained.mean()
    
    pass_eff.loc[yr] = [shotgun_ypa, non_shotgun_ypa]

fig, ax1 = plt.subplots()

# create a secondary y-axis
ax2 = ax1.twinx()

# plotting the three different lines on the graph
ax1.plot(shotgun_history.index, shotgun_history.frequency, 'g-', label='frequency of shotgun form')
ax2.plot(shotgun_history.index, pass_eff.shotgun_ypa, 'r-', label='ypa inside of shotgun form')
ax2.plot(shotgun_history.index, pass_eff.non_shotgun_ypa, 'b-', label='ypa outside of shotgun form')

# labels for the axes
ax1.set_xlabel("year")
ax1.set_ylabel('shotgun formation relative frequency')
ax2.set_ylabel('yards gained per pass attempt')

# credit for multi-axis legend: https://stackoverflow.com/a/14344146/11949019
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
plt.legend(h1+h2, l1+l2, loc='upper left', fontsize='small')

# adding a title and adjusting margins
plt.title("frequency of shotgun formation vs passing efficiency over time")
plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)

plt.show()
