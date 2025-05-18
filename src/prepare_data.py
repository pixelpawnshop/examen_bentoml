import pandas as pd
from sklearn.model_selection import train_test_split

def load_data(file_path):
    data = pd.read_csv(file_path)
    return data

def clean_data(data):
    # Drop any rows with missing values
    data = data.dropna()
    # Drop unnecessary columns if any (modify as needed)
    data = data.drop(columns=['Serial No.'], axis=1)
    
    # Strip whitespace from column names
    data.columns = data.columns.str.strip()
    return data

def split_data(data):
    X = data.drop(columns=['Chance of Admit'], axis=1)
    y = data['Chance of Admit']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    return X_train, X_test, y_train, y_test

def main():
    # Load the data
    data = load_data('./data/raw/admission.csv')
    # Clean the data
    cleaned_data = clean_data(data)
    # Split the data
    X_train, X_test, y_train, y_test = split_data(cleaned_data)
    
    # Save the processed data
    X_train.to_csv('data/processed/X_train.csv', index=False)
    X_test.to_csv('data/processed/X_test.csv', index=False)
    y_train.to_csv('data/processed/y_train.csv', index=False)
    y_test.to_csv('data/processed/y_test.csv', index=False)

if __name__ == "__main__":
    main()