import os
from flask import Flask, render_template, request, jsonify, json
# from openai import OpenAI
# from openai_mech import send_answer
from api1 import call_url


app = Flask(__name__)


@app.post("/save_url")
def save_url():
    dataframes = call_url("done")
    if dataframes:
    # Access DataFrames using the table names as keys
        personal_df = dataframes.get('Personal Data')
        address_df = dataframes.get('Address Data')
        education_df = dataframes.get('Education Data')
    message = {"answer": dataframes}
    return jsonify(message)


@app.post("/get_id")
def get_id():
    ass_id = request.get_json().get("code")
    with open('assistant_key.json', 'r') as file:
        data = json.load(file)
        data['assistant_key'] = ass_id
    return


@app.get("/")
def index_get():
    return render_template("base.html")


@app.post("/nudge")
def nudge():
    message = {"answer": "Try asking for any information or typing 'What is the HR policy for Leaves?'"}
    return jsonify(message)


@app.post("/predict")
def predict(): 
    text = request.get_json().get("message")
    # response = send_answer(text)
    message = {"answer": "response"}
    return jsonify(message)


if __name__ == "__main__":
    app.run()

