from groq import Groq, APIConnectionError
import os
import base64
import re
from speechOutput import say
from speechInput import get_speech
# from type_printing import print_response
from dotenv import load_dotenv
from utility_functions import *
from cli_colors import AsciiColors
from conversations_test import Conversation






load_dotenv()

m = AsciiColors()


class AI_Utilties:
    

    def __init__(self):
        self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        self.models = [
            "llava-v1.5-7b-4096-preview", 
            'llama3-groq-70b-8192-tool-use-preview',
            'llama3-groq-8b-8192-tool-use-preview', 
            "llama3-70b-8192", 
            "llama3-8b-8192", 
            "distil-whisper-large-v3-en"
        ]
        self.conversation = Conversation()

   

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









a = AI_Utilties()

def ai_sound_analysis_external(prompt, sound):

    client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    filename = os.path.dirname(__file__) + sound 

    # Open the audio file
    with open(filename, "rb") as file:
        # Create a transcription of the audio file
        transcription = client.audio.transcriptions.create(
        file=(filename, file.read()), # Required audio file
        model=a.models[5], # Required model to use for transcription
        prompt=prompt,  # Optional
        response_format="json",  # Optional
        language="en",  # Optional
        temperature=0.0  # Optional
        )
        # Print the transcription text
        # print(transcription.text)
        return(transcription.text)

def ai_chat_external(prompt):
    try:
        client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        completion = client.chat.completions.create(
        model=a.models[3],
        messages=a.conversation.conversation_history,
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )
        response = ''

        for chunk in completion:
            response += chunk.choices[0].delta.content or ""
        a.conversation.append_to_history('assistant', response)
        return response
    except:
        return ""

def ai_image_analysis_external(prompt, image):
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
                                "url": image if a.is_url(image) else f"data:image/jpeg;base64,{a.encode_image(image)}" if a.is_file_path(image) else "",
                            },
                        },
                    ],
                }
            ],
            model=a.models[0],
        )

        return chat_completion.choices[0].message.content
    except:
        return ""

def ai_chat(prompt):
    return ai_chat_external(prompt)

def ai_image_analysis(prompt, image):
    return ai_image_analysis_external(prompt, image)

def ai_sound_analysis(prompt, sound):
    return ai_sound_analysis_external(prompt, sound)




def ai_function_execution(prompt, tools, available_functions):
    try:
        client = Groq(api_key=os.getenv('GROQ_API_KEY'))
       
        a.conversation.append_to_history("user", prompt)
        
        # First Response
        response = client.chat.completions.create(
            model=a.models[1],
            messages=a.conversation.conversation_history,
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
                
                try:
                    function_response = function_to_call(**function_args)
                    a.conversation.append_to_history("tool", function_response, tool_call_id=tool_call.id, function_name=function_name)
                except Exception as e:
                    print(f"Error calling {function_name}: {e}")
                
            # Return Second Response
            second_response = client.chat.completions.create(
                model=a.models[1],
                messages=a.conversation.conversation_history
            )
            a.conversation.append_to_history("assistant", second_response.choices[0].message.content)
            return second_response.choices[0].message.content
        else:
            # print("No tool calls found.")
            return ai_chat(prompt)
    except APIConnectionError as e:
        print(f"API connection error: {e}")
    except Exception as e:
        print(f"Error in function execution: {e}")







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




# print("\n\n", ai_function_execution(a.get_prompt(), tools, available_functions), "\n\n")


# print("\n\n", ai_function_execution('''Hello. can you tell me the current time in ghana? After that Greet me Since My name is John Ken. Now Tell me the result of this expression (900/3-300/10000). then tell me what is in the image i will give you based on the url/path : https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQgsNffTLsiZ7L-8kk8Dy8QppedW9zjI9tkkaWIq04rOkhL7OYKV-pOvBtuVMIepqDA64o&usqp=CAU. After Everything Tell me what you know about the BMW. Also, Can you please analyse this song for me? this is the audio file /audio.mp3. Can you do this for me?''', tools, available_functions), "\n\n")

'''
 Hello. can you tell me the current time in ghana? After that Greet me Since My name is John Ken. Now Tell me the result of this expression (900/3-300/10000). then tell me what is in the image i will give you based on the url/path : https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQgsNffTLsiZ7L-8kk8Dy8QppedW9zjI9tkkaWIq04rOkhL7OYKV-pOvBtuVMIepqDA64o&usqp=CAU. After Everything Tell me what you know about the BMW. Also, Can you please analyse this song for me? this is the audio file /audio.mp3. Can you do this for me?
'''




# def chat():
#     while True:
#         # user_prompt = a.get_speech_prompt()
#         user_prompt = a.get_text_prompt()
#         if user_prompt.lower() == 'x' or user_prompt.lower() == 'exit':
#             break
#         elif user_prompt == "":
#             print("--------")
#             continue
#         response = ai_function_execution(user_prompt, tools, available_functions)
#         # print(response)
#         print_response("\n\n"+response+"\n\n")
#         # say(True, response or "Nothing in response")

# # chat()s




