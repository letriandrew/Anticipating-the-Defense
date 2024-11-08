import pandas as pd
import numpy as np

players = pd.read_csv('data/players.csv')
players = players[['nflId', 'position']]

plays = pd.read_csv('data/plays.csv')
plays = plays[[
    'gameId', 'playId', 'quarter', 'down', 'yardsToGo', 'yardlineNumber', 'gameClock', 'playClockAtSnap', 'prePenaltyYardsGained', 'yardsGained'
]]

#combine week 1 to 9 and flip plays in the left direction
for week in range(1, 10):
    print(f"Augmenting Week {week}")
    tracking = pd.read_csv(f'data/tracking_week_{week}.csv')
    #120 yards is length of field including endzones... inverse x position
    tracking.loc[tracking['playDirection'] == 'left', 'x'] = 120 - tracking['x'] 
    #invert direction
    tracking.loc[tracking['playDirection'] == 'left', 'dir'] = 360- tracking['dir']
    #edge cases to make sure we are not getting plays that begin in the endzone because that's impossible
    tracking.loc[tracking['x'] > 111, 'x'] = 111
    tracking.loc[tracking['x'] < 9, 'x'] = 9
    #edge cases for above but for the vertical positions (y)
    tracking.loc[tracking['y'] >= 53.3, 'y'] = 53.2
    tracking.loc[tracking['y'] < 0, 'y'] = 0
    #new column to track week
    tracking['week'] = week

    #STILL NEED TO IMPLEMENT REMOVAL OF CERTAIN FRAMES WE DON'T NEED (SPECIAL TEAMS, ETC)

    #IMPLEMENT OTHER NEEDED FEATURES LIKE MERGE OF PLAYS AND PLAYERS

    #createCSV.to_csv(f'data/final_tracking_week_{week}.csv')
    #if file exists, override