import json
from datetime import datetime
import pytz








def calculate(expression):
    """Evaluate a mathematical expression"""
    try:
        result = eval(expression)
        return json.dumps({"result": result})
    except:
        return json.dumps({"error": "Invalid expression"})
    
def get_current_time(e):
    location_to_timezone = {
        "Ghana": "Africa/Accra",
        "New York": "America/New_York",
        "London": "Europe/London",
        "Tokyo": "Asia/Tokyo",
        # Add more locations as needed
    }

    # Retrieve timezone from location mapping
    timezone_str = location_to_timezone.get(e)
    
    if not timezone_str:
        return "Location not recognized"

    # Get current time in the specified timezone
    timezone = pytz.timezone(timezone_str)
    current_time = datetime.now(timezone)
    
    # Format the time as HH:MM:SS
    return current_time.strftime('%H:%M:%S')

def returnHi(name):
    return f"Hello {name}"





all_tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a mathematical expression",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "The mathematical expression to evaluate"}
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "returnHi",
            "description": "Says Hello to the given name",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string", "description": "The name to greet"}},
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Tell the current time",
            "parameters": {
                "type": "object",
                "properties": {"e": {"type": "string", "description": "The country for the time."}},
                "required": ["e"],  
            },
        },
    },
]

all_functions={
    "calculate": calculate,
    "get_current_time": get_current_time,
    "returnHi": returnHi,
}
