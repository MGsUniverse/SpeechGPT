import openai
import gtts
from playsound import playsound
import speech_recognition as sr
from tkinter import *
import os
import threading


def loop():
    global string
    # Create an instance of tkinter frame
    win = Tk()

    # Set the geometry of tkinter frame
    win.geometry("750x270")

    # Create a canvas
    global canvas
    canvas = Canvas(win, width=600, height=400)
    win.title("SpeechGPT - Matt")
    canvas.pack()

    global LABEL
    LABEL = canvas.create_text(300, 50, text="Listening...", fill="black", font=('Helvetica 15 bold'))
    canvas.pack()

    def on_closing():
        os._exit(1)

    win.protocol("WM_DELETE_WINDOW", on_closing)

    win.mainloop()


thread = threading.Thread(target=loop)
thread.start()


def recognize_speech_from_mic(recognizer, microphone):
    """Transcribe speech from recorded from `microphone`.

    Returns a dictionary with three keys:
    "success": a boolean indicating whether or not the API request was
               successful
    "error":   `None` if no error occured, otherwise a string containing
               an error message if the API could not be reached or
               speech was unrecognizable
    "transcription": `None` if speech could not be transcribed,
               otherwise a string containing the transcribed text
    """
    # check that recognizer and microphone arguments are appropriate type
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    # adjust the recognizer sensitivity to ambient noise and record audio
    # from the microphone
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    # set up the response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    # try recognizing the speech in the recording
    # if a RequestError or UnknownValueError exception is caught,
    #     update the response object accordingly
    try:
        response["transcription"] = recognizer.recognize_google(audio)
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"

    return response


recognizer = sr.Recognizer()
microphone = sr.Microphone()

i = 0

openai.api_key = "APIKEY"

while True:
    query = recognize_speech_from_mic(recognizer, microphone)

    print(query["transcription"])

    if query["transcription"] is not None:
        if "Matt" in query["transcription"]:
            new_query = query["transcription"].split("Matt")
            canvas.itemconfig(LABEL, text="Processing...")
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": new_query[1]}
                ]
            )

            print(completion.choices[0].message.content)

            tts = gtts.gTTS(completion.choices[0].message.content)
            tts.save("file" + str(i) + ".mp3")
            canvas.itemconfig(LABEL, text="Speaking...")
            playsound("file" + str(i) + ".mp3")
            i += 1
            canvas.itemconfig(LABEL, text="Listening...")
