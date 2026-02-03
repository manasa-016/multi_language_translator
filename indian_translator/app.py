from flask import Flask, render_template, request, jsonify, send_file
from deep_translator import GoogleTranslator
from gtts import gTTS
import os
import tempfile
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Languages
LANGUAGES = {
    'hi': 'Hindi',
    'bn': 'Bengali', 
    'te': 'Telugu',
    'mr': 'Marathi',
    'ta': 'Tamil',
    'ur': 'Urdu',
    'gu': 'Gujarati',
    'kn': 'Kannada',
    'ml': 'Malayalam',
    'pa': 'Punjabi',
    'or': 'Odia',
    'as': 'Assamese',
    'en': 'English'
}

@app.route('/')
def home():
    return render_template('index.html', languages=LANGUAGES)

@app.route('/translate', methods=['POST'])
def translate():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        target_lang = data.get('target_lang', 'hi')
        
        if not text:
            return jsonify({'error': 'कोई टेक्स्ट नहीं है'})
        
        # Translate
        translator = GoogleTranslator(source='auto', target=target_lang)
        translated = translator.translate(text)
        
        return jsonify({
            'success': True,
            'translated_text': translated,
            'target_lang': LANGUAGES.get(target_lang, 'Unknown')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/tts', methods=['POST'])
def tts():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        lang = data.get('lang', 'en')
        
        if not text:
            return jsonify({'error': 'कोई टेक्स्ट नहीं है'})
        
        # Create audio
        tts = gTTS(text=text, lang=lang, slow=False)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        tts.save(temp_file.name)
        
        return jsonify({
            'success': True,
            'audio_url': f'/audio/{os.path.basename(temp_file.name)}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/audio/<filename>')
def audio(filename):
    try:
        return send_file(
            os.path.join(tempfile.gettempdir(), filename),
            mimetype='audio/mpeg'
        )
    except:
        return 'File not found', 404

if __name__ == '__main__':
    print("🌐 Server starting...")
    print("📁 Open: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)