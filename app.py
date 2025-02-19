from flask import Flask, request, jsonify
import base64
import tempfile
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

def transcribe_audio(audio_base64):

    # Decode the base64 audio data
    try:
        audio_data = base64.b64decode(audio_base64)
    except Exception as e:
        return f"Error decoding base64 audio: {str(e)}"
    
    # Convert base64 audio to a format that SpeechRecognition can use (WAV)
    audio_file = BytesIO(audio_data)
    audio = AudioSegment.from_file(audio_file)

    # Create a temporary file to store the WAV audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        audio.export(temp_file.name, format="wav")
        temp_file_path = temp_file.name

    # Use SpeechRecognition to transcribe the audio
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(temp_file_path) as source:
            audio_listened = recognizer.record(source)
            transcription = recognizer.recognize_google(audio_listened)
            return transcription
    except Exception as e:
        return f"Error transcribing audio: {str(e)}"

@app.route('/',methods=['GET'])
def health():
    return "Hello world from python"

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        # Get the base64 audio data from the POST request
        print("here")
        data = request.json
        if not data or 'audio_base64' not in data:
            return jsonify({"error": "Missing audio_base64 in request"}), 400

        audio_base64 = data['audio_base64']

        # Transcribe the audio
        transcription = transcribe_audio(audio_base64)
        
        print("transcription",transcription)
        if "Error" in transcription:
            return jsonify({"error": transcription}), 500

        return jsonify({"transcription": transcription}), 200
    except Exception as e:
        print("error",e)

if __name__ == '__main__':
    app.run(debug=True)
