import numpy as np
import cv2 
from flask import Flask, request, jsonify, render_template

from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired
from model import pred



# Create flask app
flask_app = Flask(__name__)
# model = pickle.load(open("model.pkl", "rb"))
flask_app.config['SECRET_KEY'] = 'supersecretkey'
flask_app.config['UPLOAD_FOLDER'] = 'static/files'

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")

@flask_app.route("/", methods = ['GET',"POST"])
def Home():
    form = UploadFileForm()
    return render_template("index.html",form=form)



@flask_app.route("/predict", methods = ['GET',"POST"])
def predict():
   



    form = UploadFileForm()
    print("aata")
    if form.validate_on_submit():
        
        file = form.file.data 
       
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),flask_app.config['UPLOAD_FOLDER'],secure_filename(file.filename))) # Then save the file
        return "File has been uploaded."
    prediction = "C C CHARU"
    return render_template("index.html", form=form, prediction_text = "The predicted car number is {}".format(prediction))
   



if __name__ == "__main__":
    flask_app.run(debug=True)