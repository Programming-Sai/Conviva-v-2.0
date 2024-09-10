import platform
import subprocess




def say(speak: bool, text: str, voice: str ='Daniel') -> str:
    """
    Speak the given text if the 'speak' flag is True.

    Args:
        speak (bool): Flag to determine whether to speak the text.
        text (str): The text to be spoken.

    Returns:
        str: The input text.
    """
    if speak:
        if platform.system() == 'Darwin':  # macOS
            # Save the speech to an audio file
            subprocess.run(["say", "-o", 'Sound/prompt.aiff', text])
            
            ALLOWED_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 /-.,?_!@$%^&*()#|")
            clean_text = ''.join(c for c in text if c in ALLOWED_CHARS)

            subprocess.run(["say", "-v", voice, clean_text])
        # elif platform.system() == 'Windows':  # Windows
        #     engine = pyttsx3.init()
        #     engine.say(text)
        #     engine.runAndWait()
    return text


# say(True, """Correct Command Usage: Use the say command with the -v option correctly. Ensure that the voice name you specify matches exactly with one from the list of voices.

# Check for Errors: If the voice is still not changing, there might be an issue with how the command is being executed or an issue with the voice installation itself.""")