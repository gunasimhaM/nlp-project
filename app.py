from flask import Flask, flash, redirect, render_template, request, jsonify
import os
from together import Together 
import re 
import json
from transformers import pipeline

app = Flask(__name__)

# Correct the API key argument
client = Together(api_key="ac7d929a9eb9529121e93611a42ec587959ae4d1d76dfd0ea167ee942c018821")

url = "https://api.together.xyz/inference"
# # lopen source trained model 
# DistilBERT, a smaller, faster, and lighter version of BERT (Bidirectional Encoder Representations from Transformers)
Model = "bhadresh-savani/distilbert-base-uncased-emotion"
# refers to a model that is based on MiniLM, a smaller and faster variant of the BERT family, 
# which has been fine-tuned for emotion classification tasks
model_ckpt = "abhyast/minilm-finetuned-emotion-class-model"
pipe = pipeline("text-classification", model=model_ckpt)

def detect_emotion(text):
    results = pipe(text)
    return results[0] if results else None

@app.route('/')
def index():
    return render_template('index.html')

def create_ad_slogan(pd, emotion):
    prompt = '''you are a creative advertisement generator. Given the user emotions and product details, you have to generate a very creative and attractive advertisement slogan so that it can market well.
    only respond in the below mentioned output format:
    {"ad_slogan":"generated ad slogan","ad_description":"generated ad description"}
    product details and user review based emotion given below:
    '''
    inputs = f"product details: {pd} user emotion: {emotion}"
    prompt = prompt + inputs
    response = client.chat.completions.create(
        model=Model,
        messages=[{"role": "user", "content": prompt}],
    )
    print("response:\n", response.choices[0].message.content)
    res = response.choices[0].message.content
    res_dict = extract_json(res)

    adslogan = res_dict["ad_slogan"]
    ad_description = res_dict["ad_description"]

    return adslogan, ad_description

def extract_json(response):
    json_match = re.search(r'\{.*\}', response, re.DOTALL)
    if json_match:
        json_string = json_match.group(0)
        json_data = json.loads(json_string)
        return json_data
    else:
        return None

@app.route('/generate', methods=['POST'])
def generate():
    if request.method == "POST":
        user_review = request.form['user_review']
        prod_details = request.form['product_details']
        emotion = detect_emotion(user_review)
        emotion = emotion['label']
        print("emotion", emotion)
        adslogan, ad_description = create_ad_slogan(prod_details, emotion)
        return render_template("prod.html", adslogan=adslogan, ad_description=ad_description, emotion=emotion)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
