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

    filtered_csv.to_csv('data/processed/temp', index = False)

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
    
    return distance

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
        distance = compute_distance(target_coords, teammate_coords)
        
        #append the playerId and distance to the list
        distances.append((teammate['playerId'], distance))

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
        distance = compute_distance(target_coords, opponents_coords)
        
        #append the playerId and distance to the list
        distances.append((opponents['playerId'], distance))

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
    distance = compute_distance(target_coords, ball_coords)

    return distance