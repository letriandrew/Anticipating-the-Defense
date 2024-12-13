import pandas as pd
import numpy as np
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Conv2D, Dense, Flatten, concatenate
from sklearn.model_selection import train_test_split

## Loading ######################################################################################
#################################################################################################

#load context and spatial data
try:
    df_context = pd.read_csv('data/processed/final_tracking_week_1_context.csv')
    df_spatial = pd.read_csv('data/processed/final_tracking_week_1_spatial.csv')
except FileNotFoundError:
    print("Data files not found. Please run features.py first.")
    exit()

#ensure the data is aligned on unique identifiers
df = df_context.merge(df_spatial, on=['gameId', 'playId', 'nflId', 'frameId'])

#extract the target variable
if 'expectedPointsAdded' not in df_context.columns:
    raise ValueError("Target column 'expectedPointsAdded' not found in context data.")

y = df['expectedPointsAdded']

#drop the target from context features
X_context = df_context.drop(columns=['expectedPointsAdded'])

#prepare spatial features
X_spatial = df_spatial[['x', 'y', 's', 'a', 'dis', 'o', 'dir']].values

#reshape spatial features dynamically
num_spatial_features = len(['x', 'y', 's', 'a', 'dis', 'o', 'dir'])
X_spatial = X_spatial.reshape((X_spatial.shape[0], 1, 1, num_spatial_features))

#train-test split
X_context_train, X_context_test, X_spatial_train, X_spatial_test, y_train, y_test = train_test_split(
    X_context, X_spatial, y, test_size=0.2, random_state=42
)

#check for NaN values in X_context_train
nan_context = X_context_train.isna().any()
if nan_context.any():
    print("NaN values found in the following context columns:")
    print(nan_context[nan_context].index.tolist())

#check for NaN values in y_train
nan_y = y_train.isna()
if nan_y.any():
    print("NaN values found in the target variable y_train.")

#check for NaN values in X_spatial_train
nan_spatial = np.isnan(X_spatial_train)
if nan_spatial.any():
    print(f"NaN values found in X_spatial_train at positions: {np.argwhere(nan_spatial)}")

#stop execution if NaN values are found
if nan_context.any() or nan_y.any() or nan_spatial.any():
    raise ValueError("NaN values found in the data. Please check the output above for details.")


## Define CNN Model #############################################################################
#################################################################################################

#spatial input
spatial_input = Input(shape=(1, 1, num_spatial_features), name='spatial_input')
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
    epochs=5,  # Reduced from 20 for faster testing
    batch_size=8  # Reduced from 32
)
