from flask import Flask, render_template, send_from_directory, request, jsonify
import os
import numpy as np
import json
import sys
import cPickle as pickle
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
import requests

app = Flask(__name__)

@app.endpoint('model.endpoint')

def load_model(filename):
    with open(filename) as f:
        model = pickle.load(f)
    return model

def race_dir_button():
    '''When clicked, allows for model stats to pop up for the DNS model'''
    ##May just bypass the pickled model for this one and just pop up the model
    ##statistics calculated by the holdout data and just return the numeric values

    ##If time allows, have a dropdown to show the results of the BB100 hold out test
    # #DNS_model.predict_proba()
    # AUC_score = ''
    # accuracy_score = '0.956'
    # accurate_show = 'Successfully predicted 3015 out of 3016 runners who showed'
    predict = '<p class=\'text-center\'>AUC score: 0.681 Accuracy score:0.956</p><p class=\'text-center\'>Successfully predicted 3015 out of 3016 runners who showed.</p>'
    #return jsonify(predict) ##return when button clicked
    return predict

#
# def parse_athlete_json(answer_list):
#     '''Takes answers from form on app and makes list for entry into DNF modeling'''
# ##button entries include age, gender, and race
# ##extrapolate from race: Season, Metro_area, WL_SO, Entry_fee, PPM
# ##gender/age group averages for: runner_rank, Age_Rank, Gender_Rank, Success_rate, Total_races
#     '''Need to change reader from list to numpy array'''
#     pass

def Gender_F(gender):
    '''Takes M/F entry in json form from webapp and converts returns 0/1'''

    if gender == 'Male':
        Gender_F = 0.
    else:
        Gender_F = 1.
    return Gender_F

def race_factors(race):
    '''Takes race from dropdown on webapp in json form and returns dataframe
    with race-specific modeling parameters'''

    if race == 'Bear 100':
        race_features = {'Season': [3], 'Metro_area': [0], 'WL_SO': [1], 'Entry_fee': [1], 'PPM': [2.5]}
    elif race == 'Black Canyon 100k':
        race_features = {'Season': [4], 'Metro_area': [1], 'WL_SO': [0], 'Entry_fee': [0], 'PPM': [2.5]}
    elif race == 'Canyons 100k':
        race_features = {'Season': [1], 'Metro_area': [1], 'WL_SO': [1], 'Entry_fee': [1], 'PPM': [3.2]}
    elif race == 'Eastern States 100':
        race_features = {'Season': [2], 'Metro_area': [0], 'WL_SO': [0], 'Entry_fee': [0], 'PPM': [1.85]}
    elif race == 'FatDog 120':
        race_features = {'Season': [2], 'Metro_area': [0], 'WL_SO': [1], 'Entry_fee': [1], 'PPM': [2.7]}
    elif race == 'Javelina Jundred':
        race_features = {'Season': [3], 'Metro_area': [1], 'WL_SO': [0], 'Entry_fee': [1], 'PPM': [2.65]}
    elif race == 'San Diego 100':
        race_features = {'Season': [2], 'Metro_area': [1], 'WL_SO': [1], 'Entry_fee': [1], 'PPM': [2.65]}
    elif race == "Sean O'Brien 100k":
        race_features = {'Season': [4], 'Metro_area': [1], 'WL_SO': [0], 'Entry_fee': [0], 'PPM': [2.5]}
    elif race == 'Tahoe Rim Trail 100':
        race_features = {'Season': [2], 'Metro_area': [1], 'WL_SO': [1], 'Entry_fee': [1], 'PPM': [2.75]}
    elif race == 'Western States 100':
        race_features = {'Season': [2], 'Metro_area': [1], 'WL_SO': [1], 'Entry_fee': [1], 'PPM': [4.1]}
    elif race == 'Zion 100':
        race_features = {'Season': [1], 'Metro_area': [1], 'WL_SO': [1], 'Entry_fee': [1], 'PPM': [2.5]}
    elif race == 'Georgia Death Race':
        race_features = {'Season': [1], 'Metro_area': [1], 'WL_SO': [1], 'Entry_fee': [1], 'PPM': [3.16]}
    race_factors = pd.DataFrame(race_features)
    return race_factors

def age_factors(age):
    '''Takes in numeric age from webapp form and evaluates and populates age-specific
    features for the athlete. Outputs dataframe.'''
    try:
        age = int(age)
    except ValueError:
        print("Age is but a number, dude!")

    if age < 20:
        age_features = {'Age': [age], 'runner_rank': [70.3851], 'Age_Rank': [0.7538], \
        'Gender_Rank': [0.6842], 'Success_rate': [0.900], 'Total_races': [11.515]}
    elif age >= 20 and age < 30:
        age_features = {'Age': [age], 'runner_rank': [74.5336], 'Age_Rank': [0.7254], \
        'Gender_Rank': [0.6560], 'Success_rate': [0.8798], 'Total_races': [10.286]}
    elif age >= 30 and age < 40:
        age_features = {'Age': [age], 'runner_rank': [72.3374], 'Age_Rank': [0.7319], \
        'Gender_Rank': [0.6689], 'Success_rate': [0.8867], 'Total_races': [11.352]}
    elif age >= 40 and age < 50:
        age_features = {'Age': [age], 'runner_rank': [69.9372], 'Age_Rank': [0.7308], \
        'Gender_Rank': [0.6668], 'Success_rate': [0.8753], 'Total_races': [11.191]}
    elif age >= 50 and age < 60:
        age_features = {'Age': [age], 'runner_rank': [66.6021], 'Age_Rank': [0.7339], \
        'Gender_Rank': [0.6733], 'Success_rate': [0.8837], 'Total_races': [11.092]}
    elif age >= 60 and age < 70:
        age_features = {'Age': [age], 'runner_rank': [61.5856], 'Age_Rank': [0.7213], \
        'Gender_Rank': [0.6683], 'Success_rate': [0.8721], 'Total_races': [10.311]}
    elif age >= 70:
        age_features = {'Age': [age], 'runner_rank': [58.3583], 'Age_Rank': [0.7308], \
        'Gender_Rank': [0.6395], 'Success_rate': [0.8579], 'Total_races': [10.080]}
    age_factors = pd.DataFrame(age_features)
    return age_factors

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/images/<path:path>', methods=['GET'])
def send_image(path):
    return send_from_directory('images', path)

@app.route('/lib/<path:path>', methods=['GET'])
def send_file(path):
    return send_from_directory('lib', path)

@app.route('/athlete_proba', methods=['POST'])
def Finish_proba():
    #data = json.loads(request.data)
    request_df = pd.read_json(request.data)
    age, gender, race = (request_df['value'][0],
                                      request_df['value'][1],
                                      request_df['value'][2])
    age_f = age_factors(age)
    gender_f = Gender_F(gender)
    race_f = race_factors(race)

    answer_list = [age, age_f['runner_rank'], race_f['Season'], \
    race_f['Metro_area'], race_f['WL_SO'], race_f['Entry_fee'], \
    race_f['PPM'], age_f['Age_Rank'], age_f['Gender_Rank'], \
    age_f['Total_races'], age_f['Success_rate'], gender_f]

    probas = Finish_model.predict_proba(answer_list)
    finish_proba = (probas[0][1]) * 100.
    round_prob = "%.2f" % finish_proba
    statement = '<p class=\'text-center\'>How cool?!? You have a ' + round_prob + '%'+' chance of finishing ' \
    + race + '.</p>' + \
    '<p class=\'text-center\'>For Entertainment Purposes Only: You are a badass even for making it to the start!</p>'
    #return jsonify(statement) ##returns the numeric probability of success for selected race
    return statement

@app.route('/race_director', methods=['POST'])
def DNS_stats():
    return race_dir_button()

#@app.route('/blog', methods=['GET'])
#def index():
#    return render_template('blog.html')



if __name__ == '__main__':
    #filename = '../model/DNS_model.pkl'
    filename2 = 'model/Finish_model.pkl'
    #DNS_model = load_model(filename)
    Finish_model = load_model(filename2)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
