import json
from datetime import datetime
import webbrowser
import os
import platform
from PIL import ImageGrab
import time


def calculate(expression):
    """Evaluate a mathematical expression"""
    try:
        result = eval(expression)
        return json.dumps({"result": result})
    except:
        return json.dumps({"error": "Invalid expression"})


def open_cmd():
    """Open the command terminal."""
    if os.name == 'nt':  # Windows
        os.system('start cmd')
    else:  # macOS/Linux
        os.system('open -a Terminal' if os.name == 'posix' else 'gnome-terminal')
    return ""


def tell_time(date=False, time=False):
    """Tell the current time and/or date."""
    current_date_time = datetime.now()
    ctime = current_date_time.strftime("%I:%M %p")
    ctime = str(int(ctime[:2])) + ctime[2:]
    day = current_date_time.day
    cdate = f"{day}{get_day_suffix(day)} of {current_date_time.strftime('%B %Y')}"

    if date and time:
        return cdate + ", " + ctime
    elif time:
        return ctime
    elif date:
        return cdate


def get_day_suffix(day):
    """Get the appropriate suffix for the day of the month."""
    if 11 <= day % 100 <= 13:
        return 'th'
    return {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')


def open_website(link):
    webbrowser.open(link)
    return ""


def play_video(video):
        """
        Play a video on YouTube.

        Args:
            prompt (str): The user's input prompt.

        Returns:
            Tuple[str, str]: Empty strings if successful, otherwise error messages.
        """
        try:
            import pywhatkit as kit
            kit.playonyt(video), f'Playing {video}'
            return ''
        except Exception as e:
            time.sleep(2)
            return ""
        
        
            


def get_system_info():
    info = {
        "System": platform.system(),
        "Node Name": platform.node(),
        "Release": platform.release(),
        "Version": platform.version(),
        "Machine": platform.machine(),
        "Processor": platform.processor(),
    }
    return json.dumps(info)


def take_screenshot(file_path='screenshot'):
    screenshot = ImageGrab.grab()
    screenshot.save(f'{file_path}.png')
    return f"Screenshot taken and saved as '{file_path}.png'"


def get_volume():
    volume = os.popen("osascript -e 'output volume of (get volume settings)'").read().strip()
    return volume


def set_volume(level):
    os.system(f"osascript -e 'set volume output volume {level}'")
    return f"Volume set to {level}%"


def mute_volume():
    os.system("osascript -e 'set volume with output muted'")
    return "Volume muted"


def lock_screen():
    os.system('osascript -e "tell application \\"System Events\\" to keystroke \\"q\\" using {control down, command down}"')
    return "Screen locked"







# Updated all_tools
all_tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a mathematical expression",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The mathematical expression to evaluate"
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "open_cmd",
            "description": "This opens the terminal for the user on request",
            "parameters": {},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tell_time",
            "description": "This tells the current time and date to the user upon request.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "boolean",
                        "description": "This determines if you should tell the user just the date."
                    },
                    "time": {
                        "type": "boolean",
                        "description": "This determines if you should tell the user just the time."
                    }
                },
                "required": ["date", "time"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "open_website",
            "description": "This should open a website based on the link given to you.",
            "parameters": {
                "type": "object",
                "properties": {
                    "link": {
                        "type": "string",
                        "description": "This is the link you would be opening in the web browser."
                    }
                },
                "required": ["link"],
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_system_info",
            "description": "Retrieve system information including OS, machine, and processor.",
            "parameters": {}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "take_screenshot",
            "description": "Take a screenshot of the current screen and save it.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "This is the name of the file to save it. if none is mentioned, it defaults to 'screenshot'"
                    }
                },
                "required": ["file_path"],
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_volume",
            "description": "Get the current system volume level. and returns it as a string",
            "parameters": {}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_volume",
            "description": "Set the system volume to a specific level (0 to 100).",
            "parameters": {
                "type": "object",
                "properties": {
                    "level": {
                        "type": "integer",
                        "description": "Volume level to set (0-100)"
                    }
                },
                "required": ["level"],
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mute_volume",
            "description": "Mute the system volume.",
            "parameters": {}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "lock_screen",
            "description": "Lock the system screen.",
            "parameters": {}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "play_video",
            "description": "Play a video on YouTube based on the title provided.",
            "parameters": {
                "type": "object",
                "properties": {
                    "video": {
                        "type": "string",
                        "description": "The title or keywords of the video to play."
                    }
                },
                "required": ["video"],
            }
        }
    }
]

# Updated all_functions
all_functions = {
    "calculate": calculate,
    "open_cmd": open_cmd,
    "tell_time": tell_time,
    "open_website": open_website,
    "get_system_info": get_system_info,
    "take_screenshot": take_screenshot,
    "get_volume": get_volume,
    "set_volume": set_volume,
    "mute_volume": mute_volume,
    "lock_screen": lock_screen,
    "play_video": play_video,
}
