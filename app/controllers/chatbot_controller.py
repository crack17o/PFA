from flask import Blueprint, request, jsonify, session
from app.models.conversation import Conversation, Message
from app import db
import openai
from datetime import datetime

chatbot_bp = Blueprint('chatbot', __name__)

@chatbot_bp.route('/chat/start', methods=['POST'])
def start_conversation():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    conv = Conversation(user_id=user_id)
    db.session.add(conv)
    db.session.commit()
    return jsonify({'conversation_id': conv.id})

@chatbot_bp.route('/chat/send', methods=['POST'])
def send_message():
    data = request.json
    user_id = session.get('user_id')
    conv_id = data.get('conversation_id')
    content = data.get('content')
    if not user_id or not conv_id or not content:
        return jsonify({'error': 'Missing data'}), 400
    conv = Conversation.query.get(conv_id)
    if not conv or conv.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    msg = Message(conversation_id=conv_id, sender='user', content=content)
    db.session.add(msg)
    db.session.commit()
    # Récupérer l'historique
    history = [{'role': m.sender, 'content': m.content} for m in conv.messages]
    # Appel OpenAI
    openai.api_key = 'YOUR_OPENAI_API_KEY'  # à remplacer par variable d'env
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=history
    )
    bot_content = response.choices[0].message['content']
    bot_msg = Message(conversation_id=conv_id, sender='bot', content=bot_content)
    db.session.add(bot_msg)
    db.session.commit()
    return jsonify({'bot_reply': bot_content})

@chatbot_bp.route('/chat/history/<conv_id>', methods=['GET'])
def get_history(conv_id):
    user_id = session.get('user_id')
    conv = Conversation.query.get(conv_id)
    if not conv or conv.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    messages = [{'sender': m.sender, 'content': m.content, 'timestamp': m.timestamp} for m in conv.messages]
    return jsonify({'messages': messages})
