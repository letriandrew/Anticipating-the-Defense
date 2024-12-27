## GLOBAL #######################################################################################
#################################################################################################
import math
import pandas as pd
import os 

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

def add_gap_info_to_before_snap(csv, gap_analysis):
    try:
        working_csv = pd.read_csv(csv)
        before_snap_data = working_csv[working_csv['frameType'] == 'BEFORE_SNAP']
    except FileNotFoundError:
        return "Error: The specified CSV file does not exist. Please check the file path and try again."
    
    #list of only defensive positions
    allowed_defensive_positions = ['DE', 'DT', 'SS', 'OLB', 'ILB', 'NT', 'MLB', 'LB', 'FS', 'DB', 'CB']

    #initialize result storage
    result_rows = []

    #merge gap_analysis output for mapping
    gap_df = pd.DataFrame(gap_analysis)
    combined_data = pd.merge(
        before_snap_data,
        gap_df[['gameId', 'playId', 'gapsAttacked']],
        on=['gameId', 'playId'],
        how='left'
    )

    #iterate through each BEFORE_SNAP frame and create the gap columns
    for _, row in combined_data.iterrows():
        game_id = row['gameId']
        play_id = row['playId']
        nfl_id = row['nflId']
        frame_id = row['frameId']
        x = row['x']
        y = row['y']
        position = row['position']
        gaps_attacked = row['gapsAttacked']

        #default values for gaps if no information is available
        gap_data = {
            'gameId': game_id,
            'playId': play_id,
            'nflId': nfl_id,
            'frameId': frame_id,
            'x': x,
            'y': y,
            'position': position,
            'left_c': None,
            'left_b': None,
            'left_a': None,
            'right_a': None,
            'right_b': None,
            'right_c': None
        }

        #only assign nflId to gaps if the defensive player is in the allowed list of positions
        if pd.notna(gaps_attacked):  #check if gapsAttacked has valid data
            for gap, info in gaps_attacked.items():
                nfl_id = info.get('nflId', None)
                
                #only fill the gap if the player has an allowed defensive position
                if nfl_id is not None and position in allowed_defensive_positions:
                    gap_data[gap] = nfl_id  #assign the nflId to the gap column

        result_rows.append(gap_data)

    #convert the result to a DF
    result_df = pd.DataFrame(result_rows)

    #return DF for BEFORE_SNAP data with gaps and frame details to keep x, y, and position
    return result_df

def aggregate_play_data(input_csv):
    """
    This function aggregates the player position data for each gameId, playId, and frameId, creating a sequence of player positions while keeping the gap columns

    """
    #load the CSV into a DataFrame
    df = pd.read_csv(input_csv)
    
    #remove the 'position' column 
    df = df.drop(columns=['position'])

    #group by gameId, playId, and frameId to collect player data
    grouped = df.groupby(['gameId', 'playId', 'frameId'])

    #prepare a list to hold the processed rows
    aggregated_data = []

    #iterate over the groups and aggregate data for each game-play-frame sequence
    for (gameId, playId, frameId), group in grouped:
        play_sequence = []
        
        #extract gap values from the first frame (assuming they are the same across all frames in a play)
        if frameId == group['frameId'].iloc[0]:  # Only get gap values for the first frame
            gap_values = group[['left_c', 'left_b', 'left_a', 'right_a', 'right_b', 'right_c']].iloc[0].tolist()
        
        #create the sequence of player data for each frame
        frame_list = group[['nflId', 'x', 'y']].values.tolist()
        play_sequence.append(frame_list)
        
        #check if the row for this game and play exists, and create a new row if not
        existing_row = next((row for row in aggregated_data if row['gameId'] == gameId and row['playId'] == playId), None)
        if not existing_row:
            row = {
                'gameId': gameId,
                'playId': playId,
                'left_c': gap_values[0],
                'left_b': gap_values[1],
                'left_a': gap_values[2],
                'right_a': gap_values[3],
                'right_b': gap_values[4],
                'right_c': gap_values[5],
                'sequence': [play_sequence]
            }
            aggregated_data.append(row)
        else:
            #add the sequence data for this frame to the existing row
            existing_row['sequence'].append(play_sequence)


    aggregated_df = pd.DataFrame(aggregated_data)

    aggregated_df.to_csv('data/processed/final_tracking_week_1_aggregated.csv', index=False)

    print(f"Aggregated data with gap columns has been saved.")


#test
sequences, gap_analysis = gap_sequencer('data/processed/organized_final_tracking_week_1.csv')

"""
for i, sequence in enumerate(sequences[:1], start=1):
    print(f"Sequence {i}: {sequence} \n")

for gap_result in gap_analysis[:1]:
    print(f"Gap Analysis: {gap_result} \n")
"""

before_snap_data = add_gap_info_to_before_snap('data/processed/organized_final_tracking_week_1.csv', gap_analysis)

#define a list of positions to exclude
exclude_positions = ['T', 'G', 'C', 'TE']

#filter the DataFrame to exclude these positions
before_snap_data = before_snap_data[~before_snap_data['position'].isin(exclude_positions)]

before_snap_data.to_csv('data/processed/organized_final_tracking_week_1_before_snap.csv', index=False)

aggregate_play_data('data/processed/organized_final_tracking_week_1_before_snap.csv')