## GLOBAL #######################################################################################
#################################################################################################
import math
import pandas as pd

## FUNCTIONS ####################################################################################
#################################################################################################
# Function to isolate the respective play, its players, and its metadata to reduce compute
def isolate_play(csv, targetGameId, targetPlayId):
    working_csv = pd.read_csv(csv)

    # filter rows by targetGameId and targetPlayId
    filtered_csv = working_csv[
        (working_csv['gameId'] == targetGameId) & (working_csv['playId'] == targetPlayId)
    ]

    #return dataframe of the filtered rows
    return filtered_csv

    #filtered_csv.to_csv('data/processed/temp', index = False)

# Function to compute Euclidean distance between two coordinate points
def compute_distance(target1, target2): 
    """
    Computes the Euclidean distances from one tuple to another tuple

    Parameters:
        target1 (tuple): Coordinates of target1 as (x, y).
        target2 (tuple): Coordinates of target2 as (x, y).

    Returns:
        float: The Euclidean distance between the two points.
    """

    x1, y1 = target1
    x2, y2 = target2
    
    # Calculate the distance
    distance = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    
    # theta is based on target1 as the reference point
    theta_rad = math.atan((y2-y1), (x2-x1))
    theta_deg = math.degrees(theta_rad)

    return distance,theta_deg

# Function to find closest teammates regardless of defense/offense in given frame
def find_closest_teammates_distance(csv, frameId, targetId, teammates_quantity):
    working_csv = pd.read_csv(csv)

    #filter rows by target frameid
    frame_data = working_csv[working_csv['frameId'] == frameId]

    #isolate the target player's row based on targetId
    target_player = frame_data[frame_data['playerId'] == targetId].iloc[0]

    #get the target player's team role (offense/defense)
    target_role = target_player['team_side']  # 'offense' or 'defense'
    
    #get all teammates of the same role (offense or defense)
    teammates = frame_data[frame_data['team_side'] == target_role]
    
    #get the target player's coordinates
    target_coords = (target_player['x'], target_player['y'])

    #create a list of tuples (playerId, distance) for all teammates
    distances = []

    for _, teammate in teammates.iterrows():
        #skip the target player itself
        if teammate['playerId'] == targetId:
            continue
        
        teammate_coords = (teammate['x'], teammate['y'])
        
        #compute distance to teammate
        distance,theta_deg = compute_distance(target_coords, teammate_coords)
        
        #append the playerId and distance to the list
        distances.append((teammate['playerId'], distance, theta_deg))

    #sort the list by distance (ascending) and select the closest teammates
    closest_teammates = sorted(distances, key=lambda x: x[1])[:teammates_quantity]

    return closest_teammates

# Function to find closest opponents regardless of defense/offense in given frame
def find_closest_opponents_distance(csv, frameId, targetId, opponents_quantity):
    working_csv = pd.read_csv(csv)

    #filter rows by target frameid
    frame_data = working_csv[working_csv['frameId'] == frameId]

    #isolate the target player's row based on targetId
    target_player = frame_data[frame_data['playerId'] == targetId].iloc[0]

    #get the target player's team role (offense/defense)
    target_role = target_player['team_side']  # 'offense' or 'defense'
    
    #get all opponents of the same role (offense or defense)
    opponents = frame_data[frame_data['team_side'] != target_role]
    
    #get the target player's coordinates
    target_coords = (target_player['x'], target_player['y'])

    #create a list of tuples (playerId, distance) for all opponents
    distances = []

    for _, opponents in opponents.iterrows():
        #skip the target player itself
        if opponents['playerId'] == targetId:
            continue
        
        opponents_coords = (opponents['x'], opponents['y'])
        
        #compute distance to opponent
        distance,theta_deg = compute_distance(target_coords, opponents_coords)
        
        #append the playerId and distance to the list
        distances.append((opponents['playerId'], distance, theta_deg))

    #sort the list by distance (ascending) and select the closest opponents
    closest_opponents = sorted(distances, key=lambda x: x[1])[:opponents_quantity]

    return closest_opponents

def find_football_distance(csv, frameId, targetId):
    working_csv = pd.read_csv(csv)

    #filter rows by target frameid
    frame_data = working_csv[working_csv['frameId'] == frameId]

    #isolate the target player's row based on targetId
    target_player = frame_data[frame_data['playerId'] == targetId].iloc[0]

    #find the NaN team_side rows which should be the football
    ball = frame_data[frame_data['team_side'] == 'NaN']

    #get the target player's coordinates
    target_coords = (target_player['x'], target_player['y'])

    #get the ball's coordinates
    ball_coords = (ball['x'], ball['y'])

    #compute distance to ball from target
    distance,theta_deg = compute_distance(target_coords, ball_coords)

    return distance,theta_deg

def gap_sequencer(csv):
    try:
        working_csv = pd.read_csv(csv)
    except FileNotFoundError:
        return "Error: The specified CSV file does not exist. Please check the file path and try again."
    
    # Filter rows with frameType SNAP or AFTER_SNAP
    filtered_data = working_csv[working_csv['frameType'].isin(['SNAP', 'AFTER_SNAP'])]

    # Group by gameId and playId to create sequences
    sequences = []
    gap_analysis = []  # Added: List to store gap analysis for each play

    for (game_id, play_id), play_data in filtered_data.groupby(['gameId', 'playId']):
        frames = []
        for frame_id, frame_data in play_data.groupby('frameId'):

            # Apply position reassignment for all relevant frames
            frame_data = reassign_positions(frame_data)

            # Only keep SNAP frame and only 10 AFTER_SNAP frames
            if len(frames) >= 11:
                break

            # Extract features (example: x, y, position)
            frame_features = frame_data[['x', 'y', 'position']].values
            frames.append(frame_data)  # Updated: Append full frame_data for gap analysis later

        sequences.append(frames)

        # Added: Perform gap analysis for the play
        if len(frames) == 11:  # Ensure we have all 21 frames
            gap_result = find_gaps(frames, game_id, play_id)
            if gap_result:
                gap_analysis.append(gap_result)

    return sequences, gap_analysis  # Updated: Return gap_analysis along with sequences

def reassign_positions(frame_data):
    """
    Reassigns positions for offensive line players based on their 'y' values.
    The positions 'LT', 'LG', 'C', 'RG', 'RT' are assigned based on descending order of 'y'.
    """
    # Filter players with initial positions relevant to the offensive line
    offensive_line = frame_data[frame_data['position'].isin(['T', 'G', 'C'])]
    if len(offensive_line) < 5:
        return frame_data  # Skip reassignment if there aren't enough players

    # Sort by 'y' value in descending order
    offensive_line_sorted = offensive_line.sort_values(by='y', ascending=False)

    # Ensure we have exactly 5 players to assign positions
    offensive_line_sorted = offensive_line_sorted.head(5)
    
    # Assign new positions based on the sorted 'y' values
    new_positions = ['LT', 'LG', 'C', 'RG', 'RT']
    for i, (index, _) in enumerate(offensive_line_sorted.iterrows()):
        frame_data.loc[index, 'position'] = new_positions[i]
    
    return frame_data


def find_gaps(frames, game_id, play_id):
    """
    Identifies which gaps are attacked by defensive players based on their relative position to each gap
    Returns the defensive player ('nflId') who was in each gap the longest, or none if no player was in the gap.
    """
    #combine all frames into a single dataFrame
    combined_frames = pd.concat(frames)

    #ensure numeric columns for aggregation
    numeric_columns = ['x', 'y']
    avg_positions = (
        combined_frames.groupby('nflId')[numeric_columns]
        .mean()
        .reset_index()
    )

    #find the 'y' positions for the offensive line
    offensive_line = combined_frames[combined_frames['position'].isin(['LT', 'LG', 'C', 'RG', 'RT'])]
    if len(offensive_line) < 5:
        raise ValueError("Not enough offensive line players")

    #calculate average positions for offensive line players
    avg_offensive_line = (
        offensive_line.groupby('position')[numeric_columns]
        .mean()
        .sort_values(by='y', ascending=False)
        .reset_index()
    )

    #define gap positions
    gap_positions = {
        'left_c': avg_offensive_line.iloc[0]['y'] - 1,  #LT
        'left_b': (avg_offensive_line.iloc[0]['y'] + avg_offensive_line.iloc[1]['y']) / 2,  #LT-LG
        'left_a': (avg_offensive_line.iloc[1]['y'] + avg_offensive_line.iloc[2]['y']) / 2,  #LG-C
        'right_a': (avg_offensive_line.iloc[2]['y'] + avg_offensive_line.iloc[3]['y']) / 2,  #C-RG
        'right_b': (avg_offensive_line.iloc[3]['y'] + avg_offensive_line.iloc[4]['y']) / 2,  #RG-RT
        'right_c': avg_offensive_line.iloc[4]['y'] + 1,  #RT
    }

    #initialize a dictionary to track the nflId of the player filling each gap
    gap_filled_by_player = {gap: {'nflId': None, 'time_spent': 0} for gap in gap_positions.keys()}

    #define the list of defensive positions
    defensive_positions_of_interest = ['DE', 'DT', 'SS', 'OLB', 'ILB', 'NT', 'MLB', 'LB', 'FS', 'DB', 'CB']

    #filter combined_frames to get only the defensive players with relevant positions
    defensive_players = combined_frames[combined_frames['position'].isin(defensive_positions_of_interest)]

    #group defensive players by 'nflId' and calculate their average position
    avg_defensive_positions = (
        defensive_players.groupby('nflId')[numeric_columns]
        .mean()
        .reset_index()
    )

    for _, player in avg_defensive_positions.iterrows():
        for gap, gap_y in gap_positions.items():
            #calculate distance of the defensive player to the gap
            distance = abs(player['y'] - gap_y)

            #if the player is within a threshold distance of the gap, consider them as attacking the gap
            if distance < 1:  #adjust threshold as needed
                gap_filled_by_player[gap]['nflId'] = player['nflId']
                gap_filled_by_player[gap]['time_spent'] += 1  #increment time spent in the gap based on frames

    #which gap is longest
    gap_result = {}
    for gap, data in gap_filled_by_player.items():
        if data['nflId'] is not None:
            gap_result[gap] = {
                'nflId': data['nflId'], 
                'time_spent': data['time_spent']
            }

    return {
        'gameId': game_id, 'playId': play_id, 'gapsAttacked': gap_result
    }

#test
sequences, gap_analysis = gap_sequencer('data/processed/organized_final_tracking_week_1.csv')

for i, sequence in enumerate(sequences[:1], start=1):
    print(f"Sequence {i}: {sequence} \n")

for gap_result in gap_analysis[:50]:
    print(f"Gap Analysis: {gap_result} \n")
