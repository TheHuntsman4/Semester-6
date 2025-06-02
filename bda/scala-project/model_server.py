from flask import Flask, request, jsonify
import pickle
import numpy as np

app = Flask(__name__)

# Load the Random Forest model from pickle file
try:
    with open('model.pkl', 'rb') as file:
        model = pickle.load(file)
except FileNotFoundError:
    print("Error: model.pkl file not found in the current directory")
    exit(1)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get the data from POST request
        data = request.get_json()
        print(f"Received request data: {data}")
        
        # Convert input data to numpy array
        features = np.array(data['features']).reshape(1, -1)
        print(f"Features shape: {features.shape}")
        
        # Make prediction
        prediction = model.predict(features).tolist()
        print(f"Prediction: {prediction}")
        
        response = {
            'status': 'success',
            'prediction': prediction[0]
        }
        print(f"Sending response: {response}")
        return jsonify(response)
    
    except Exception as e:
        error_response = {
            'status': 'error',
            'message': str(e)
        }
        print(f"Error occurred: {str(e)}")
        return jsonify(error_response), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 