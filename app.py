import os
import json
import re
from flask import Flask, render_template, request, jsonify
from api1 import call_url

app = Flask(__name__)

# Load intents from data.json
current_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(current_dir, "data.json")

with open(json_path, "r", encoding="utf-8") as file:
    intents = json.load(file)["intents"]

def get_response(user_input):
    """Match user input with intent patterns using improved keyword ranking."""
    user_input = user_input.lower()
    best_match = None
    highest_score = 0

    for intent in intents:
        for pattern in intent["patterns"]:
            pattern_lower = pattern.lower()

            # ✅ Exact Match
            if user_input == pattern_lower:
                return intent["responses"]

            # ✅ Keyword Score: Count matching words
            keywords = set(pattern_lower.split())
            user_words = set(user_input.split())
            common_words = keywords.intersection(user_words)
            score = len(common_words)

            # ✅ Partial Matching: Use regex to find phrases
            if re.search(r"\b" + re.escape(pattern_lower) + r"\b", user_input):
                score += 2  # Boost score for regex matches

            # ✅ Choose the best match
            if score > highest_score:
                highest_score = score
                best_match = intent["responses"]

    return best_match if best_match else ["Sorry, I didn't understand that. Please try again."]

@app.get("/")
def index_get():
    return render_template("base.html")

@app.post("/save_url")
def save_url():
    dataframes = call_url("done")
    message = {"answer": dataframes} if dataframes else {"answer": "No data found"}
    return jsonify(message)


@app.post("/nudge")
def nudge():
    return jsonify({"answer": "Try asking for any information or typing 'What is the HR policy for Leaves?'"})

@app.post("/predict")
def predict():
    """Processes user query and returns an appropriate response."""
    user_input = request.get_json().get("message")
    response_list = get_response(user_input)

    print(f"User Input: {user_input}")
    print(f"Matched Response (Before Sending): {response_list}")

    # ✅ Ensure response is a string, not a character array
    if response_list:
        full_response = response_list if isinstance(response_list, str) else response_list[0]
        print(f"Sending Response: {full_response}")  # Debugging log
        return jsonify({"answer": full_response})
    else:
        return jsonify({"answer": "I couldn't find an answer to your question."})

if __name__ == "__main__":
    app.run(debug=True)
