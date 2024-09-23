import speech_recognition as STT


def get_speech():

    recognizer = STT.Recognizer()
    recognizer.energy_threshold = 200  # default is 300
    # recognizer.pause_threshold = 0.5  # default is 0.8
    # recognizer.non_speaking_duration = 0.5  # default is 0.5

    with STT.Microphone() as source:
        print('say something: ')
        audio = recognizer.listen(source)



    try:
        text = recognizer.recognize_google(audio)
        print('You Said: ', text)
        return text
    except STT.UnknownValueError:
        print("Google Speech Recognition could not understand the audio")
        return ""
    except STT.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
        return ""
