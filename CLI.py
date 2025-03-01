from pathlib import Path
import shutil

import questionary
from llm_processing import *
from cli_colors import AsciiColors
import argparse as ag
import time
import random
import threading
import sys
import tty
import termios
import select
from utility_functions import *
from tabulate import tabulate




title = r"""
 .--..--..--..--..--..--..--..--..--..--..--..--..--. 
/ .. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \
\ \/\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ \/ /
 \/ /`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'\/ / 
 / /\                                            / /\ 
/ /\ \    ______                 _              / /\ \
\ \/ /   / ____/___  ____ _   __(_)   ______ _  \ \/ /
 \/ /   / /   / __ \/ __ \ | / / / | / / __ `/   \/ / 
 / /\  / /___/ /_/ / / / / |/ / /| |/ / /_/ /    / /\ 
/ /\ \ \____/\____/_/ /_/|___/_/ |___/\__,_/    / /\ \
\ \/ /                                          \ \/ /
 \/ /                                            \/ / 
 / /\.--..--..--..--..--..--..--..--..--..--..--./ /\ 
/ /\ \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \/\ \
\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `' /
 `--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--' 
"""



 
class CLI(ag.ArgumentParser):
    def __init__(self):
        super().__init__(description="This command-line interface (CLI) tool offers a range of functionalities, including mathematical calculations, date and time retrieval, web browsing, audio and video downloading from YouTube, and AI-powered features such as chat and media analysis. Users can perform actions like taking screenshots, locking the screen, managing system volume, and more through straightforward commands and options. The program supports both speech and text interactions for an engaging user experience.")  

        self.end_convo = False

        self.utilities = AI_Utilties(self.cli_title_function, Conversation(self.cli_title_function))
        self.ascii_colors = AsciiColors()

        self.subparsers = self.add_subparsers(dest='command', required=False, parser_class=ag.ArgumentParser)
        self.extra_func_args = {
            'extra_prompt': '',
            'path': '',
            'extra_utilities_class': self.utilities,
            'func': None,
            'type': ''
        }
        self.stop_input_thread = threading.Event()
        self.stop_print_thread = threading.Event()

        self.conversation = []
        self.conversation_so_far = ''
        self.voice = self.get_or_set_voice('get')
        self.get_convresation_content()
        self.add_arguments()
        self.process_args()
        
   
    def cli_title_function(self):
        return input('Please what would you like to name this conversation?  ').replace(' ', '-').replace('_', '-')


    def add_arguments(self):
        # Conversation Modes
        # self.add_argument('-s', '--speech', action='store_true', help='Start a conversation using voice input and AI-generated speech responses.')
        # self.add_argument('-t', '--text', action='store_true', help='Start a conversation using text input where you type messages.')

        # Managing Conversations
        self.add_argument('-n', '--new-conversation', action='store_true', help='Start a new conversation session, separate from previous ones.')
        self.add_argument('-l', '--list-conversation', action='store_true', help='List all stored conversations with their names and timestamps.')

        # Conversation History Management
        self.add_argument('-c', '--clear-conversation', action='store_true', help='Delete all stored conversations and reset conversation history.')
        self.add_argument('-e', '--edit-conversation', action='store_true', help='Rename a saved conversation by providing its current name.')
        self.add_argument('-o', '--open-conversation', action='store_true', help='Open and view a saved conversation by providing its name.')
        self.add_argument('-d', '--delete-conversation', action='store_true', help='Delete a specific conversation by providing its name.')

        # Conversation Search
        self.add_argument('-F', '--search-conversation', action='store_true', help='Enter an interactive mode to search for specific conversations.')
        self.add_argument('-k', '--search-key', type=str, help='Find and display conversations containing a specific keyword.')

        # Voice Settings
        self.add_argument('-v', '--select-voice', type=str, help='Set the AI response voice by providing a voice name or ID.')

        # Open GUI
        self.add_argument('--gui', action='store_true', help='Launch the graphical user interface (GUI) for the application.')




    def process_args(self):
        try:
            print()
            args = self.parse_args()
            # if  args.speech:
            #     self.start_conversation(True, False)

            # elif args.text:
            #     self.start_conversation(False, True)
            
            if args.new_conversation:
                print("Creating a new conversation")
                self.new_conversation()


            elif args.list_conversation:
                print("List out all conversations")
                self.list_conversations()

            elif args.open_conversation:
                print("Open a Conversation")
                convo = self.select_conversation(action='To Open')
                self.update_conversation_tracker(convo)
                self.open_conversation(self.extract_timestamp(convo).replace("_", ""))

            elif args.clear_conversation:
                print("Clearing All Conversations")
                self.clear_conversation_history()
                
            elif args.edit_conversation:
                print("Editting an individual conversation")
                self.edit_conversation(self.select_conversation(action='To Edit'))
                   
            elif args.delete_conversation:
                print("Deleting a single conversation")
                self.delete_conversation(self.select_conversation(action='To Delete'))

                
            elif args.search_conversation:
                print("Searching for a conversation.")
                search_term = args.search_key if args.search_key else input("Enter a search term: ")
                self.search_filter_conversations(search_term)

                   
            elif args.select_voice:
                print("Selecting all voices")
                self.select_main_voice()
            
            elif args.gui:
                print("Opening GUI")

                
            else:
                self.start_conversation(False, True)
            print()
            return
        except Exception as e:
            print(f'\n\nSomething went Wrong. This Was The issue: {e}')




    def get_user_input(self, speech, text):
        if speech:
            user_speech = self.utilities.get_speech_prompt()
            return user_speech, user_speech.split(' ')
        elif text:
            user_text = self.utilities.get_text_prompt()
            return user_text, user_text.split(' ')
                
    def show_model_response(self, user_prompt, speech, text):
        if self.extra_func_args['func']:
            self.extra_func_args['extra_prompt'] = user_prompt
            response = ai_function_execution(user_prompt, tools, available_functions, self.utilities, extra_func=self.extra_func_args['func'], **{k: self.extra_func_args[k] for k in ['extra_prompt', 'path', 'extra_utilities_class']})
            self.extra_func_args = {
                'extra_prompt': '',
                'path': '',
                'extra_utilities_class': self.utilities,
                'func': None,
                'type': ''
            }
        else:
            response = ai_function_execution(user_prompt, tools, available_functions, self.utilities)
        if speech:
            say(speech, response or "Nothing in response", voice=self.voice)
        else:
            print(self.ascii_colors.color("\nConviva: ", self.ascii_colors.GREEN), end="")
            self.print_response(""+self.ascii_colors.color(response, self.ascii_colors.YELLOW)+"\n")
   


    def get_media_file_for_upload(self, file_path):

        file_extension = Path(file_path).suffix.replace('.', '').replace("'", "")

        print(": File path entered ->", file_path)
        print(": Extracted extension ->", file_extension)
        
        self.extra_func_args = {
            'extra_prompt': '',
            'path': file_path,
            'extra_utilities_class': self.utilities,
            'func': None,
            'type': ''
        }
        # Assigning the appropriate function for image or audio processing
        if file_extension in {'png', 'jpeg', 'jpg'}:
            self.extra_func_args['type'] = 'image'
            self.extra_func_args['func'] = ai_image_analysis
        elif file_extension in {'mp3', 'wav'}: 
            self.extra_func_args['func'] = ai_sound_analysis
            self.extra_func_args['type'] = 'sound'

        # print(": Assigned function ->", self.extra_func_args['func'])

        
    def upload_media(self):
        file = input("Enter Media for Analysis: ").strip()

        # Remove leading/trailing quotes if present
        if file.startswith(("'", '"')) and file.endswith(("'", '"')):
            file = file[1:-1]

        # Check if file exists
        if not os.path.isfile(file):
            print("Error: File does not exist. Please enter a valid file path.")
            return
        self.get_media_file_for_upload(file)



    def get_or_set_voice(self, action, voice={}):
        filename = "voice.json"
        if action == 'get':
            if os.path.exists(filename):
                try:
                    with open(filename, "r") as f:
                        return json.load(f)
                except json.JSONDecodeError:
                    print("Warning: Corrupted JSON file. Resetting to default.")
            else:
                with open(filename, 'w') as f:
                    json.dump({'voice': 'Daniel'}, f, indent=4)
        else:
            self.voice = voice
            with open(filename, 'w') as f:
                json.dump(f, voice, indent=4)

    def start_conversation(self, speech, text):
        if not self.get_conversations():
            self.new_conversation()
            return 
        print(self.ascii_colors.center_block_text(self.ascii_colors.random_color(title)))
        print(self.conversation_so_far)
        while True:
            user_prompt = self.get_user_input(speech, text)[0]
            if user_prompt.lower() == '/exit' or self.end_convo:
                print("Exiting application...")
                os._exit(1)
            elif user_prompt.lower() == '/new':
                self.new_conversation()
                continue
            elif user_prompt.lower() == '/upload':
                self.upload_media()
                continue
            elif user_prompt == "":
                print("--------")
                continue
            self.show_model_response(user_prompt, speech, text)
          
    def print_with_delay(self, passage):
        for char in passage:
            if self.stop_print_thread.is_set():  # Check if stop signal is set
                break
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(random.uniform(0.02, 0.1)) if char != '\n' else time.sleep(0.25)
        self.stop_input_thread.set()  # Set stop signal for input

    def disable_input(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)  # Save terminal settings
        try:
            tty.setcbreak(fd)  # Set terminal to raw mode
            while not self.stop_input_thread.is_set():
                if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                    key = sys.stdin.read(1)
                    if key == '\x03':  # Handle Ctrl+C (SIGINT)
                        raise KeyboardInterrupt
                    elif key.lower() == 'i':  # Stop printing only if 'i' is pressed
                        self.stop_print_thread.set()
                        break
        except KeyboardInterrupt:
            print("\nProcess interrupted by user.")
            self.stop_print_thread.set()
            self.stop_input_thread.set()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)  # Restore terminal settings

    def print_response(self, passage):
        self.stop_input_thread.clear()  # Reset stop signal
        self.stop_print_thread.clear()  # Reset stop signal for printing

        # Start the threads
        print_thread = threading.Thread(target=self.print_with_delay, args=(passage,))
        input_thread = threading.Thread(target=self.disable_input)

        print_thread.start()
        input_thread.start()

        print_thread.join()  # Wait for the print thread to finish
        self.stop_input_thread.set()  # Ensure stop event is set
        input_thread.join()  # Wait for the input thread to finish

    def new_conversation(self):
        self.utilities.conversation.move_file = True
        self.utilities.conversation.create_new_conversation()
        print("New Conversation Should Start here!!!")
        self.utilities.conversation.move_file = False
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n"*20)
        self.end_convo=True
        with open('Conversations/.current_conversation_file_name.txt', 'r') as f:
            self.open_conversation(self.extract_timestamp(f.read()).replace("_", ''))

   
    def open_conversation(self, id):
        self.conversation_so_far = ""
        print(id)
        try:
            conversations = self.get_conversations()
            conversation_to_open = [i for i in conversations if id == self.extract_timestamp(i).replace("_", "")][0]
            # Updating the current conversation file reference
            with open("Conversations/.current_conversation_file_name.txt", 'w') as f:
                f.write(conversation_to_open)

            # Loading the conversation history from the file
            with open(conversation_to_open, 'r') as file:
                self.utilities.conversation.conversation_history = json.load(file)
                self.conversation = self.utilities.conversation.conversation_history
            self.get_conversation_so_far()
            self.end_convo=False
            print("Starting Convo")
            return self.start_conversation(False, True)
        except Exception as e:
            print(f"Error opening conversation: {e}")
            self.utilities.conversation.conversation_history = []
            self.conversation = self.utilities.conversation.conversation_history
            self.new_conversation()

    def get_convresation_content(self):
        conversation_to_open = ''
        with open("Conversations/.current_conversation_file_name.txt", 'r') as f:
            conversation_to_open = f.read()

        print(conversation_to_open)
        # Loading the conversation history from the file
        with open(conversation_to_open, 'r') as file:
            self.utilities.conversation.conversation_history = json.load(file)
            self.conversation = self.utilities.conversation.conversation_history
        self.get_conversation_so_far()

    def extract_timestamp(self, file_name):
        """
        Extracts the timestamp from a conversation file name.

        Args:
            file_name (str): The file path of the conversation.

        Returns:
            str: Extracted timestamp in the format 'YYYY_MM_DD'.
        """
        copy = file_name.replace("Conversations/", "")

        # Returning empty string if it's a hidden file
        if copy.startswith("."):
            return ""
        
        # Extracting and returning the timestamp
        return copy.split('_')[1] + "_" + copy.split('_')[2] + "_" + copy.split('_')[3]

    def get_conversation_so_far(self):
        for i in self.conversation:
            if i['role'] == 'user':
                self.conversation_so_far += f"{self.ascii_colors.color('\n\nYou: ', self.ascii_colors.GREEN)}{i['content']}"
            elif i['role'] == 'assistant':
                self.conversation_so_far += f"{self.ascii_colors.color('\n\nConviva: ', self.ascii_colors.GREEN)}{self.ascii_colors.color(i['content'], self.ascii_colors.YELLOW)}"


    def get_conversations(self):
        """
        Retrieves and sorts conversation files based on extracted timestamps.

        Returns:
            list: A list of conversation file paths sorted by timestamp in descending order.
        """
        # Walking through the "Conversations" directory to get all files
        walk_gen = os.walk("Conversations")
        walk_list = list(walk_gen)
        root = walk_list[0][0]

        # Collecting file paths in the directory
        files = [os.path.join(root, i) for i in walk_list[0][2]] or []

        # Sorting files based on extracted timestamps (newest first)
        sorted_files = sorted(files, key=lambda x: self.extract_timestamp(x), reverse=True)
        return sorted_files
    

    def clear_conversation_history(self):
        if input("Are you sure that you want to clear your conversation history (Y/n): ").lower() == 'y':
            try:
                folder_path = "Conversations"
                # Deleting all conversation files
                for filename in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, filename)
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.remove(file_path)  
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path) 
                self.utilities.conversation.conversation_history = []
                self.conversation = self.utilities.conversation.conversation_history
            except Exception as e:
                print(f"Sonething went Wrong: {e}")
                
    def update_conversation_tracker(self, new_convo):
        with open('Conversations/.current_conversation_file_name.txt', 'w') as f:
            f.write(new_convo)

    def delete_conversation(self, file_path):
        if input(f"Are you sure that you want to delete {file_path[45:].replace('.json', "")} (Y/n): ").lower() == 'y':
            try:
                os.remove(file_path)
                print(f"{file_path[45:].replace('.json', "")} has been deleted successfully")
                conversations = self.get_conversations()
                self.update_conversation_tracker(conversations[0]) #if conversations[0] == file_path else ''
            except Exception as e:
                print("Sorry This Error has occured: ", e)
        

    def edit_conversation(self, file_path):
        if input(f"Are you sure that you want to rename {file_path[45:].replace('.json', "")} (Y/n): ").lower() == 'y':
            try:
                old = file_path
                new_title = input("Enter the New Conversation Title: ").replace(" ", "-")
                new = file_path.replace(file_path[45:].replace('.json', ""), new_title)
                os.rename(old, new)
                self.update_conversation_tracker(new)
                print(f"{file_path[45:].replace('.json', "")} has been renamed to {new[45:].replace('.json', "")} successfully")
            except Exception as e:
                print("Sorry This Error has occured: ", e)

    def search_filter_conversations(self, key_word):
        directory = 'Conversations'
        matching_files = [os.path.join(directory, f) for f in os.listdir(directory) if key_word.lower() in f.lower() and not f.startswith(".")]
        if matching_files: return matching_files

        if platform.system() == "Windows":
            # Using findstr for Windows
            try:
                result = subprocess.run(
                    ["findstr", "/S", "/I", key_word, f"{directory}\\*.json"], 
                    capture_output=True, text=True
                )
                content_matches = {line.split(":")[0] for line in result.stdout.splitlines()}  # Extract filenames only
            except Exception as e:
                content_matches = []
        else:
            # Using grep for macOS/Linux
            try:
                result = subprocess.run(
                    ["grep", "-ril", key_word, directory], capture_output=True, text=True
                )
                content_matches = set(result.stdout.splitlines())  # File names only
            except Exception as e:
                content_matches = []

        # Combine results (filenames + content matches)
        return content_matches

        

    def get_voices(self):
        # Get the voices from the "say" command
        result = subprocess.run(["say", "-v", "?"], capture_output=True, text=True)

        voices = []
        for line in result.stdout.splitlines():
            parts = line.split("#")
            if len(parts) == 2:
                name_and_lang = parts[0].strip().split(maxsplit=1)
                if len(name_and_lang) == 2:
                    name, lang = name_and_lang
                    description = parts[1].strip()
                    voices.append({"name": name, "language": lang, "description": description})
        return voices
    
    def paginate_list(self, items, page_size=10):
        """Splits the list into pages of size page_size."""
        return [items[i:i + page_size] for i in range(0, len(items), page_size)]
    

    def select_main_voice(self):
        voices = self.get_voices()
        custom_style = questionary.Style([
            ('pointer', 'fg:#00ff00 bold'),
            ('highlighted', 'fg:#ffcc00 bold')
        ])

        page_size = 10
        pages = self.paginate_list(voices, page_size)
        current_page = 0

        while True:
            page = pages[current_page]
            choices = [questionary.Choice(title=v["name"], value=v) for v in page]

            if current_page > 0:
                choices.insert(0, "⬆ Previous Page")
            if current_page < len(pages) - 1:
                choices.append("⬇ Next Page")
            choices.append("Exit")

            selected_voice = questionary.select(
                "Select a Voice:",
                choices=choices,
                pointer="❯",
                style=custom_style
            ).ask()

            if selected_voice == "⬆ Previous Page":
                current_page -= 1
            elif selected_voice == "⬇ Next Page":
                current_page += 1
            elif selected_voice == "Exit" or not selected_voice:
                break
            else:
                while True:
                    action = questionary.select(
                        f"You selected {selected_voice['name']}. What would you like to do?",
                        choices=["Preview Voice", "Select Voice", "Go Back"],
                        pointer="❯",
                        style=custom_style
                    ).ask()

                    if action == "Preview Voice":
                        say(True, selected_voice["description"], voice=selected_voice['name'])  
                        # break
                    elif action == "Select Voice":
                        print(f"You have selected {selected_voice['name']}.")
                        self.voice = selected_voice['name']
                        self.get_or_set_voice('set', voice={'voice': selected_voice['name']})
                        return selected_voice  
                    elif action == "Go Back":
                        break  # Restart voice selection


    def open_gui(self):
        pass    
        # Check if gui exists
        # If it does, open it
        # If it doesn't, ask to download it and thenopen it.
        # Else End

    def select_conversation(self, action=''):
        conversations = self.get_conversations()
        custom_style = questionary.Style([
            ('pointer', 'fg:#00ff00 bold'),  
            ('highlighted', 'fg:#ffcc00 bold')  
        ])
        conversation_map={ i[45:].replace('.json', "") : i for i in conversations if i != 'Conversations/.current_conversation_file_name.txt' }
        print()
        choice = questionary.select(
            f"Select a Conversation {action}:",
            choices=list(conversation_map.keys()),
            pointer="❯",  
            style=custom_style  
        ).ask()
        print("")
        return conversation_map.get(choice)


    def list_conversations(self):
        history = [(idx, self.extract_timestamp(i).replace("_", ""), i, i[45:].replace('.json', "")) for idx, i in enumerate(self.get_conversations()) if i != 'Conversations/.current_conversation_file_name.txt']
        headers = ['No.', 'ID', "File", 'Title']
        print(tabulate(history, headers=headers, stralign="left", numalign="center", tablefmt="pipe"))

    
    

if __name__ == '__main__':
    cli = CLI()
    # cli.new_conversation()
    # cli.open_conversation('20241020152410730023')
    # print(cli.select_conversation())
    # cli.list_conversations()
    # print(cli.search_filter_conversations("Luffy"))
    # print(cli.search_filter_conversations("2025-02-28".replace("-", "")))
    # print(cli.search_filter_conversations("p"))

    # cli.select_main_voice()
    # print(cli.voice)