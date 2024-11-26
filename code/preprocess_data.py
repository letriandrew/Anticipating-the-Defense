import pandas as pd
import numpy as np

players = pd.read_csv('data/players.csv')
players = players[['nflId', 'position']]

plays = pd.read_csv('data/plays.csv')
plays = plays[[
    'gameId', 'playId', 'playDescription', 'quarter', 'down', 'yardsToGo', 'possessionTeam', 'defensiveTeam', 'preSnapHomeScore', 'preSnapVisitorScore', 'playNullifiedByPenalty', 'expectedPoints', 'offenseFormation', 'receiverAlignment', 'qbSpike', 'qbKneel', 'passResult', 'yardlineNumber', 'gameClock', 'playClockAtSnap', 'prePenaltyYardsGained', 'yardsGained', 'homeTeamWinProbabilityAdded', 'visitorTeamWinProbilityAdded', 'expectedPointsAdded', 'qbSneak'
]]


#remove unneccessary data and rows THIS IS NOT WORKING PROPERLY
filtered_plays = plays[
    (plays['playNullifiedByPenalty'] == 'N') &
    (plays['qbKneel'] == 0) &
    (plays['qbSpike'] != True)
]

#combine week 1 to 9 and flip plays in the left direction
for week in range(1, 10):
    print(f"Augmenting Week {week}")
    tracking = pd.read_csv(f'data/tracking_week_{week}.csv')

    #120 yards is length of field including endzones... inverse x position
    tracking.loc[tracking['playDirection'] == 'left', 'x'] = 120 - tracking['x'] 

    #invert direction
    tracking.loc[tracking['playDirection'] == 'left', 'dir'] = 360 - tracking['dir']

    #edge cases to make sure we are not getting plays that begin in the endzone because that's impossible
    tracking.loc[tracking['x'] > 111, 'x'] = 111
    tracking.loc[tracking['x'] < 9, 'x'] = 9

    #edge cases for above but for the vertical positions (y)
    tracking.loc[tracking['y'] >= 53.3, 'y'] = 53.2
    tracking.loc[tracking['y'] < 0, 'y'] = 0

    #new column to track week
    tracking['week'] = week

    #make sure nflid is not a floatvalue
    tracking['nflId'] = tracking['nflId'].fillna(0).astype(int)

    #plays.csv -> playsNullifiedByPenalty, offensiveFormation, receiverAlignment, passResult, qbSpike, qbKneel
    #NO QB KNEELS, NO QB SPIKES, NO PENALTY PLAYS

    #merge tracking data with players and plays
    merged_data = tracking.merge(players, on='nflId', how='left')

    merged_data = merged_data.merge(filtered_plays, on=['gameId', 'playId'], how='left')

    #save to csv file
    merged_data.to_csv(f'data/processed/final_tracking_week_{week}.csv', index=False)


    print(f"Week {week} processing complete.")


print("Data processing and merging complete.")

#expected points = metric to train for positive actions