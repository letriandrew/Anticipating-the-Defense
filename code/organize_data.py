## GLOBAL #######################################################################################
#################################################################################################
import math
import pandas as pd
from pathlib import Path
import sys
import os
import time
from sklearn.preprocessing import MinMaxScaler

## INIT #########################################################################################
#################################################################################################
# adding to path
abs_path = str(Path(__file__).parent.parent)
sys.path.insert(0, abs_path)

week_path = abs_path + '/data/processed/'

## FUNCTIONS ####################################################################################
#################################################################################################

def organize_week(week_file):
    with open(week_file, 'r') as file:
        file_name = "organized_" + str(os.path.basename(week_file))

        tracking_pd = pd.read_csv(file)

        #normalize the 'x' and 'y' columns
        scaler = MinMaxScaler(feature_range=(0, 1))
        tracking_pd[['x', 'y']] = scaler.fit_transform(tracking_pd[['x', 'y']])

        col_list = list(tracking_pd)
        col_list[2], col_list[3] = col_list[3], col_list[2]
        tracking_pd = tracking_pd.reindex(columns=col_list)
        tracking_pd = tracking_pd.sort_values(by=['gameId','playId','frameId'])
        tracking_pd.to_csv(f'{week_path}{file_name}', index=False)

## MAiN #########################################################################################
#################################################################################################
if __name__ == '__main__':
    print(f"Iterating over {week_path} tracking files")
    length = 0
    start_time = time.time()

    if os.path.exists(week_path):
        lst = os.listdir(week_path)
        length = len(lst)
        print(f"Total of {length} weeks to iterate")
        idx = 0
        try:
            for filename in lst:
                print(f"{idx}/{length}",f"{idx/length*100:.3f}","percent complete         \r",end="")
                f = os.path.join(week_path, filename)
                
                organize_week(f)
                idx +=1

        except Exception as error:
            print()
            print("Program crashed while reading:", error)
            exit()
    else:
        print(f"Path ({week_path}) does not exist...")
    
    print(f"{length}/{length}",f"{length/length*100:.3f}","percent complete         \r",end="")
    end_time = time.time()
    print(f"\nTask took {(end_time-start_time):.3f} seconds")