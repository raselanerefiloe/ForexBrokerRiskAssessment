from flask import Flask, render_template, send_file
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend
import matplotlib.pyplot as plt

import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import silhouette_score
from joblib import dump, load
import os

app = Flask(__name__)

# Load the saved KMeans model, scaler, and label encoder
kmeans = load('model.joblib')  # Load the KMeans model
scaler = load('scaler.joblib')  # Load the scaler used for training
le = load('label_encoder.joblib')  # Load the label encoder used for training


# Preprocess and predict using the loaded model
def preprocess_and_predict(data):
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

    return data, features_scaled


@app.route('/')
def brokers():
    # Load new data (the broker data you want to display)
    brokers_data = pd.read_csv('brokers_data.csv')

    # Preprocess the data and predict risk levels
    brokers_data, _ = preprocess_and_predict(brokers_data)

    # Pass data to the template for rendering
    return render_template(
        'brokers.html',
        brokers=brokers_data[['Name', 'Link', 'Rating', 'Regulation Status', 'Risk Level']].to_dict(orient='records'),
    )


@app.route('/performance')
def performance():
    # Load new data (the broker data you want to include in the report)
    brokers_data = pd.read_csv('brokers_data.csv')

    # Preprocess the data and predict risk levels
    brokers_data, features_scaled = preprocess_and_predict(brokers_data)

    # Calculate performance metrics
    inertia = kmeans.inertia_
    silhouette_avg = silhouette_score(features_scaled, brokers_data['Risk Category'])

    # Create a performance report DataFrame
    performance_report = pd.DataFrame({
        'Metric': ['Inertia', 'Silhouette Score'],
        'Value': [inertia, silhouette_avg]
    })

    # Save the performance visualizations
    save_performance_visualizations(features_scaled)

    # Render performance report
    return render_template('performance.html', performance=performance_report.to_dict(orient='records'))


def save_performance_visualizations(features_scaled):
    inertia_values = []
    silhouette_scores = []
    K = range(2, 10)

    for k in K:
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(features_scaled)
        inertia_values.append(kmeans.inertia_)
        silhouette_scores.append(silhouette_score(features_scaled, kmeans.labels_))

    # Plotting Inertia
    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.plot(K, inertia_values, 'bo-')
    plt.title('Elbow Method: Inertia')
    plt.xlabel('Number of Clusters')
    plt.ylabel('Inertia')
    plt.grid()

    # Save the inertia plot
    inertia_plot_path = 'static/inertia_plot.png'
    plt.savefig(inertia_plot_path)
    plt.close()  # Close the figure to avoid display issues

    plt.subplot(1, 2, 2)
    plt.plot(K, silhouette_scores, 'ro-')
    plt.title('Silhouette Scores for Different k')
    plt.xlabel('Number of Clusters')
    plt.ylabel('Silhouette Score')
    plt.grid()

    # Save the silhouette plot
    silhouette_plot_path = 'static/silhouette_plot.png'
    plt.savefig(silhouette_plot_path)
    plt.close()  # Close the figure to avoid display issues

    return inertia_plot_path, silhouette_plot_path


if __name__ == '__main__':
    app.run(debug=True)
