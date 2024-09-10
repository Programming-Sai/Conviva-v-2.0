import speech_recognition as STT

recognizer = STT.Recognizer()

with STT.Microphone() as source:
    print('say something: ')
    audio = recognizer.listen(source)



try:
    print('You Said: ', recognizer.recognize_google(audio))
except STT.UnknownValueError:
    print("Google Speech Recognition could not understand the audio")
except STT.RequestError as e:
    print("Could not request results from Google Speech Recognition service; {0}".format(e))
