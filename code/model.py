import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.callbacks import EarlyStopping
from keras.metrics import AUC, Accuracy, Precision, Recall
from tensorflow.keras.regularizers import l2
import tensorflow as tf

## Loading ######################################################################################
#################################################################################################

#load context and spatial data
# Initialize an empty list to store dataframes
all_data = []

# Iterate through weeks 1 to 9 and load the data
for week in range(1, 10):
    file_path = f'data/processed/final_tracking_week_{week}_aggregated.csv'
    data = pd.read_csv(file_path)
    all_data.append(data)

# Concatenate all the dataframes into one
data = pd.concat(all_data, ignore_index=True)

# Parse the sequences from strings to arrays
def parse_sequence(seq_str):
    try:
        parsed = eval(seq_str)
        # Ensure that each inner list has 3 elements (nflId, x, y)
        return [inner if len(inner) == 3 else [0, 0, 0] for inner in parsed]  # Adjust as necessary
    except Exception as e:
        print(f"Error parsing sequence: {seq_str}, Error: {e}")
        raise e

data['sequence_parsed'] = data['sequence'].apply(parse_sequence)

# Extract sequences and normalize
sequences = data['sequence_parsed'].tolist()

# Get max sequence length
max_length = max(len(seq) for seq in sequences)

# Pad the sequences to make them uniform in length
padded_sequences = pad_sequences(
    sequences, padding='post', dtype='int32', value=-1, maxlen=max_length
)

## Define RNN Model #############################################################################
#################################################################################################

# Prepare target variables
gaps = ['right_c', 'right_b', 'right_a', 'left_a', 'left_b', 'left_c']
label_encoders = [LabelEncoder() for _ in gaps]
one_hot_encoders = [OneHotEncoder(sparse_output=False) for _ in gaps]

categorical_targets = []
for i, gap in enumerate(gaps):
    # Encode the gap targets
    encoded = label_encoders[i].fit_transform(data[gap])
    one_hot = one_hot_encoders[i].fit_transform(encoded.reshape(-1, 1))
    categorical_targets.append(one_hot)

# Align input and targets for train-test split
X = padded_sequences
y_dict = {gaps[i]: categorical_targets[i] for i in range(len(gaps))}

# Train-test split for each gap
X_train, X_test, y_train_dict, y_test_dict = {}, {}, {}, {}
for gap in gaps:
    X_train[gap], X_test[gap], y_train_dict[gap], y_test_dict[gap] = train_test_split(
        X, y_dict[gap], test_size=0.2, random_state=42
    )

# Combine the splits for training and testing
X_train_combined = X_train[gaps[0]]  # Same X for all gaps
X_test_combined = X_test[gaps[0]]  # Same X for all gaps
y_train_combined = {gap: y_train_dict[gap] for gap in gaps}
y_test_combined = {gap: y_test_dict[gap] for gap in gaps}

# Define the RNN model with multiple outputs and additional tuning
input_layer = Input(shape=(max_length, 3))  # Input shape includes nflId, x, y
x = LSTM(256, return_sequences=True, kernel_regularizer=l2(0.001))(input_layer)  # Increased LSTM units and added L2 regularization
x = Dropout(0.2)(x)  # Increased dropout
x = LSTM(64, return_sequences=True)(x)  # Increased second LSTM units
x = Dropout(0.5)(x)  # Increased dropout
x = LSTM(32)(x)  # Increased third LSTM units
x = Dropout(0.5)(x)  # Increased dropout

# Create separate outputs for each gap
outputs = [Dense(len(label_encoders[i].classes_), activation='softmax', name=gaps[i])(x) for i in range(len(gaps))]

# Define a list of metrics, one for each output
metrics = [
    AUC(name='right_a_auc'),
    AUC(name='right_b_auc'),
    AUC(name='right_c_auc'),
    AUC(name='left_a_auc'),
    AUC(name='left_b_auc'),
    AUC(name='left_c_auc'),
]

# Define learning rate scheduler
initial_lr = 0.001
lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(
    initial_lr, decay_steps=100000, decay_rate=0.96, staircase=True
)
optimizer = Adam(learning_rate=lr_schedule)

# Define the model
model = Model(inputs=input_layer, outputs=outputs)
model.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=metrics)

# Early stopping to prevent overfitting
early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

## Train the Model ##############################################################################
#################################################################################################

# Train the model
history = model.fit(
    X_train_combined,
    [y_train_combined[gap] for gap in gaps],  # Multiple outputs
    validation_data=(X_test_combined, [y_test_combined[gap] for gap in gaps]),
    epochs=100,
    batch_size=32,
    callbacks=[early_stopping]
)

## Evaluate the Model ###########################################################################
#################################################################################################

# Evaluate the model
evaluation = model.evaluate(
    X_test_combined,
    [y_test_combined[gap] for gap in gaps]
)
print("Evaluation Results:", evaluation)

# Example predictions
predictions = model.predict(X_test_combined)
for i, gap in enumerate(gaps):
    print(f"Predictions for {gap}:")
    print(predictions[i])

print(model.summary())