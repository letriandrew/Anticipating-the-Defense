"""
A script that animates tracking data, given gameId and playId. 
Players can be identified by mousing over the individuals dots. 
The play description is also displayed at the bottom of the plot, 
together with play information at the top of the plot. 

Data should be stored in a dir named data, in the same dir as this script. 

Original Source: https://www.kaggle.com/code/huntingdata11/animated-and-interactive-nfl-plays-in-plotly/notebook
"""


import plotly.graph_objects as go
import pandas as pd
import numpy as np

# read csv and join
games = pd.read_csv('../data/games.csv')
players = pd.read_csv('../data/players.csv')
plays = pd.read_csv('../data/plays.csv')
player_play = pd.read_csv('../data/player_play.csv') #play metadata
week1 = pd.read_csv('../data/tracking_week_1.csv')
week2 = pd.read_csv('../data/tracking_week_2.csv')
week3 = pd.read_csv('../data/tracking_week_3.csv')
week4 = pd.read_csv('../data/tracking_week_4.csv')
week5 = pd.read_csv('../data/tracking_week_5.csv')
week6 = pd.read_csv('../data/tracking_week_6.csv')
week7 = pd.read_csv('../data/tracking_week_7.csv')
week8 = pd.read_csv('../data/tracking_week_8.csv')
week9 = pd.read_csv('../data/tracking_week_9.csv')

weeks = [week1, week2, week3, week4, week5, week6, week7, week8, week9]

joined_all = pd.merge(games,plays,how="inner",on = "gameId")

"""
THE BELOW CODE DOESN'T WORK

I was going to try to merge all plays from all weeks into one but saw that there exists identical play id's -- will create a future function to solve this issue

for week in weeks:
    joined_all = pd.merge(joined_all, week,how="inner",on=["gameId", "playId"])
"""

joined_all = pd.merge(joined_all, week1,how="inner",on=["gameId", "playId"])

# left join on players to keep football records
joined_all = pd.merge(joined_all,players,how="left",on = "nflId")

# select specific playid
play_focus = 64
focused_df = joined_all[(joined_all.playId==play_focus)]


# team colors to distinguish between players on plots
colors = {
    "ARI": "#97233F",
    "ATL": "#A71930",
    "BAL": "#241773",
    "BUF": "#00338D",
    "CAR": "#0085CA",
    "CHI": "#C83803",
    "CIN": "#FB4F14",
    "CLE": "#311D00",
    "DAL": "#003594",
    "DEN": "#FB4F14",
    "DET": "#0076B6",
    "GB": "#203731",
    "HOU": "#03202F",
    "IND": "#002C5F",
    "JAX": "#9F792C",
    "KC": "#E31837",
    "LA": "#FFA300",
    "LAC": "#0080C6",
    "LV": "#000000",
    "MIA": "#008E97",
    "MIN": "#4F2683",
    "NE": "#002244",
    "NO": "#D3BC8D",
    "NYG": "#0B2265",
    "NYJ": "#125740",
    "PHI": "#004C54",
    "PIT": "#FFB612",
    "SEA": "#69BE28",
    "SF": "#AA0000",
    "TB": "#D50A0A",
    "TEN": "#4B92DB",
    "WAS": "#5A1414",
    "football": "#CBB67C"
}

