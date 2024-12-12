## GLOBAL #######################################################################################
#################################################################################################
import pandas as pd
import numpy as np
import sys
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder, LabelEncoder

## INIT #########################################################################################
#################################################################################################

numerical_categories = ['yardsToGo','preSnapHomeTeamWinProbability','preSnapVisitorTeamWinProbability','expectedPoints','yardsGained','homeTeamWinProbabilityAdded','visitorTeamWinProbilityAdded','expectedPointsAdded','timeToThrow','timeInTackleBox','timeToSack','passLength', 'yardsToEndzone']

categorical_categories = ['offenseFormation','receiverAlignment','pff_passCoverage','pff_manZone','passResult','team_side']

categorical_categories_onehot = ['passTippedAtLine','unblockedPressure', 'play_success']

unique_id = ['gameId','playId','nflId','frameType', 'club','week']


## FUNCTIONS ####################################################################################
#################################################################################################

def normalize(dataframe):

    #apply min-max scaling to numerical categories
    scaler = MinMaxScaler()
    dataframe[numerical_categories] = scaler.fit_transform(dataframe[numerical_categories])

    #one-hot encode categorical features (binary/categorical columns)
    onehot_encoder = OneHotEncoder(sparse_output=False, drop='first')  # drop='first' avoids multicollinearity
    onehot_encoded = onehot_encoder.fit_transform(dataframe[categorical_categories_onehot])
    onehot_encoded_df = pd.DataFrame(onehot_encoded, columns=onehot_encoder.get_feature_names_out(categorical_categories_onehot))
    dataframe = dataframe.drop(columns=categorical_categories_onehot)  # drop the original columns
    dataframe = pd.concat([dataframe, onehot_encoded_df], axis=1)

    #apply label encoding to ordinal/categorical features 
    label_encoder = LabelEncoder()
    for cat in categorical_categories:
        dataframe[cat] = label_encoder.fit_transform(dataframe[cat])

    return dataframe


def create_context():
    for week in range(1, 2):
        print(f"Creating {week} Context/Categorical Features")
        df = pd.read_csv(f'data/processed/final_tracking_week_{week}.csv')

        df = normalize(df)

        df.to_csv(f'data/processed/final_tracking_week_{week}_normalized.csv', index=False)
        print(f"Week {week} processed and saved.")

    

## MAIN #########################################################################################
#################################################################################################

if __name__ == "__main__":
    create_context()
