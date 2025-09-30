from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import asyncio
import re
import os
from telegram import Bot
from telegram.constants import ParseMode
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = "@qcmchannel001"

def strip_html(text):
    """Supprime les balises HTML et nettoie le texte"""
    if not text:
        return ""
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</[^>]+>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()

def escape_markdown_v2(text):
    """Échappe les caractères spéciaux pour MarkdownV2"""
    if not text:
        return ""
    escape_chars = r'_*[]()~`>#+=|{}.!-'
    return ''.join('\\' + char if char in escape_chars else char for char in text)

def check_options_length(options, max_length=100):
    """Vérifie si toutes les options respectent la longueur maximale"""
    for opt in options:
        clean_opt = strip_html(opt)
        if len(clean_opt) > max_length:
            return False
    return True

def truncate_text(text, max_length=4000):
    """Tronque le texte s'il est trop long"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

async def send_quizzes(questions):
    """Fonction asynchrone pour envoyer les quizzes"""
    bot = Bot(TOKEN)
    sent_count = 0
    skipped_count = 0
    
    for i, q in enumerate(questions, 1):
        clean_question = strip_html(q["question"])
        
        if len(clean_question) > 300:
            print(f"⊘ Question {i}/{len(questions)} ignorée (question > 300 caractères)")
            skipped_count += 1
            continue
        
        clean_options = [strip_html(opt) for opt in q["options"]]
        
        if not check_options_length(q["options"]):
            print(f"⊘ Question {i}/{len(questions)} ignorée (option > 100 caractères)")
            skipped_count += 1
            continue
        
        try:
            await bot.send_poll(
                chat_id=CHANNEL_ID,
                question=clean_question,
                options=clean_options,
                type="quiz",
                correct_option_id=q["correct_answers"][0],
            )
            print(f"✓ Question {i}/{len(questions)} envoyée")
            sent_count += 1

            await asyncio.sleep(5)

            if q.get('explication') and q['explication'].strip():
                clean_explanation = strip_html(q['explication'])
                clean_explanation = truncate_text(clean_explanation, 4000)
                escaped_explanation = escape_markdown_v2(clean_explanation)
                explanation_message = f"||{escaped_explanation}||"
                
                await bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=explanation_message,
                    parse_mode=ParseMode.MARKDOWN_V2
                )
                print(f"  ↳ Explication envoyée")
            
            await asyncio.sleep(15)
            
        except Exception as e:
            print(f"✗ Erreur avec la question {i}: {e}")
            continue

    return sent_count, skipped_count

@app.route('/')
def index():
    """Serve the HTML interface"""
    # Get the absolute path to index.html
    base_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(base_dir, '..', 'index.html')
    
    # Check if file exists
    if not os.path.exists(html_path):
        return jsonify({"error": "index.html not found", "path": html_path}), 404
    
    return send_file(html_path)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Quiz Bot",
        "channel": CHANNEL_ID
    }), 200

@app.route('/api/start-bot', methods=['POST'])
def start_bot():
    """Endpoint pour démarrer le bot avec les questions JSON"""
    try:
        questions = request.get_json()
        
        if not questions or not isinstance(questions, list):
            return jsonify({"error": "Invalid JSON format"}), 400
        
        # Run async function
        sent, skipped = asyncio.run(send_quizzes(questions))
        
        return jsonify({
            "success": True,
            "sent": sent,
            "skipped": skipped,
            "total": len(questions)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    if not TOKEN:
        print("✗ ERREUR: Le jeton du bot Telegram n'est pas défini.")
        print("  ↳ Créez un fichier .env et ajoutez TELEGRAM_BOT_TOKEN=VOTRE_JETON")
    else:
        print("🚀 Quiz Bot Server starting...")
        print("  ↳ Token: ...{}".format(TOKEN[-4:]))
        print("  ↳ Channel: {}".format(CHANNEL_ID))
        print("  ↳ Ready to accept requests")
        app.run(host='0.0.0.0', port=5000, debug=False)