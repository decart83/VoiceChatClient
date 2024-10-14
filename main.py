#import streamlit packages
import streamlit as st
from audio_recorder_streamlit import audio_recorder
from openai import OpenAI
API_KEY = st.secrets["API_KEY"]

#import chat server packages
import socket
import threading
import random


#Voice functions
def transcribe_text_to_voice(audio_location):
    client = OpenAI(api_key=API_KEY)
    audio_file= open(audio_location, "rb")
    transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
    return transcript.text

def chat_completion_call(text):
    client = OpenAI(api_key=API_KEY)
    messages = [{"role": "user", "content": text}]
    response = client.chat.completions.create(model="gpt-3.5-turbo-1106", messages=messages)
    return response.choices[0].message.content


def text_to_speech_ai(speech_file_path, api_response):
    client = OpenAI(api_key=API_KEY)
    response = client.audio.speech.create(model="tts-1",voice="nova",input=api_response)
    response.stream_to_file(speech_file_path)

#server functions
# Listening to Server and Sending Nickname
def receive():
    while True:
        try:
            # Receive Message From Server
            # If 'NICK' Send Nickname
            message = client.recv(1024).decode('ascii')
            if message == nickname:
                client.send(nickname.encode('ascii'))
            else:
                print(message)
        except:
            # Close Connection When Error
            print("An error occured!")
            client.close()
            break

# Sending Messages To Server
def write():
    while True:
        message = '{}: {}'.format(nickname, input(''))
        client.send(message.encode('ascii'))




#connect to server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('165.227.200.35', 8080))

#server nickname
#nickname = input("Choose your nickname: ")
nickname = "User " + str(random.randint(1, 900))

# Starting Threads For Listening And Writing
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()

st.title("Talking Assistant")

audio_bytes = audio_recorder()
if audio_bytes:
    ##Save the Recorded File
    audio_location = "audio_file.wav"
    with open(audio_location, "wb") as f:
        f.write(audio_bytes)

    #Transcribe the saved file to text
    text = transcribe_text_to_voice(audio_location)
    st.write(text)

    #Use API to get an AI response
    api_response = chat_completion_call(text)
    st.write(api_response)

    # Read out the text response using tts
    speech_file_path = 'audio_response.mp3'
    text_to_speech_ai(speech_file_path, api_response)
    st.audio(speech_file_path)