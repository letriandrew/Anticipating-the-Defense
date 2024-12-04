import math

# height and width of a football field, x2, rounded up. total space 240 * 107 = 25,680
h = 120 * 2
w = math.ceil(53.3 * 2)

def create_grid():
    arr = [[[0]* h]*w]
    return arr

# do it per frame, per game, per week
# 1/-1 on based on team
# since scaled by 2, 2 players can occupy the same spot (x1,y1) = (x2,y2) ~= (x_1, y_1) = (x_1+1, y_1+1)

# additionally, combine games with plays.csv homeTeamWinProbabilityAdded, visitorTeamWinProbilityAdded