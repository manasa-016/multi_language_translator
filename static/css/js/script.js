// DOM Elements
const inputText = document.getElementById('inputText');
const outputText = document.getElementById('outputText');
const translateBtn = document.getElementById('translateBtn');
const detectBtn = document.getElementById('detectBtn');
const speakBtn = document.getElementById('speakBtn');
const copyBtn = document.getElementById('copyBtn');
const clearBtn = document.getElementById('clearBtn');
const targetLang = document.getElementById('targetLang');
const detectedLang = document.getElementById('detectedLang');
const detectedLangCode = document.getElementById('detectedLangCode');
const targetLangName = document.getElementById('targetLangName');
const targetLangCode = document.getElementById('targetLangCode');
const audioPlayer = document.getElementById('audioPlayer');
const audioElement = document.getElementById('audioElement');
const downloadAudio = document.getElementById('downloadAudio');
const charCounter = document.getElementById('charCounter');

// State
let currentTranslation = '';
let currentAudioUrl = '';

// Initialize
function init() {
    // Update character counter
    inputText.addEventListener('input', () => {
        const count = inputText.value.length;
        charCounter.textContent = count;
        charCounter.style.color = count > 5000 ? '#ef476f' : '#06d6a0';
    });

    // Enter key for translation
    inputText.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') {
            translate();
        }
    });

    // Quick language buttons
    document.querySelectorAll('.lang-quick-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const lang = btn.getAttribute('data-lang');
            targetLang.value = lang;
            updateTargetLanguage();
        });
    });

    // Language cards
    document.querySelectorAll('.lang-card').forEach(card => {
        card.addEventListener('click', () => {
            const lang = card.getAttribute('data-lang');
            targetLang.value = lang;
            updateTargetLanguage();
            showAlert(`Selected ${card.querySelector('.lang-name').textContent}`, 'info');
        });
    });

    // Quick text buttons
    document.querySelectorAll('.quick-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            inputText.value = btn.getAttribute('data-text');
            inputText.dispatchEvent(new Event('input'));
            showAlert('Example text loaded', 'info');
        });
    });

    // Auto-detect language while typing
    let detectTimeout;
    inputText.addEventListener('input', () => {
        clearTimeout(detectTimeout);
        if (inputText.value.trim().length >= 3) {
            detectTimeout = setTimeout(detectLanguage, 1500);
        }
    });

    updateTargetLanguage();
}

// Update target language display
function updateTargetLanguage() {
    const selectedOption = targetLang.options[targetLang.selectedIndex];
    targetLangName.textContent = selectedOption.text.split('(')[0].trim();
    targetLangCode.textContent = targetLang.value;
}

// Detect language
async function detectLanguage() {
    const text = inputText.value.trim();
    
    if (text.length < 3) {
        detectedLang.textContent = 'Text too short';
        detectedLangCode.textContent = '--';
        return;
    }

    try {
        const response = await fetch('/detect', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });

        const data = await response.json();
        
        if (data.success) {
            detectedLang.textContent = data.language;
            detectedLangCode.textContent = data.code;
            showAlert(`Detected: ${data.language}`, 'success');
        }
    } catch (error) {
        console.error('Detection failed:', error);
        showAlert('Language detection failed', 'error');
    }
}

// Translate text
async function translate() {
    const text = inputText.value.trim();
    
    if (!text) {
        showAlert('Please enter text to translate', 'error');
        return;
    }

    if (text.length > 5000) {
        showAlert('Text is too long (max 5000 characters)', 'error');
        return;
    }

    try {
        // Show loading state
        translateBtn.disabled = true;
        translateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Translating...';

        const response = await fetch('/translate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: text,
                target_lang: targetLang.value
            })
        });

        const data = await response.json();

        if (data.success) {
            currentTranslation = data.translated_text;
            
            // Display translation
            outputText.innerHTML = `
                <div class="translation-result">
                    <div class="source-info">
                        <small>Translated from ${data.source_lang} to ${data.target_lang}</small>
                    </div>
                    <div class="translation-text">${currentTranslation}</div>
                </div>
            `;

            // Update language displays
            detectedLang.textContent = data.source_lang;
            detectedLangCode.textContent = data.source_code;
            targetLangName.textContent = data.target_lang;
            targetLangCode.textContent = data.target_code;

            // Enable output buttons
            speakBtn.disabled = false;
            copyBtn.disabled = false;
            document.getElementById('downloadBtn').disabled = false;
            audioPlayer.style.display = 'none';

            showAlert('Translation successful!', 'success');
        } else {
            throw new Error(data.error || 'Translation failed');
        }
    } catch (error) {
        console.error('Translation error:', error);
        showAlert(`Translation failed: ${error.message}`, 'error');
    } finally {
        translateBtn.disabled = false;
        translateBtn.innerHTML = '<i class="fas fa-exchange-alt"></i> Translate Now';
    }
}

// Generate speech
async function generateSpeech() {
    if (!currentTranslation) {
        showAlert('No translation available', 'error');
        return;
    }

    try {
        speakBtn.disabled = true;
        speakBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';

        const response = await fetch('/tts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: currentTranslation,
                lang: targetLang.value
            })
        });

        const data = await response.json();

        if (data.success) {
            currentAudioUrl = data.audio_url;
            audioElement.src = currentAudioUrl;
            downloadAudio.href = currentAudioUrl;
            audioPlayer.style.display = 'flex';
            
            // Auto-play
            setTimeout(() => {
                audioElement.play().catch(e => {
                    console.log('Autoplay prevented');
                });
            }, 100);

            showAlert('Speech generated successfully', 'success');
        } else {
            throw new Error(data.error || 'Speech generation failed');
        }
    } catch (error) {
        console.error('Speech error:', error);
        showAlert(`Speech generation failed: ${error.message}`, 'error');
    } finally {
        speakBtn.disabled = false;
        speakBtn.innerHTML = '<i class="fas fa-volume-up"></i> Listen';
    }
}

// Copy translation
function copyTranslation() {
    if (!currentTranslation) {
        showAlert('No translation to copy', 'error');
        return;
    }

    navigator.clipboard.writeText(currentTranslation)
        .then(() => {
            copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
            showAlert('Translation copied to clipboard', 'success');
            
            setTimeout(() => {
                copyBtn.innerHTML = '<i class="fas fa-copy"></i> Copy';
            }, 2000);
        })
        .catch(err => {
            console.error('Copy failed:', err);
            showAlert('Failed to copy text', 'error');
        });
}

// Clear all
function clearAll() {
    inputText.value = '';
    outputText.innerHTML = `
        <div class="placeholder">
            <i class="fas fa-language"></i>
            <h4>Translation will appear here</h4>
            <p>Select target language and click Translate</p>
        </div>
    `;
    detectedLang.textContent = 'Auto-Detect';
    detectedLangCode.textContent = '--';
    currentTranslation = '';
    speakBtn.disabled = true;
    copyBtn.disabled = true;
    audioPlayer.style.display = 'none';
    charCounter.textContent = '0';
    
    showAlert('All fields cleared', 'info');
}

// Alert system
function showAlert(message, type) {
    // Remove existing alerts
    const existing = document.querySelector('.alert');
    if (existing) existing.remove();

    // Create alert
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <span>${message}</span>
        <button class="alert-close">&times;</button>
    `;

    document.body.appendChild(alert);

    // Close button
    alert.querySelector('.alert-close').addEventListener('click', () => {
        alert.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => alert.remove(), 300);
    });

    // Auto-remove
    setTimeout(() => {
        if (alert.parentElement) {
            alert.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => alert.remove(), 300);
        }
    }, 5000);
}

// Event listeners
document.addEventListener('DOMContentLoaded', init);
translateBtn.addEventListener('click', translate);
detectBtn.addEventListener('click', detectLanguage);
speakBtn.addEventListener('click', generateSpeech);
copyBtn.addEventListener('click', copyTranslation);
clearBtn.addEventListener('click', clearAll);
targetLang.addEventListener('change', updateTargetLanguage);

// Audio player events
audioElement.addEventListener('play', () => {
    document.getElementById('audioStatus').textContent = 'Playing...';
});

audioElement.addEventListener('ended', () => {
    document.getElementById('audioStatus').textContent = 'Playback finished';
});

// Download audio
downloadAudio.addEventListener('click', (e) => {
    e.preventDefault();
    const filename = `translation_${targetLang.value}_${Date.now()}.mp3`;
    downloadAudio.download = filename;
});