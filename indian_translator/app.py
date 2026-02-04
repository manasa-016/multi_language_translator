#!/usr/bin/env python3
"""
Indian Language Translator for Render Deployment
Make sure this file is in the ROOT directory
"""

import os
import sys

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from flask import Flask, render_template, request, jsonify, send_file
    from deep_translator import GoogleTranslator
    from gtts import gTTS
    import tempfile
    import logging
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Please install dependencies: pip install Flask deep-translator gtts langdetect")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get PORT from environment or use default
PORT = int(os.environ.get('PORT', 5000))

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'render-translator-secret-2024')

# Indian Languages with TTS support
INDIAN_LANGUAGES = {
    'hi': {'name': 'Hindi', 'native': 'हिन्दी', 'tts_lang': 'hi'},
    'bn': {'name': 'Bengali', 'native': 'বাংলা', 'tts_lang': 'bn'},
    'te': {'name': 'Telugu', 'native': 'తెలుగు', 'tts_lang': 'te'},
    'mr': {'name': 'Marathi', 'native': 'मराठी', 'tts_lang': 'mr'},
    'ta': {'name': 'Tamil', 'native': 'தமிழ்', 'tts_lang': 'ta'},
    'ur': {'name': 'Urdu', 'native': 'اردو', 'tts_lang': 'ur'},
    'gu': {'name': 'Gujarati', 'native': 'ગુજરાતી', 'tts_lang': 'gu'},
    'kn': {'name': 'Kannada', 'native': 'ಕನ್ನಡ', 'tts_lang': 'kn'},
    'ml': {'name': 'Malayalam', 'native': 'മലയാളം', 'tts_lang': 'ml'},
    'pa': {'name': 'Punjabi', 'native': 'ਪੰਜਾਬੀ', 'tts_lang': 'pa'},
    'or': {'name': 'Odia', 'native': 'ଓଡ଼ିଆ', 'tts_lang': 'or'},
    'as': {'name': 'Assamese', 'native': 'অসমীয়া', 'tts_lang': 'as'},
    'en': {'name': 'English', 'native': 'English', 'tts_lang': 'en'}
}

@app.route('/')
def home():
    """Home page with translation interface"""
    print("📄 Serving home page")
    try:
        return render_template('index.html', languages=INDIAN_LANGUAGES)
    except Exception as e:
        print(f"❌ Template error: {e}")
        return """
        <html>
        <head><title>Indian Translator</title></head>
        <body>
            <h1>Indian Language Translator</h1>
            <p>Template not found. Please ensure templates/index.html exists.</p>
        </body>
        </html>
        """

@app.route('/health')
def health():
    """Health check endpoint for Render"""
    return jsonify({
        'status': 'healthy',
        'service': 'Indian Language Translator',
        'port': PORT,
        'languages': len(INDIAN_LANGUAGES)
    })

@app.route('/translate', methods=['POST'])
def translate():
    """Translate text between languages"""
    try:
        print("🔄 Translation request received")
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        text = data.get('text', '').strip()
        target_lang = data.get('target_lang', 'hi')
        
        if not text:
            return jsonify({'error': 'Please enter text'}), 400
        
        print(f"📝 Translating: '{text[:50]}...' to {target_lang}")
        
        # Translate using Google Translator
        translator = GoogleTranslator(source='auto', target=target_lang)
        translated = translator.translate(text)
        
        print(f"✅ Translation successful")
        
        return jsonify({
            'success': True,
            'original_text': text,
            'translated_text': translated,
            'target_lang': INDIAN_LANGUAGES.get(target_lang, {}).get('name', 'Unknown')
        })
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return jsonify({'error': f'Translation failed: {str(e)}'}), 500

@app.route('/tts', methods=['POST'])
def text_to_speech():
    """Convert text to speech"""
    try:
        print("🔊 TTS request received")
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        text = data.get('text', '').strip()
        lang = data.get('lang', 'en')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Limit text length for performance
        text = text[:500]
        
        print(f"🎵 Generating speech for {lang}, text length: {len(text)}")
        
        # Get TTS language code
        lang_info = INDIAN_LANGUAGES.get(lang, INDIAN_LANGUAGES['en'])
        tts_lang = lang_info['tts_lang']
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        temp_path = temp_file.name
        
        # Generate speech
        tts = gTTS(text=text, lang=tts_lang, slow=False)
        tts.save(temp_path)
        
        print(f"✅ Speech generated: {temp_path}")
        
        filename = os.path.basename(temp_path)
        
        return jsonify({
            'success': True,
            'audio_url': f'/audio/{filename}',
            'message': 'Speech generated successfully'
        })
        
    except Exception as e:
        logger.error(f"TTS error: {e}")
        return jsonify({'error': f'Speech generation failed: {str(e)}'}), 500

@app.route('/audio/<filename>')
def serve_audio(filename):
    """Serve generated audio files"""
    try:
        print(f"🎧 Serving audio file: {filename}")
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, filename)
        
        if os.path.exists(file_path):
            return send_file(
                file_path,
                mimetype='audio/mpeg',
                as_attachment=False,
                download_name="translation.mp3"
            )
        else:
            print(f"❌ Audio file not found: {file_path}")
            return jsonify({'error': 'Audio file not found'}), 404
            
    except Exception as e:
        logger.error(f"Audio serve error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/languages', methods=['GET'])
def get_languages():
    """Get list of supported languages"""
    return jsonify({
        'success': True,
        'languages': INDIAN_LANGUAGES,
        'count': len(INDIAN_LANGUAGES)
    })

def create_template_if_missing():
    """Create basic template if it doesn't exist"""
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(template_dir, exist_ok=True)
    
    template_path = os.path.join(template_dir, 'index.html')
    
    if not os.path.exists(template_path):
        print("📝 Creating basic template...")
        basic_html = """<!DOCTYPE html>
<html>
<head>
    <title>Indian Translator</title>
    <style>
        body { font-family: Arial; padding: 20px; max-width: 800px; margin: 0 auto; }
        textarea, select, button { width: 100%; padding: 10px; margin: 10px 0; }
        .output { background: #f0f0f0; padding: 15px; margin: 20px 0; }
    </style>
</head>
<body>
    <h1>Indian Language Translator</h1>
    <textarea id="text" rows="4">Hello, how are you?</textarea>
    <select id="lang">
        <option value="hi">Hindi</option>
        <option value="bn">Bengali</option>
        <option value="ta">Tamil</option>
        <option value="te">Telugu</option>
        <option value="en">English</option>
    </select>
    <button onclick="translate()">Translate</button>
    <button onclick="speak()" id="speakBtn" disabled>Speak</button>
    <div class="output" id="output"></div>
    <audio id="audio" controls></audio>
    
    <script>
        async function translate() {
            const text = document.getElementById('text').value;
            const lang = document.getElementById('lang').value;
            
            const res = await fetch('/translate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({text: text, target_lang: lang})
            });
            
            const data = await res.json();
            if (data.success) {
                document.getElementById('output').innerHTML = data.translated_text;
                document.getElementById('speakBtn').disabled = false;
            }
        }
        
        async function speak() {
            const text = document.getElementById('output').innerText;
            const lang = document.getElementById('lang').value;
            
            const res = await fetch('/tts', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({text: text, lang: lang})
            });
            
            const data = await res.json();
            if (data.success) {
                document.getElementById('audio').src = data.audio_url;
                document.getElementById('audio').play();
            }
        }
    </script>
</body>
</html>"""
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(basic_html)
        
        print(f"✅ Template created at: {template_path}")

if __name__ == '__main__':
    print("=" * 60)
    print("INDIAN LANGUAGE TRANSLATOR")
    print("=" * 60)
    print(f"Port: {PORT}")
    print(f"Python: {sys.version}")
    print(f"Working Directory: {os.getcwd()}")
    print(f"File Location: {__file__}")
    print("=" * 60)
    
    # Create template if missing
    create_template_if_missing()
    
    # List files in current directory
    print("📁 Files in current directory:")
    for root, dirs, files in os.walk('.'):
        level = root.replace('.', '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            print(f"{subindent}{file}")
    
    print("=" * 60)
    print("🚀 Starting Flask server...")
    
    # Run the app
    app.run(
        host='0.0.0.0',
        port=PORT,
        debug=False  # Set to False for production
    )