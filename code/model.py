import pandas as pd
import numpy as np
from tensorflow.python.keras.models import Model
from tensorflow.python.keras.layers import Input, Conv2D, Dense, Flatten, concatenate
from sklearn.model_selection import train_test_split

## Loading  #############################################################################
#########################################################################################

#load context and spatial data
df_context = pd.read_csv('data/processed/final_tracking_week_1_context.csv')
df_spatial = pd.read_csv('data/processed/final_tracking_week_1_spatial.csv')

#ensure the data is aligned on unique identifiers
df = df_context.merge(df_spatial, on=['gameId', 'playId', 'nflId', 'frameType', 'club', 'week'])

#extract the target variable
y = df['expectedPointsAdded']

#drop the target from context features
X_context = df_context.drop(columns=['expectedPointsAdded'])

#prepare spatial features
#assuming the spatial data needs to be reshaped into (frames, grid_x, grid_y, channels)
X_spatial = df_spatial[['x', 'y', 's', 'a', 'dis', 'o', 'dir']].values

#reshape spatial features to (samples, 1, 1, 7) for simplicity
#update this shape based on your actual spatial data requirements
X_spatial = X_spatial.reshape((X_spatial.shape[0], 1, 1, 7))

#train-test split
X_context_train, X_context_test, X_spatial_train, X_spatial_test, y_train, y_test = train_test_split(
    X_context, X_spatial, y, test_size=0.2, random_state=42
)

## Define CNN Model #############################################################################
#################################################################################################

#spatial input
spatial_input = Input(shape=(1, 1, 7), name='spatial_input')
x_spatial = Conv2D(16, (1, 1), activation='relu')(spatial_input)
x_spatial = Flatten()(x_spatial)

#context input
context_input = Input(shape=(X_context.shape[1],), name='context_input')
x_context = Dense(64, activation='relu')(context_input)

#combine spatial and context features
combined = concatenate([x_spatial, x_context])

#output layer
output = Dense(1, activation='linear', name='output')(combined)

#create and compile model
model = Model(inputs=[spatial_input, context_input], outputs=output)
model.compile(optimizer='adam', loss='mse', metrics=['mae'])

#model summary
model.summary()

## Train the Model ##############################################################################
#################################################################################################

history = model.fit(
    [X_spatial_train, X_context_train],
    y_train,
    validation_data=([X_spatial_test, X_context_test], y_test),
    epochs=20,
    batch_size=32
)
