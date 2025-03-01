import questionary
from questionary import Style

# Define a custom style
custom_style = Style([
    ('pointer', 'fg:#00ff00 bold'),  # Change arrow color (green) and make it bold
    ('highlighted', 'fg:#ffcc00 bold')  # Change highlighted text color (yellow)
])

print()
# Prompt with a custom arrow (pointer)
choice = questionary.select(
    "Pick a framework:",
    choices=["React", "Vue", "Svelte"],
    pointer="❯",  # Change the default arrow
    style=custom_style  # Apply the custom style
).ask()

print(f"You selected: {choice}")
