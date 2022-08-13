import numpy as np
from flask import Flask, request, jsonify, render_template
# import pickle

# Create flask app
flask_app = Flask(__name__)
# model = pickle.load(open("model.pkl", "rb"))

@flask_app.route("/")
def Home():
    return render_template("index.html")


@flask_app.route("/predict", methods = ["POST"])
def predict():
    print("Cool cool")
    prediction = "C C CHARU"
    return render_template("index.html", prediction_text = "The predicted car number is {}".format(prediction))

if __name__ == "__main__":
    flask_app.run(debug=True)