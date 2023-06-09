from flask import Flask, request
import joblib

app = Flask(__name__)

# Load the trained machine learning model
model = joblib.load('path/to/your/model.pkl')

# Define a route for serving the model
@app.route('/predict', methods=['POST'])
def predict():
    # Get the input data from the POST request
    data = request.json
    
    # Use the model to make predictions
    predictions = model.predict(data)
    
    # Return the predictions as a JSON response
    return {'predictions': predictions.tolist()}
    
# Run the app
if __name__ == '__main__':
    app.run(debug=True)
