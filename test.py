import questionary
import pyttsx3

# List of voices (for testing)
voices = [
    {"name": "Alex"}, {"name": "Alice"}, {"name": "Alva"}, {"name": "Amelie"},
    {"name": "Anna"}, {"name": "Carmit"}, {"name": "Damayanti"}, {"name": "Daniel"},
    {"name": "Diego"}, {"name": "Ellen"}, {"name": "Fiona"}, {"name": "Fred"},
    {"name": "Ioana"}, {"name": "Joana"}, {"name": "Jorge"}, {"name": "Juan"},
    {"name": "Kanya"}, {"name": "Karen"}, {"name": "Kate"}, {"name": "Kyoko"},
    {"name": "Laura"}, {"name": "Lekha"}, {"name": "Luca"}, {"name": "Luciana"},
    {"name": "Maged"}, {"name": "Mariska"}, {"name": "Mei-Jia"}, {"name": "Melina"},
    {"name": "Milena"}, {"name": "Moira"}, {"name": "Monica"}, {"name": "Nora"},
    {"name": "Oliver"}, {"name": "Paulina"}, {"name": "Rishi"}, {"name": "Samantha"},
    {"name": "Sara"}, {"name": "Satu"}, {"name": "Serena"}, {"name": "Sin-ji"},
    {"name": "Tessa"}, {"name": "Thomas"}, {"name": "Ting-Ting"}, {"name": "Veena"},
    {"name": "Victoria"}, {"name": "Xander"}
]

def paginate_list(items, page_size=10):
    """Splits the list into pages of size page_size."""
    return [items[i:i + page_size] for i in range(0, len(items), page_size)]

# Paginate voices
page_size = 10
pages = paginate_list(voices, page_size)
current_page = 0

while True:
    # Get the current batch of voices
    page = pages[current_page]
    
    # Add navigation options
    choices = [questionary.Choice(v["name"], v) for v in page]
    if current_page > 0:
        choices.insert(0, "⬆ Previous Page")
    if current_page < len(pages) - 1:
        choices.append("⬇ Next Page")
    choices.append("Exit")

    # Select a voice
    choice = questionary.select(
        "Select a Voice:",
        choices=choices,
        pointer="❯"
    ).ask()

    if choice == "⬆ Previous Page":
        current_page -= 1
    elif choice == "⬇ Next Page":
        current_page += 1
    elif choice == "Exit" or not choice:
        break
    else:
        print(f"Selected voice: {choice['name']}")
        break
