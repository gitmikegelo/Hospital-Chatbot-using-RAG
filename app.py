import yaml
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from openai import OpenAI
from pinecone import Pinecone

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat_history.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

import json

with open('apikeys.json') as config_file:
    config = json.load(config_file)


openai_api_key = config['openai_key']
pinecone_api_key= config['pinecone_key']

client = OpenAI(api_key=openai_api_key)
pc = Pinecone(api_key=pinecone_api_key)
index_name = 'chatbot'
index = pc.Index(index_name)

# Load prompts.yaml
with open('prompts.yaml', 'r') as file:
    prompts = yaml.safe_load(file)
combined_prompt_template = prompts['combined_prompt']

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_message = db.Column(db.String(500), nullable=False)
    bot_response = db.Column(db.String(500), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)

@app.route('/clear-history', methods=['POST'])
def clear_history():
    try:
        db.session.query(Message).delete()
        db.session.commit()
        return "Chat history cleared successfully!"
    except Exception as e:
        db.session.rollback()
        return str(e), 500

def generate_response(prompt, context):
    chat_history = Message.query.all()
    chat_history_text = " ".join([f"User: {msg.user_message} Bot: {msg.bot_response}" for msg in chat_history])
    combined_prompt = combined_prompt_template.format(prompt=prompt, context=context, chat_history="")
    response = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=combined_prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

@app.route('/', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        data = request.get_json()
        
        if 'name' in data and 'phone' in data:
            name = data['name']
            phone = data['phone']
            new_user = User(name=name, phone=phone)
            db.session.add(new_user)
            db.session.commit()
            return jsonify(message="User information saved successfully.")

        user_query = data['query']
        query_embedding = client.embeddings.create(
            input=[user_query],
            model="text-embedding-ada-002"
        ).data[0].embedding
        query_results = index.query(vector=query_embedding, top_k=1, namespace="ns1", include_metadata=True)
        best_match = query_results['matches'][0] if query_results['matches'] else None
        context = best_match['metadata']['text'] if best_match else "I couldn't find anything relevant."
        response_text = generate_response(user_query, context)

        new_message = Message(user_message=user_query, bot_response=response_text)
        db.session.add(new_message)
        db.session.commit()

        return jsonify(bot_response=response_text)
    else:
        chat_history = Message.query.all()
        return render_template('chat.html', chat_history=chat_history)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
