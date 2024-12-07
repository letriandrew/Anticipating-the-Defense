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

# read csv and join
games = pd.read_csv(abs_path+'/data/games.csv')
players = pd.read_csv(abs_path+'/data/players.csv').drop("displayName",axis=1)
plays = pd.read_csv(abs_path+'/data/plays.csv')
player_play = pd.read_csv(abs_path+'/data/player_play.csv') #play metadata


week1 = pd.read_csv(abs_path+'/data/processed/final_tracking_week_1.csv')
# Filter plays to only include gameId values that are in week1
plays_filtered_gameId = plays[plays['gameId'].isin(week1['gameId'])]
plays_f = pd.merge(games, plays_filtered_gameId, how="inner", on="gameId")

gameid_playid_arr = []
for idx in range (0, len(plays_f["gameId"])):
    gameid_playid_arr.append([int(plays_f["gameId"][idx]), int(plays_f["playId"][idx])])

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

def store_play(games,tracking_df,play_df,players,gameId,playId, idx):
    tracking_players_df = pd.merge(tracking_df,players,how="left",on = "nflId")
    selected_tracking_df = tracking_players_df[(tracking_players_df.playId==playId)&(tracking_players_df.gameId==gameId)].copy()

    sorted_frame_list = selected_tracking_df.frameId.unique()
    sorted_frame_list.sort()

    frames = []
    for frameId in sorted_frame_list:
        position_occupied_grid = create_grid()   # denotes if space is occupied, 0/1
        home_team_density_grid = create_grid()  # denotes numeric value of home team per cell
        away_team_density_grid = create_grid()  # denotes numeric value of away team per cell
        # TODO unsure if home team and away team are calculated properly
        t_dict = {}
        i = 1
        try:
            for team in selected_tracking_df.club.unique():
                plot_df = selected_tracking_df[(selected_tracking_df.club==team)&(selected_tracking_df.frameId==frameId)].copy()
                if team != "football":
                    if team not in t_dict:
                        t_dict[team] = i
                        i = -1 # away team flag
                    # organizing into points of (x,y)
                    x = plot_df["x"] # x-coords of all team A at frame B
                    y = plot_df["y"] # y-coords of all team A at frame B
                    for x1,y1 in zip(x,y):
                        x_arr = math.ceil(x1)
                        y_arr = math.ceil(y1)

                        position_occupied_grid[x_arr][y_arr] = 1
                        if t_dict[team] == 1: # home team
                            home_team_density_grid[x_arr][y_arr] += 1
                        else:
                            away_team_density_grid[x_arr][y_arr] += 1
            
            frames.append([position_occupied_grid, home_team_density_grid, away_team_density_grid])
        except Exception as error:
            print("An error has occured:", error)
            print("arr_maxX=", len(position_occupied_grid))
            print("arr_ymax=", len(position_occupied_grid[0]))
            print("x_arr=",x_arr)
            print("y_arr=",y_arr)
            print("x1=",x1)
            print("y1=",y1)
            print("idx=",idx)
            exit()

    return frames


## MAiN #########################################################################################
#################################################################################################
if __name__ == "__main__":
    length = len(plays_f["gameId"])
    print(f"Total of {length} plays to iterate")
    start_time = time.time()
    try:
        week_string = "week1/"
        final_directory = abs_path + "/code/parsed_data/" + week_string
        if not os.path.exists(final_directory):
            os.makedirs(final_directory)

        for idx in range (0, length):
            print(f"{idx}/{length}",f"{idx/length*100:.3f}","percent complete         \r",end="")
            gameId = gameid_playid_arr[idx][0]
            playId = gameid_playid_arr[idx][1]

            output_file = final_directory + "gameId_" + str(gameId) + "_playId_" + str(playId) + ".txt"
            if os.path.isfile(output_file):
                            time.sleep(0.0001)
                            continue

            gameplay_frames = store_play(games,week1,plays,players,gameId,playId,idx)
            
            with open(output_file, "w") as txt_file:
                for grids in gameplay_frames:
                    for grid in grids:
                        for line in grid:
                            str_line = ''.join(str(x) for x in line)
                            txt_file.write(" ".join(''.join(str_line)) + "\n")
                        txt_file.write("\n")
    except Exception as error:
        print()
        print("Program crashed while printing:", error)
        exit()
    print(f"{length}/{length}",f"{length/length*100:.3f}","percent complete         \r",end="")
    end_time = time.time()
    print(f"\nTask took {(end_time-start_time):.3f} seconds")
    print(f"Completed all {length} plays")

# do it per frame, per game, per week
# 1/-1 on based on team
# since scaled by 2, 2 players can occupy the same spot (x1,y1) = (x2,y2) ~= (x_1, y_1) = (x_1+1, y_1+1)

# additionally, combine games with plays.csv homeTeamWinProbabilityAdded, visitorTeamWinProbilityAdded