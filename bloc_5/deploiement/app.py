from flask import Flask, request, jsonify, render_template
import numpy as np
import joblib
import os

app = Flask(__name__)

regressor = joblib.load("models/model.joblib")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    # Check if request has a JSON content
    if request.json:
    
        # Get the JSON as dictionnary
        req = request.get_json()
        # Check mandatory key
        if "input" in req.keys():
            # Predict
            data_in = req['input']
            prediction = regressor.predict(np.array(data_in).reshape(len(data_in), 11))
            # Return the result as JSON but first we need to transform the
            # result so as to be serializable by jsonify()
            return jsonify({"predict": str(prediction)}), 200
        else :
            return jsonify({"msg": "Error: not a JSON or no input key in your request"})

    return jsonify({"msg": "Error: not a JSON or no email key in your request"})

if __name__ == "__main__":
    app.run(debug=True)
