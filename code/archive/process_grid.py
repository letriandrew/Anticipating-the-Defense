## GLOBAL #######################################################################################
#################################################################################################
import math
import pandas as pd
from pathlib import Path
import sys
import os
import time

## INIT #########################################################################################
#################################################################################################
# adding to path
abs_path = str(Path(__file__).parent.parent)
sys.path.insert(0, abs_path)
"""
# filtered week play from preprocess_data.py
week1 = pd.read_csv(abs_path+'/data/processed/final_tracking_week_1.csv')

# nflId is playerId

# grab unique gameId playId pairs
gameid_playid_arr = []
for idx in range (0, len(week1["gameId"])):
    if [int(week1["gameId"][idx]), int(week1["playId"][idx])] not in gameid_playid_arr:
        gameid_playid_arr.append([int(week1["gameId"][idx]), int(week1["playId"][idx])])
"""

## FUNCTIONS ####################################################################################
#################################################################################################

# height and width of a football field, x2, rounded up. total space 120 * 54 = 6480
# 7.5 yard padding because certain edge case where players run off field
h = int((120 + 7.5))
w = int(math.ceil(53.3 + 7.5))

def create_grid():
    arr = [[0 for i in range(w)] for j in range(h)]
    arr = [[0 for i in range(w)] for j in range(h)]
    return arr

def consume_input(input_file):
    idx = 0
    x = 0
    y = 0
    position_occupied_grid = create_grid()
    home_team_density_grid = create_grid()
    away_team_density_grid = create_grid()

    frames = []
    count = 0

    with open(input_file, "r") as file:
        for line in file:
            line = line.strip().split()

            if not line:
                x = 0
                y = 0
                idx +=1
            elif "=" in line[0]:
                # new frame detected
                # do something
                frames.append([position_occupied_grid, home_team_density_grid, away_team_density_grid])
                position_occupied_grid = create_grid()
                home_team_density_grid = create_grid()
                away_team_density_grid = create_grid()
                x = 0
                y = 0
                idx = 0
            else:
                # modify position grid
                if idx == 0:
                    for cell in line:
                        position_occupied_grid[y][x] = int(cell)
                        x += 1
                # modify home_team_density grid
                elif idx == 1:
                    for cell in line:
                        home_team_density_grid[y][x] = int(cell)
                        x += 1
                # modify away_team_density grid
                elif idx == 2:
                    for cell in line:
                        away_team_density_grid[y][x] = int(cell)
                        x += 1
                y += 1
                x = 0
    
    # returns a list of 3 arrays for each frame: 1. position_occupied_grid, 2. home_team_density_grid, 3. away_team_density_grid
    return frames
    
    
## MAiN #########################################################################################
#################################################################################################
if __name__ == "__main__":
    week_string = "week1/"
    parsed_data_path = abs_path + "/code/parsed_data/" + week_string
    length = 0
    start_time = time.time()
    print(f"Iterating over {parsed_data_path} grid files")
    if os.path.exists(parsed_data_path):
        lst = os.listdir(parsed_data_path)
        length = len(lst)
        print(f"Total of {length} plays to iterate")
        idx = 0
        try:
            for filename in lst:
                print(f"{idx}/{length}",f"{idx/length*100:.3f}","percent complete         \r",end="")
                f = os.path.join(parsed_data_path, filename)
                
                frames = consume_input(f)
                idx +=1

        except Exception as error:
            print()
            print("Program crashed while reading:", error)
            exit()
    print(f"{length}/{length}",f"{length/length*100:.3f}","percent complete         \r",end="")
    end_time = time.time()
    print(f"\nTask took {(end_time-start_time):.3f} seconds")