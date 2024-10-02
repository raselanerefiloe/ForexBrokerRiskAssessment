import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib

# Load the data
data = pd.read_csv('brokers_data.csv')

# Preprocess data
data['Regulation Status'] = data['Regulation Status'].map({'YES': 1, 'No': 0})
data['Rating'] = pd.to_numeric(data['Rating'], errors='coerce').fillna(0)

# Encode the regulation details
le = LabelEncoder()
data['Regulation Details'] = le.fit_transform(data['Regulation Details'].astype(str))

# Select features for clustering
features = data[['Regulation Status', 'Regulation Details', 'Rating']]

# Normalize the features
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)

# Apply K-means
kmeans = KMeans(n_clusters=2, random_state=42)
data['Risk Category'] = kmeans.fit_predict(features_scaled)

# Interpret clusters
# Assuming cluster 0 is low risk and cluster 1 is high risk based on analysis
data['Risk Level'] = data['Risk Category'].map({0: 'Low Risk', 1: 'High Risk'})

# Display the results
print(data[['Name', 'Link', 'Rating', 'Risk Level']])

# Save the model, scaler, and label encoder with .joblib extension
joblib.dump(kmeans, 'kmeans_model.joblib')
joblib.dump(scaler, 'scaler.joblib')
joblib.dump(le, 'label_encoder.joblib')

print("Model, scaler, and label encoder saved successfully with .joblib extension.")
