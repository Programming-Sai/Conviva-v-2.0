from groq import Groq, APIConnectionError
import os
import base64
import re
from dotenv import load_dotenv
from utility_functions import *
from cli_colors import AsciiColors
from conversations import Conversation
from pynput import keyboard
import threading
import platform
import subprocess
import speech_recognition as STT








load_dotenv()

m = AsciiColors()


class AI_Utilties:
    

    def __init__(self, title_function, conversation=None):
        self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        self.models_deprecated = [
            "llava-v1.5-7b-4096-preview", 
            'llama3-groq-70b-8192-tool-use-preview',
            'llama3-groq-8b-8192-tool-use-preview', 
            "llama3-70b-8192", 
            "llama3-8b-8192", 
            "distil-whisper-large-v3-en"
        ]

        self.models = [
            'llama-3.3-70b-versatile',
            'llama-3.2-11b-vision-preview',
            "distil-whisper-large-v3-en",
        ]
        
        
        self.conversation = conversation if conversation is not None else Conversation(title_function)

        
    def get_text_prompt(self):
        return input(m.color("\nYou: ", m.GREEN))
   
    def get_speech_prompt(self):
        return get_speech()

    def encode_image(self, image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')

    def is_url(self, string):
        url_pattern = re.compile(
            r'^(?:http|ftp)s?://' # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
            r'localhost|' # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|' # ...or ipv4
            r'\[?[A-F0-9]*:[A-F0-9:]+\]?)' # ...or ipv6
            r'(?::\d+)?' # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return re.match(url_pattern, string) is not None

    def is_base64_image(self, string):
        base64_pattern = re.compile(
            r'^data:image/(?P<type>jpeg|png|gif);base64,[A-Za-z0-9+/=]+$', re.IGNORECASE)
        return re.match(base64_pattern, string) is not None

    def is_windows_path(self,string):
        # Check for Windows path pattern
        return re.match(r'^[A-Z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]*$', string, re.IGNORECASE) is not None

    def is_unix_path(self, string):
        # Check for Unix/Linux/Mac path pattern
        return re.match(r'^(/[^/ ]*)+/?$', string) is not None

    def is_file_path(self, string):
        # Check if it is not a URL and matches file path patterns
        return not self.is_url(string) and (self.is_windows_path(string) or self.is_unix_path(string))

    
'''
Set up the STT for the cli so it looks nice and easy to use.  and also set up an interrupt mechanism so that speech can be cut when not needed.

Set up subparsers for the cli, so that there would be a more sturctured system of command line tools.


'''




# a = AI_Utilties()
x = AsciiColors()

 
def ai_sound_analysis_external(prompt, sound, utilities_class):

    client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    # filename = os.path.dirname(__file__) + sound 
    filename = sound

    # Open the audio file
    with open(filename, "rb") as file:
        try:
            transcription = client.audio.transcriptions.create(
                file=(filename, file.read()), # Required audio file
                # model=utilities_class.models[5], # Required model to use for transcription
                model=utilities_class.models[2], # Required model to use for transcription
                response_format="json",  # Optional
                language="en",  # Optional
                temperature=0.0  # Optional
            )
        

            completion = client.chat.completions.create(
            model=utilities_class.models[3],
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Lyrics: {transcription.text}\n\n{prompt}"}
            ],
                temperature=1,
                max_tokens=1024,
                top_p=1,
            )
            response = completion.choices[0].message.content
            return response
        except:
            return ""
       

def ai_chat_external(utilities_class):
    try:
        client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        completion = client.chat.completions.create(
        model=utilities_class.models[0],
        # model=utilities_class.models[3],
        messages=utilities_class.conversation.conversation_history,
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )
        response = ''

        for chunk in completion:
            response += chunk.choices[0].delta.content or ""
        utilities_class.conversation.append_to_history('assistant', response)
        return response
    except Exception as e:
        print(e)
        if "Request too large" in str(e):
            return "This conversation has exceeded the size limit. You can delete some messages, start a new conversation, or optionally delete this entire conversation."
        return f"Some Thing Unexpected Happened: {e}"

def ai_image_analysis_external(prompt, image, utilities_class):
    try:
        client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        chat_completion = client.chat.completions.create(
        messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image if utilities_class.is_url(image) else f"data:image/jpeg;base64,{utilities_class.encode_image(image)}" if utilities_class.is_file_path(image) else "",
                            },
                        },
                    ],
                }
            ],
            model=utilities_class.models[1],
            # model=utilities_class.models[0],
        )

        return chat_completion.choices[0].message.content
    except:
        return ""

def ai_chat(utilities_class):
    return ai_chat_external(utilities_class)

def ai_image_analysis(prompt, image, utilities_class):
    return ai_image_analysis_external(prompt, image, utilities_class)

def ai_sound_analysis(prompt, sound, utilities_class):
    return ai_sound_analysis_external(prompt, sound, utilities_class)




# Global flag to stop speech
stop_speaking = False

def stop_speech():
    """
    Monitors for the 'I' key press to stop the speech using pynput.
    """
    global stop_speaking
    
    def on_press(key):
        try:
            if key.char == 'i':  # Stop if 'I' is pressed
                stop_speaking = True
                if platform.system() == 'Darwin':
                    subprocess.run(['killall', 'say'])
                return False  # Stop listener
        except AttributeError:
            # Handle special keys if needed
            pass

    # Start listening for key presses
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

def say(speak: bool, text: str, voice: str = 'Daniel') -> str:
    """
    Speak the given text if the 'speak' flag is True, and stop when 'I' is pressed.

    Args:
        speak (bool): Flag to determine whether to speak the text.
        text (str): The text to be spoken.
        voice (str): Voice name (default is 'Daniel' on macOS).

    Returns:
        str: The input text.
    """
    global stop_speaking
    stop_speaking = False

    if speak:
        if platform.system() == 'Darwin':  # macOS
            # Start the thread that waits for 'I' to stop the speech
            stop_thread = threading.Thread(target=stop_speech)
            stop_thread.start()

            ALLOWED_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 /-.,?_!@$%^&*()#")
            clean_text = ''.join(c for c in text if c in ALLOWED_CHARS)

            # Run the speech command, allowing it to be stopped
            try:
                # Save the speech to an audio file
                # subprocess.run(["say", "-o", 'Sound/prompt.aiff', text])

                # # Speak out loud
                # subprocess.run(["say", "-v", voice, clean_text])
                subprocess.run(["say", "-v", "Daniel", "-o", os.path.join(os.getcwd(), 'Sound', 'prompt.aiff'), text])

            except subprocess.CalledProcessError:
                if stop_speaking:
                    print("Speech stopped.")
        
            # Join the thread back to ensure proper termination
            stop_thread.join()

        # elif platform.system() == 'Windows':  # Windows
        #     engine = pyttsx3.init()
        #     engine.say(text)
        #     engine.runAndWait()

    return text



def ai_function_execution(prompt, tools, available_functions, utilities_class):
    try:
        client = Groq(api_key=os.getenv('GROQ_API_KEY'))
       
        utilities_class.conversation.append_to_history("user", prompt)
        
        # First Response
        response = client.chat.completions.create(
            model=utilities_class.models[1],
            messages=utilities_class.conversation.conversation_history,
            tools=tools,
            tool_choice="auto",
            max_tokens=4096
        )
        
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls or {}


        if tool_calls:
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions.get(function_name)
                function_args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
                
                if function_name in ['ai_image_analysis', 'ai_sound_analysis']:  
                    function_args['utilities_class'] = utilities_class 

                try:
                    function_response = function_to_call(**function_args)
                    utilities_class.conversation.append_to_history("tool", function_response, tool_call_id=tool_call.id, function_name=function_name)
                except Exception as e:
                    print(f"Error calling {function_name}: {e}")
                
            # Return Second Response
            second_response = client.chat.completions.create(
                model=utilities_class.models[1],
                messages=utilities_class.conversation.conversation_history
            )
            utilities_class.conversation.append_to_history("assistant", second_response.choices[0].message.content)
            return second_response.choices[0].message.content
        else:
            return ai_chat(utilities_class)
    except APIConnectionError as e:
        print(f"API connection error: {e}")
    except Exception as e:
        print(f"Error in function execution: {e}")




def get_speech():

    recognizer = STT.Recognizer()
    recognizer.energy_threshold = 200  # default is 300
    # recognizer.pause_threshold = 0.5  # default is 0.8
    # recognizer.non_speaking_duration = 0.5  # default is 0.5

    with STT.Microphone() as source:
        print(x.color('Say something: ', x.BRIGHT_BLUE))
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        print(x.color('You Said: ', x.GREEN), text)
        return text
    except STT.UnknownValueError:
        print(x.color("...", x.BRIGHT_RED))
        return ""
    except STT.RequestError as e:
        print(x.color("Could not request results from Google Speech Recognition service; {0}".format(e), x.BRIGHT_RED))
        return ""





available_functions = all_functions | {
    "ai_image_analysis": ai_image_analysis,
    "ai_sound_analysis": ai_sound_analysis 
}


tools = all_tools + [  
    {
        "type": "function",
        "function": {
            "name": "ai_image_analysis",
            "description": "Analyze an image based on the provided prompt and image path or URL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "The prompt for image analysis."},
                    "image": {"type": "string", "description": "The path or URL to the image to be analyzed."}
                },
                "required": ["prompt", "image"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "ai_sound_analysis",
            "description": "Analyze an audio based on the provided prompt and audio path or URL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "The prompt for sound analysis."},
                    "sound": {"type": "string", "description": "The path or URL to the audio to be analyzed."}
                },
                "required": ["prompt", "sound"],
            },
        },
    }
]




