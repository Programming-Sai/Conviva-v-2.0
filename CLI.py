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

        self.stop_input_thread = threading.Event()
        self.stop_print_thread = threading.Event()

        self.conversation = []
        self.conversation_so_far = ''

        self.add_arguments()
        self.process_args()
   
    def cli_title_function(self):
        return input('Please what would you like to name this conversation?  ').replace(' ', '-').replace('_', '-')

    def add_arguments(self):
        self.add_argument('-s', '--speech', action='store_true', help='Start a voice-based AI conversation using speech recognition.')
        self.add_argument('-t', '--text', action='store_true', help='Start a text-based AI conversation where you type messages.')
        self.add_argument('-n', '--new-conversation', action='store_true', help='Create a new conversation session, separate from previous ones.')
        self.add_argument('-a', '--switch-conversation', type=str, help='Switch to a previously saved conversation by providing its name.')
        self.add_argument('-l', '--list-conversation', action='store_true', help='Display all stored conversations with their names and timestamps.')

        # Managing Conversations
        self.add_argument('-c', '--clear-conversation', action='store_true', help='Delete all stored conversations and reset history.')
        self.add_argument('-e', '--edit-conversation', action='store_true', help='Edit a specific conversation by providing its name.')
        self.add_argument('-o', '--open-conversation', action='store_true', help='Open a specific conversation by providing its name.')
        self.add_argument('-d', '--delete-conversation', action='store_true', help='Delete a specific conversation from history by name.')
        self.add_argument('-F', '--search-conversation', action='store_true', help='Search for a conversation by keyword in an interactive mode.')
        self.add_argument('-i', '--search-conversation-interactive', type=str, help='Search for a conversation by keyword in an interactive mode.')
        self.add_argument('-f', '--search-conversation-tabular', type=str, help='Search for a conversation by keyword and display results in tabular format.')

        # Voice Settings
        self.add_argument('-v', '--select-voice', type=str, help='Choose a specific voice for AI responses by providing a voice ID or name.')
        self.add_argument('-p', '--preview-voice', action='store_true', help='Listen to a short sample of the currently selected AI voice.')
        
        # Calling GUI
        self.add_argument('--gui', action='store_true', help='Opening GUI')



        # Clear current conversation on each switch
        # Uploading images and audio files
        # Find conversations by date, name, content(use sparingly)
        # Add a customized system prompt.

        

    def process_args(self):
        try:
            print()
            args = self.parse_args()
            if  args.speech:
                self.start_conversation(True, False)

            elif args.text:
                self.start_conversation(False, True)
            
            elif args.new_conversation:
                print("Creating a new conversation")
                self.new_conversation()


            elif args.list_conversation:
                print("List out all conversations")
                self.list_conversations()

            elif args.open_conversation:
                print("Open a Conversation")
                self.open_conversation(self.extract_timestamp(self.select_conversation(action='To Open')).replace("_", ""))

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

                   
            elif args.select_voice:
                print("Selecting all voices")
                
            elif args.preview_voice:
                print("Preview a voice")
            
            elif args.gui:
                print("Opening GUI")
                
            else:
                # self.start_conversation(False, True)
                print("Would Default to Convo")
            print()
            return
        except Exception as e:
            print(f'\n\nSomething went Wrong. This Was The issue: {e}')




    def handle_audio_or_image_analysis(self, function, file_parameter):
        print("Please Enter Your Prompt Here (Ctrl+D to end): \n\n")
        prompt = sys.stdin.read()


        global stop_spinner_event
        stop_spinner_event = threading.Event()  # Event to control spinner

        # Start the spinner in a separate thread
        spinner_thread = threading.Thread(target=self.spinner)
        spinner_thread.start()


        result = function(prompt, file_parameter)


        stop_spinner_event.set()  # Stop the spinner
        spinner_thread.join()  # Wait for the spinner thread to finish
       
        print(result)

    def get_user_input(self, speech, text):
        if speech:
            user_speech = self.utilities.get_speech_prompt()
            return user_speech, user_speech.split(' ')
        elif text:
            user_text = self.utilities.get_text_prompt()
            return user_text, user_text.split(' ')
                
    def show_model_response(self, user_prompt, speech, text):
        response = ai_function_execution(user_prompt, tools, available_functions, self.utilities)
        if speech:
            say(speech, response or "Nothing in response")
        else:
            print(self.ascii_colors.color("\nConviva: ", self.ascii_colors.GREEN), end="")
            self.print_response(""+self.ascii_colors.color(response, self.ascii_colors.YELLOW)+"\n")
   


    def start_conversation(self, speech, text):
        if not self.get_conversations():
            self.new_conversation()
            return 
        print(self.ascii_colors.center_block_text(self.ascii_colors.random_color(title)))
        print(self.conversation_so_far)
        while True:
            user_prompt = self.get_user_input(speech, text)[0]
            if user_prompt.lower() in ['x', 'exit'] or self.end_convo:
                break
            elif user_prompt.lower() == 'c':
                self.new_conversation()
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
            # print(self.conversation_so_far)
            self.end_convo=False
            self.start_conversation(False,  True)
            print("Starting Convo")
        except:
            # Resetting conversation data in case of an error
            self.utilities.conversation.conversation_history = []
            self.conversation = self.utilities.conversation.conversation_history
            self.new_conversation()
            self.end_convo=False
            self.start_conversation(False, True)

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
                


    def delete_conversation(self, file_path):
        if input(f"Are you sure that you want to delete {file_path[45:].replace('.json', "")} (Y/n): ").lower() == 'y':
            try:
                os.remove(file_path)
                print(f"{file_path[45:].replace('.json', "")} has been deleted successfully")
            except Exception as e:
                print("Sorry This Error has occured: ", e)
        

    def edit_conversation(self, file_path):
        if input(f"Are you sure that you want to rename {file_path[45:].replace('.json', "")} (Y/n): ").lower() == 'y':
            try:
                old = file_path
                new = f"Conversations/conviva_20250228_175438_071642_{input("Enter the New Conversation Title").replace(" ", "-")}.json"
                os.rename(old, new)
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
        pass    
        # Get all voices and return them

    def select_main_voice(self, id):
        pass
        # get all voices
        # select and save chosen voice

    def preview_voice(self, id):
        pass
        # Preview given voice

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


    def spinner(self):
        """Spinner animation displayed while waiting."""
        characters = [
            '⠻', '⠿', '⠽', '⠻', '⠺', '⠹', '⠸', '⠷', 
            '⠶', '⠵', '⠴', '⠳', '⠲', '⠱', '⠰', '⠯', 
            '⠮', '⠭', '⠬', '⠫', '⠪', '⠩', '⠨', '⠧', 
            '⠦', '⠥', '⠤', '⠣', '⠢', '⠡', '⠠', '⠟', 
            '⠞', '⠝', '⠜', '⠛', '⠚', '⠙', '⠘', '⠗', 
            '⠖', '⠕', '⠔', '⠓', '⠒', '⠑', '⠐', '⠏', 
            '⠎', '⠍', '⠌', '⠋', '⠊', '⠉', '⠈', '⠇', 
            '⠆', '⠅', '⠄', '⠃', '⠂'
        ]

        
        while not stop_spinner_event.is_set():
            print('\n')
            for char in characters:
                if stop_spinner_event.is_set():
                    print('\n\n')
                    break
                sys.stdout.write(f'\r{char}')
                sys.stdout.flush()
                time.sleep(0.5) 

    def list_conversations(self):
        history = [(idx, self.extract_timestamp(i).replace("_", ""), i, i[45:].replace('.json', "")) for idx, i in enumerate(self.get_conversations()) if i != 'Conversations/.current_conversation_file_name.txt']
        headers = ['No.', 'ID', "File", 'Title']
        print(tabulate(history, headers=headers, stralign="left", numalign="center", tablefmt="pipe"))

    def get_previous_conversation(self):
        return input('Which conversation would you like to switch to? ')

    

if __name__ == '__main__':
    cli = CLI()
    # cli.new_conversation()
    # cli.open_conversation('20241020152410730023')
    # print(cli.select_conversation())
    # cli.list_conversations()
    # print(cli.search_filter_conversations("Luffy"))
    # print(cli.search_filter_conversations("2025-02-28".replace("-", "")))
    # print(cli.search_filter_conversations("p"))


