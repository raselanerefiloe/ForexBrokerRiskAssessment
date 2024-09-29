from flask import Flask, render_template
import pandas as pd
from joblib import load

app = Flask(__name__)

# Load the saved KMeans model, scaler, and label encoder
kmeans = load('model.joblib')  # Load the KMeans model
scaler = load('scaler.joblib')  # Load the scaler used for training
le = load('label_encoder.joblib')  # Load the label encoder used for training


# Preprocess and predict using the loaded model
def preprocess_and_predict(data):
    # Preprocess data in the same way as during training
    data['Regulation Status'] = data['Regulation Status'].map({'YES': 1, 'No': 0})
    data['Rating'] = pd.to_numeric(data['Rating'], errors='coerce').fillna(0)

    # Encode the regulation details using the loaded LabelEncoder
    data['Regulation Details'] = le.transform(data['Regulation Details'].astype(str))

    # Select features for clustering
    features = data[['Regulation Status', 'Regulation Details', 'Rating']]

    # Normalize the features using the loaded scaler
    features_scaled = scaler.transform(features)

    # Predict risk categories using the loaded KMeans model
    data['Risk Category'] = kmeans.predict(features_scaled)

    # Map risk categories to risk levels
    data['Risk Level'] = data['Risk Category'].map({0: 'Low Risk', 1: 'High Risk'})

    return data


@app.route('/')
def brokers():
    # Load new data (the broker data you want to display)
    brokers_data = pd.read_csv('brokers_data.csv')

    # Preprocess the data and predict risk levels
    brokers_data = preprocess_and_predict(brokers_data)

    # Pass data to the template for rendering
    return render_template(
        'brokers.html',
        brokers=brokers_data[['Name', 'Link', 'Rating', 'Regulation Status', 'Risk Level']].to_dict(orient='records')
    )


if __name__ == '__main__':
    app.run(debug=True)
