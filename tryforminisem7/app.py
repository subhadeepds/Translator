import os
from flask import Flask, request, jsonify, render_template
import googletrans
import gtts
import playsound
import speech_recognition as sr
from datetime import datetime
import PyPDF2
import pytesseract
from PIL import Image

app = Flask(__name__, template_folder='templates', static_folder='static')
translator = googletrans.Translator()

# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/translate_voice', methods=['POST'])
def translate_voice():
    recognizer = sr.Recognizer()
    data = request.get_json()
    from_lang = data['from_lang']
    to_lang = data['to_lang']
    translate_to_voice = data.get('translate_to_voice', True)
   
    with sr.Microphone() as source:
        print("Speak now")
        voice = recognizer.listen(source)
        listen = recognizer.recognize_google(voice, language=from_lang)
        print(listen)

    translate = translator.translate(listen, dest=to_lang)
    print(translate.text.encode('utf-8'))

    if translate_to_voice:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"translated_{timestamp}.mp3"
        converted_audio = gtts.gTTS(translate.text, lang=to_lang)
        converted_audio.save(filename)
        playsound.playsound(filename)
        os.remove(filename)
   
    return jsonify({'translated_text': translate.text})

@app.route('/translate_text', methods=['POST'])
def translate_text():
    data = request.get_json()
    text = data['text']
    to_lang = data['to_lang']
    translate = translator.translate(text, dest=to_lang)
    return jsonify({'translated_text': translate.text})

@app.route('/text_to_speech', methods=['POST'])
def text_to_speech():
    data = request.get_json()
    text = data['text']
    to_lang = data['to_lang']
   
    translate = translator.translate(text, dest=to_lang)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"text_to_speech_{timestamp}.mp3"
    converted_audio = gtts.gTTS(translate.text, lang=to_lang)
    converted_audio.save(filename)
    playsound.playsound(filename)
    os.remove(filename)
   
    return jsonify({'status': 'success'})

@app.route('/file_translate', methods=['POST'])
def file_translate():
    file = request.files['file']
    from_lang = request.form['from_lang']
    to_lang = request.form['to_lang']

    if file.filename.endswith('.txt'):
        text = file.read().decode('utf-8')
    elif file.filename.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(file)
        text = ''
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    else:
        return jsonify({'error': 'Unsupported file type'}), 400

    translate = translator.translate(text, dest=to_lang)
    return jsonify({'translated_text': translate.text})

@app.route('/image_translate', methods=['POST'])
def image_translate():
    file = request.files['file']
    from_lang = request.form['from_lang']
    to_lang = request.form['to_lang']

    if file and (file.filename.endswith('.jpg') or file.filename.endswith('.png') or file.filename.endswith('.jpeg')):
        image = Image.open(file)
        text = pytesseract.image_to_string(image, lang=from_lang)
        translate = translator.translate(text, dest=to_lang)
        return jsonify({'translated_text': translate.text})
    else:
        return jsonify({'error': 'Unsupported file type'}), 400

if __name__ == '__main__':
    app.run(debug=True)
