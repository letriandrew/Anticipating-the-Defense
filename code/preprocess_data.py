import pandas as pd
import numpy as np

players = pd.read_csv('data/players.csv')
players = players[['nflId', 'position']]

plays = pd.read_csv('data/plays.csv')
plays = plays[[
    'gameId', 'playId', 'quarter', 'down', 'yardsToGo', 'possessionTeam', 'defensiveTeam', 'preSnapHomeScore', 'preSnapVisitorScore', 'playNullifiedByPenalty', 'expectedPoints', 'offenseFormation', 'receiverAlignment', 'qbSpike', 'qbKneel', 'passResult', 'yardlineNumber', 'gameClock', 'playClockAtSnap', 'prePenaltyYardsGained', 'yardsGained', 'homeTeamWinProbabilityAdded', 'visitorTeamWinProbilityAdded', 'expectedPointsAdded', 'qbSneak'
]]

final_tracking = pd.DataFrame()

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

    #save new csv file
    tracking.to_csv(f'data/processed/final_tracking_week_{week}.csv', index=False)

    #append processed tracking dataframe to final dataframe
    final_tracking = pd.concat([final_tracking, tracking], ignore_index=True)

    #remove unneccessary data and rows
    filtered_plays = plays.query('playNullifiedByPenalty == False and qbKneel == 0 and qbSpike != True')

    #plays.csv -> playsNullifiedByPenalty, offensiveFormation, receiverAlignment, passResult, qbSpike, qbKneel
    #NO QB KNEELS, NO QB SPIKES, NO PENALTY PLAYS

    # Merge tracking data with players and plays
    merged_data = tracking.merge(players, on='nflId', how='left')
    merged_data = merged_data.merge(filtered_plays, on=['gameId', 'playId'], how='left')

    # Save the processed data for the week to a CSV file
    merged_data.to_csv(f'data/processed/final_tracking_week_{week}.csv', index=False)

    print(f"Week {week} processing complete.")


print("Data processing and merging complete.")

#expected points

#createCSV.to_csv(f'data/final_tracking_week_{week}.csv')
#if file exists, override