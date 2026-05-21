import speech_recognition as sr

import pyttsx3

import datetime

import webbrowser

import os



# Initialize the recognizer and TTS engine

recognizer = sr.Recognizer()

engine = pyttsx3.init()



def speak(text):

    engine.say(text)

    engine.runAndWait()



def greet():

    hour = datetime.datetime.now().hour

    if 0 <= hour < 12:

        speak("Good morning!")

    elif 12 <= hour < 18:

        speak("Good afternoon!")

    else:

        speak("Good evening!")

    speak("I am your Voice Assistant. How can I help you today?")



def listen():

    with sr.Microphone() as source:

        print("Listening...")

        recognizer.adjust_for_ambient_noise(source)

        audio = recognizer.listen(source)

        try:

            command = recognizer.recognize_google(audio)

            print(f"You said: {command}")

            return command.lower()

        except sr.UnknownValueError:

            speak("Sorry, I didn't understand that.")

            return ""

        except sr.RequestError:

            speak("Sorry, the service is down.")

            return ""



def execute_command(command):

    if 'time' in command:

        time = datetime.datetime.now().strftime('%I:%M %p')

        speak(f"The current time is {time}")

    elif 'open google' in command:

        speak("Opening Google")

        webbrowser.open('https://www.google.com')

    elif 'play music' in command:

        speak("Playing music")

        music_folder = "C:/Users/Public/Music"  # Change path as needed

        songs = os.listdir(music_folder)

        os.startfile(os.path.join(music_folder, songs[0]))

    elif 'exit' in command or 'quit' in command:

        speak("Goodbye!")

        exit()

    else:

        speak("Sorry, I can't perform that action.")



if __name__ == "__main__":

    greet()

    while True:

        command = listen()

        if command:

            execute_command(command)

