## GLOBAL #######################################################################################
#################################################################################################
import pandas as pd
import numpy as np
import sys

## INIT #########################################################################################
#################################################################################################
players = pd.read_csv('data/players.csv')
players = players[['nflId', 'position']]

plays = pd.read_csv('data/plays.csv')
plays = plays[[
    'gameId', 'playId', 'playDescription', 'yardsToGo', 'playNullifiedByPenalty', 'qbSpike', 'qbKneel', 'absoluteYardlineNumber', 'yardsGained',  'qbSneak',  'pff_runPassOption', 'rushLocationType', 'passResult', 'pff_runConceptPrimary', 'pff_runConceptSecondary'
]]

#columns removed = 'playDescription, 'quarter', 'down', 'possessionTeam', 'defensiveTeam', 'preSnapHomeScore', 'preSnapVisitorScore', 'passResult',

# distinguish between plays with pre-play MOVEMENT (not just motion) and those without 
player_play = pd.read_csv('data/player_play.csv')
player_play = player_play[['gameId', 'playId', 'nflId']]
#player_play = player_play[['gameId', 'playId', 'nflId', 'inMotionAtBallSnap', 'shiftSinceLineset', 'motionSinceLineset']]

"""
# filter rows where any columns 'inMotionAtBallSnap', 'shiftSinceLineset', or 'motionSinceLineset' are True
movement_plays = player_play[
    (player_play['inMotionAtBallSnap'] == True) | 
    (player_play['shiftSinceLineset'] == True) | 
    (player_play['motionSinceLineset'] == True)
]

#movement_plays.to_csv('data/processed/movement_player_plays.csv')
"""

#remove unneccessary data and rows 
filtered_plays = plays[
    (plays['playNullifiedByPenalty'] == 'N') &
    (plays['qbKneel'] == 0) &
    (plays['qbSpike'] != True) &
    (plays['qbSneak'] != True)
]

#remove columns we don't need anymore since we filtered out above parameters
filtered_plays = filtered_plays.drop(columns=['playNullifiedByPenalty', 'qbKneel', 'qbSpike', 'qbSneak'])

# NOTE = NO QB KNEELS, NO QB SPIKES, NO PENALTY PLAYS

## FUNCTIONS ####################################################################################
#################################################################################################

def create_final_tracking_week():

    #combine week 1 to 9 and flip plays in the left direction
    for week in range(1, 2):
        print(f"Augmenting Week {week}")
        tracking = pd.read_csv(f'data/tracking_week_{week}.csv')

        #120 yards is length of field including endzones... inverse x position
        tracking.loc[tracking['playDirection'] == 'left', 'x'] = 120 - tracking['x'] 

        #invert direction
        tracking.loc[tracking['playDirection'] == 'left', 'dir'] = 360 - tracking['dir']

        #make sure nflid is not a floatvalue
        tracking['nflId'] = tracking['nflId'].fillna(0).astype(int)

        #merge tracking data with players and plays
        merged_data = tracking.merge(players, on='nflId', how='left')

        merged_data = merged_data.merge(filtered_plays, on=['gameId', 'playId'], how='left')

        positions = ['TE', 'T', 'G', 'C', 'DE', 'DT', 'SS', 'OLB', 'ILB', 'NT', 'MLB', 'LB', 'FS', 'DB']

        merged_data = merged_data[merged_data['position'].isin(positions)]

        #keep only rows where 'pff_runConceptPrimary' is not NA (run plays)
        merged_data = merged_data[merged_data['pff_runConceptPrimary'].notna()]

        #keep only hard run plays no RPO
        merged_data = merged_data[merged_data['pff_runPassOption'] == 0]

        merged_data = merged_data[merged_data['passResult'].isna()]
        
        merged_data = merged_data[merged_data['rushLocationType'].notna()]

        #remove headway 
        merged_data = merged_data.drop(columns=['displayName', 'time', 'jerseyNumber', 'playDescription', 'pff_runConceptPrimary', 'pff_runPassOption', 'rushLocationType', 'absoluteYardlineNumber', 'pff_runConceptSecondary', 'club', 's', 'a','dis','o','dir', 'playDirection', 'passResult', 'yardsToGo', 'yardsGained', 'event'])

        #save to csv file
        merged_data.to_csv(f'data/processed/final_tracking_week_{week}.csv', index=False)


        print(f"Week {week} processing complete.")

## MAIN #########################################################################################
#################################################################################################
if __name__ == "__main__":
    create_final_tracking_week()

    print("Data processing and merging complete.")