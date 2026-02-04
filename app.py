"""
Indian Language Translator - Compatible with Python 3.9-3.11
For Render deployment
"""

import os
import sys
import tempfile
import logging

# Check Python version
python_version = sys.version_info
print(f"🐍 Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")

# Ensure we're using compatible Python version
if python_version.major == 3 and python_version.minor >= 14:
    print("⚠️  WARNING: Python 3.14+ may have compatibility issues")
    print("💡 Recommended: Use Python 3.9-3.11 on Render")

try:
    from flask import Flask, render_template, request, jsonify, send_file
    from deep_translator import GoogleTranslator
    from gtts import gTTS
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("📦 Installing dependencies...")
    print("Run: pip install Flask deep-translator gtts")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get PORT from environment (Render provides this)
PORT = int(os.environ.get('PORT', 5000))

# Initialize Flask app with explicit paths
try:
    # Get the directory of this file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(current_dir, 'templates')
    static_dir = os.path.join(current_dir, 'static')
    
    print(f"📁 Current directory: {current_dir}")
    print(f"📄 Template directory: {template_dir}")
    print(f"🎨 Static directory: {static_dir}")
    
    # Create Flask app with explicit template folder
    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir
    )
    
    app.secret_key = os.environ.get('SECRET_KEY', 'indian-translator-secret-key-2024')
    
    print("✅ Flask app initialized successfully")
    
except Exception as e:
    print(f"❌ Flask initialization error: {e}")
    print("💡 Trying alternative initialization...")
    
    # Fallback initialization
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'fallback-secret-key')

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
    """Home page - Simple HTML if template fails"""
    print("🌐 Serving home page")
    
    # Check if template exists
    template_path = os.path.join(app.template_folder, 'index.html')
    if os.path.exists(template_path):
        try:
            return render_template('index.html', languages=INDIAN_LANGUAGES)
        except Exception as e:
            print(f"❌ Template render error: {e}")
    
    # Fallback HTML
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Indian Language Translator</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            h1 {
                color: #333;
                text-align: center;
                margin-bottom: 30px;
            }
            textarea, select, button {
                width: 100%;
                padding: 15px;
                margin: 10px 0;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 16px;
            }
            textarea {
                min-height: 120px;
                resize: vertical;
            }
            button {
                background: #667eea;
                color: white;
                border: none;
                cursor: pointer;
                font-weight: bold;
                transition: 0.3s;
            }
            button:hover {
                background: #5a67d8;
                transform: translateY(-2px);
            }
            .output {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
                min-height: 100px;
                border: 2px dashed #ddd;
            }
            audio {
                width: 100%;
                margin-top: 20px;
            }
            .status {
                background: #10b981;
                color: white;
                padding: 10px;
                border-radius: 5px;
                text-align: center;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="status">
                ✅ Indian Language Translator is Running
            </div>
            
            <h1>🌐 Indian Language Translator</h1>
            
            <textarea id="inputText" placeholder="Enter text to translate...">Hello, how are you today?</textarea>
            
            <select id="targetLang">
                <option value="hi">Hindi (हिन्दी)</option>
                <option value="bn">Bengali (বাংলা)</option>
                <option value="ta">Tamil (தமிழ்)</option>
                <option value="te">Telugu (తెలుగు)</option>
                <option value="mr">Marathi (मराठी)</option>
                <option value="en">English</option>
            </select>
            
            <button onclick="translateText()">Translate</button>
            <button onclick="speakText()" id="speakBtn" disabled>Speak Translation</button>
            
            <div class="output" id="outputText">
                Translation will appear here...
            </div>
            
            <audio id="audioPlayer" controls></audio>
            
            <div style="margin-top: 30px; text-align: center; color: #666; font-size: 14px;">
                <p>Powered by Flask, deep-translator & gTTS</p>
                <p>Port: """ + str(PORT) + """ | Python: """ + f"{python_version.major}.{python_version.minor}" + """</p>
            </div>
        </div>
        
        <script>
            let currentTranslation = '';
            
            async function translateText() {
                const text = document.getElementById('inputText').value;
                const lang = document.getElementById('targetLang').value;
                
                if (!text.trim()) {
                    alert('Please enter text to translate');
                    return;
                }
                
                try {
                    const response = await fetch('/translate', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({text: text, target_lang: lang})
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        currentTranslation = data.translated_text;
                        document.getElementById('outputText').innerHTML = `
                            <strong>Translation:</strong><br>
                            ${currentTranslation}<br><br>
                            <small>To ${data.target_lang}</small>
                        `;
                        document.getElementById('speakBtn').disabled = false;
                    } else {
                        alert('Error: ' + data.error);
                    }
                } catch (error) {
                    alert('Error: ' + error);
                }
            }
            
            async function speakText() {
                if (!currentTranslation) {
                    alert('Please translate text first');
                    return;
                }
                
                try {
                    const lang = document.getElementById('targetLang').value;
                    
                    const response = await fetch('/tts', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({text: currentTranslation, lang: lang})
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        const audio = document.getElementById('audioPlayer');
                        audio.src = data.audio_url;
                        audio.play();
                    } else {
                        alert('Error: ' + data.error);
                    }
                } catch (error) {
                    alert('Error: ' + error);
                }
            }
            
            // Auto-translate on Ctrl+Enter
            document.getElementById('inputText').addEventListener('keydown', function(e) {
                if (e.ctrlKey && e.key === 'Enter') {
                    translateText();
                }
            });
        </script>
    </body>
    </html>
    """
    
    return html_content

@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    return jsonify({
        'status': 'healthy',
        'service': 'Indian Language Translator',
        'version': '2.0.0',
        'port': PORT,
        'python_version': f"{python_version.major}.{python_version.minor}.{python_version.micro}",
        'languages_supported': len(INDIAN_LANGUAGES)
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
        
        print(f"📝 Translating {len(text)} characters to {target_lang}")
        
        # Translate
        translator = GoogleTranslator(source='auto', target=target_lang)
        translated = translator.translate(text)
        
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
        
        # Limit text length
        text = text[:500]
        
        print(f"🎵 Generating speech for {lang}")
        
        # Get TTS language
        lang_info = INDIAN_LANGUAGES.get(lang, INDIAN_LANGUAGES['en'])
        tts_lang = lang_info['tts_lang']
        
        # Create temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        
        # Generate speech
        tts = gTTS(text=text, lang=tts_lang, slow=False)
        tts.save(temp_file.name)
        
        return jsonify({
            'success': True,
            'audio_url': f'/audio/{os.path.basename(temp_file.name)}',
            'message': 'Speech generated successfully'
        })
        
    except Exception as e:
        logger.error(f"TTS error: {e}")
        return jsonify({'error': f'Speech generation failed: {str(e)}'}), 500

@app.route('/audio/<filename>')
def serve_audio(filename):
    """Serve generated audio files"""
    try:
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

def check_directories():
    """Check and create necessary directories"""
    print("\n📁 Checking directory structure...")
    
    # List current directory
    print("Current directory contents:")
    for item in os.listdir('.'):
        print(f"  - {item}")
    
    # Create templates directory if it doesn't exist
    templates_path = os.path.join(os.path.dirname(__file__), 'templates')
    if not os.path.exists(templates_path):
        print(f"📝 Creating templates directory: {templates_path}")
        os.makedirs(templates_path, exist_ok=True)
        
        # Create basic template
        template_file = os.path.join(templates_path, 'index.html')
        with open(template_file, 'w') as f:
            f.write("<!-- Template will be loaded from fallback -->")
        print(f"📄 Created template file: {template_file}")
    
    # Create static directory if it doesn't exist
    static_path = os.path.join(os.path.dirname(__file__), 'static')
    if not os.path.exists(static_path):
        print(f"🎨 Creating static directory: {static_path}")
        os.makedirs(static_path, exist_ok=True)

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 INDIAN LANGUAGE TRANSLATOR")
    print("=" * 60)
    print(f"📡 Port: {PORT}")
    print(f"🐍 Python: {python_version.major}.{python_version.minor}.{python_version.micro}")
    print(f"📁 Working dir: {os.getcwd()}")
    print(f"📄 App file: {__file__}")
    print("=" * 60)
    
    # Check directories
    check_directories()
    
    print("✅ Starting Flask server...")
    print(f"🌐 Access at: http://localhost:{PORT}")
    print("=" * 60)
    
    # Run the app
    app.run(
        host='0.0.0.0',
        port=PORT,
        debug=False  # Set to False for production
    )