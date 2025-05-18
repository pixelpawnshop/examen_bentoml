import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import bentoml
import joblib
import os

# Load the training data
def load_data():
    data_path = os.path.join('data', 'processed')
    X_train = pd.read_csv(os.path.join(data_path, 'X_train.csv'))
    y_train = pd.read_csv(os.path.join(data_path, 'y_train.csv'))
    return X_train, y_train

# Train the regression model
def train_model(X_train, y_train):
    model = LinearRegression()
    model.fit(X_train, y_train)
    return model

# Evaluate the model performance
def evaluate_model(model, X_train, y_train):
    y_pred = model.predict(X_train)
    r2 = r2_score(y_train, y_pred)
    rmse = mean_squared_error(y_train, y_pred, squared=False)
    mae = mean_absolute_error(y_train, y_pred)
    return r2, rmse, mae

# Save the model to BentoML Model Store
def save_model(model):
    bentoml.sklearn.save_model("admissions_model", model)

if __name__ == "__main__":
    X_train, y_train = load_data()
    model = train_model(X_train, y_train)
    r2, rmse, mae = evaluate_model(model, X_train, y_train)
    
    print(f"Model Performance:\nR2: {r2}\nRMSE: {rmse}\nMAE: {mae}")
    
    save_model(model)