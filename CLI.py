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
        self.add_argument('-e', '--edit-conversation', type=str, help='Edit a specific conversation by providing its name.')
        self.add_argument('-d', '--delete-conversation', type=str, help='Delete a specific conversation from history by name.')
        self.add_argument('-F', '--search-conversation', type=str, help='Search for a conversation by keyword in an interactive mode.')
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

            elif args.switch_conversation:
                print("Switching to another conversation")
                # Would have to find the conversation to open
                # Would then have to open the conversation


            elif args.list_conversation:
                print("List out all conversations")
                self.list_conversations()

            elif args.clear_conversation:
                print("Clearing All Conversations")
                
            elif args.edit_conversation:
                print("Editting an individual conversation")
                   
            elif args.delete_conversation:
                print("Deleting a single conversation")
                
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
        print(self.ascii_colors.center_block_text(self.ascii_colors.random_color(title)))
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
        # Opening New Conversation

    def open_conversation(self, id):
        pass

    def clear_conversation_history(self):
        pass
        # ask for confirmation 
        # then delete

    def edit_conversation(self, id):
        pass
        # Get exact conversation
        # Edit it's title
        # Save it back

    def delete_conversation(self, id):
        pass
        # Get exact conversation
        # delete it

    def search_filter_conversations(self):
        pass
        # Search for a conversation based on title, id (date), content from conversation
        # Return all results

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
        history = self.utilities.conversation.list_conversation_histories()
        headers = ['No.', 'ID', "File", 'Title']
        print(tabulate(history, headers=headers, stralign="center", numalign="center", tablefmt="pipe"))

    def get_previous_conversation(self):
        return input('Which conversation would you like to switch to? ')

    def select_conversation(self):
        pass

if __name__ == '__main__':
    cli = CLI()
    # cli.new_conversation()
    cli.list_conversations()









