import numpy as np
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
from sklearn.ensemble import RandomForestClassifier
import pickle
from pymongo import MongoClient
from datetime import datetime

# Initialize the Flask application
app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['crop_recommendation']
forum_posts_collection = db['forum_posts']

# Load the trained model (assuming it's saved as 'model.pkl')
with open('model.pkl', 'rb') as model_file:
    model = pickle.load(model_file)

# Route to display the index page with the form
@app.route('/')
def index():
    # Fetch all forum posts from the MongoDB collection
    posts = forum_posts_collection.find().sort('created_at', -1)  # Sort by creation date
    return render_template('index.html', posts=posts)

@app.route('/farming-practices')
def farming_practices():
    return render_template('farming-practices.html')

# Route to handle form submission and prediction
@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        # Extracting the input features from the form
        N = float(request.form['Nitrogen'])
        P = float(request.form['Phosphorus'])
        K = float(request.form['Potassium'])
        temp = float(request.form['Temperature'])
        humidity = float(request.form['Humidity'])
        ph = float(request.form['Ph'])
        rainfall = float(request.form['Rainfall'])
        
        # Combine these features into a list
        input_features = [N, P, K, temp, humidity, ph, rainfall]
        
        # Convert the input features to a numpy array and reshape for prediction
        input_features = np.array(input_features).reshape(1, -1)

        # Make the prediction using the loaded model
        prediction = model.predict(input_features)
        
        # Return the prediction result as a string
        return render_template('index.html', prediction_text=f'The best crop for the given input is: {prediction[0]}')

# Route to handle posting a new forum post
@app.route('/post', methods=['POST'])
def post():
    if request.method == 'POST':
        # Extracting the data from the form
        title = request.form['title']
        content = request.form['content']
        created_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        
        # Create a new forum post document
        new_post = {
            'title': title,
            'content': content,
            'comments': [],
            'created_at': created_at
        }

        # Insert the post into the MongoDB collection
        forum_posts_collection.insert_one(new_post)
        
        # Redirect back to the home page to display the updated posts
        return redirect(url_for('index'))

# Route to add a comment to a post
@app.route('/add_comment/<post_id>', methods=['POST'])
def add_comment(post_id):
    if request.method == 'POST':
        # Extract comment from the form
        comment = request.form['comment']
        
        # Find the post by ID and add the comment to the post's 'comments' list
        forum_posts_collection.update_one(
            {'_id': post_id},
            {'$push': {'comments': {'comment': comment, 'created_at': datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}}}
        )
        
        # Redirect to the homepage after adding the comment
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
