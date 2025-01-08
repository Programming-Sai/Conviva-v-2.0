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
import json
from utility_functions import *
from Youtube_Downloader import YoutubeDownloader
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


        self.utilities = AI_Utilties(Conversation(self.cli_title_function))
        self.ascii_colors = AsciiColors()

        self.subparsers = self.add_subparsers(dest='command', required=False, parser_class=ag.ArgumentParser)

        self.stop_input_thread = threading.Event()
        self.stop_print_thread = threading.Event()

        self.add_arguments()
        self.process_args()
   
    def cli_title_function(self):
        return input('Please what would you like to name this conversation?  ').replace(' ', '-').replace('_', '-')

    def add_arguments(self):

        # Standalone Commands
        self.add_argument('-t', '--terminal', action='store_true', help='Opens the terminal')
        self.add_argument('-s', '--screenshot', action='store_true', help='Takes a Screenshot.')
        self.add_argument('-f', '--file-path', type=str, default='screenshot', help='Takes a Screenshot and stores it in a given file..')        
        self.add_argument('-l', '--lock-screen', action='store_true', help='locks the screen')
        self.add_argument('-m', '--manual', action='store_true', help='Show help information for all commands.')
        
        # Math Parser
        math_parser = self.subparsers.add_parser('calc', help="Perform basic mathematical operations", description="Performs calculations based on mathematical expressions.")
        math_parser.add_argument('expression', type=str, help="This is the matimatical expression to be operated on.")
        math_parser.add_argument('-p', '--precision', type=int, help='Specifies the number of decimal places that a value should fall under. it defaults to 0', default=0)


        # Date and Time Parser
        datetime_parser = self.subparsers.add_parser('datetime', help='Returns the current date or time', description="Returns the current date and/or time.")
        datetime_parser.add_argument('-t', '--time', action='store_true', help='This determines if the time is needed.')
        datetime_parser.add_argument('-d', '--date', action='store_true', help='This determines if the date is needed.')

        # Website 
        website_parser = self.subparsers.add_parser('url', help='Opens a website based on a given link', description="Opens the provided website link.")
        website_parser.add_argument('link', type=str, help='This is the link to be opened')
        
        # Adding YouTube parser
        youtube_parser = self.subparsers.add_parser('youtube', help='Performs some basic YouTube operations', description="Performs actions related to YouTube such as downloading videos.")


        # Subparsers for download options (audio/video download)
        download_subparser = youtube_parser.add_subparsers(dest='download', help='Download options for YouTube')

        # This argument is used for opening a video without downloading
        show_video = download_subparser.add_parser('show', help='Opens the video on Youtube', description="Opens the video on Youtube")
        show_video.add_argument('video_name', type=str, help='Name Of the video to open.')

        # Volume Manupulation
        volume_subparser = self.subparsers.add_parser('volume', help='Manages the volume of the system.', description="Manages system volume, allowing you to get, set, or mute the volume.")
        volume_subparser.add_argument('-g', '--get-volume', action='store_true', help="Get's and display's the volume")
        volume_subparser.add_argument('-s', '--set-volume', type=int, metavar='VOLUME', help='Sets the volume. Usage: -s <volume>')
        volume_subparser.add_argument('-x', '--mute-volume', action='store_true', help='Mutes the volume')

        # Ai Chat and Other stuff
        ai_subparser = self.subparsers.add_parser('ai', help='Provides various AI-powered features like chat and speech synthesis.')
        ai_subparser_subparsers = ai_subparser.add_subparsers(dest='subcommand')  # Create subparsers for the 'ai' command
        
        # Chat subcommand
        chat_parser = ai_subparser_subparsers.add_parser('chat', help="Start an AI-powered chat conversation. Use '--speech' or '--text' for interaction type.")
        chat_parser.add_argument('-s', '--speech', action='store_true', help='Initiate the conversation with speech recognition and AI responses.')
        chat_parser.add_argument('-t', '--text', action='store_true', help='Start a text-based conversation with AI for typing messages.')
        chat_parser.add_argument('-cc', '--create-conversation', action='store_true', help='Start a new conversation from scratch.')
        chat_parser.add_argument('-sc', '--switch-conversation', type=str, help='Switch to a previous conversation.')
        chat_parser.add_argument('-lc', '--list-conversation', action='store_true', help='Show all conversations')

        # AI image analysis
        image_subparser = ai_subparser_subparsers.add_parser('ai-image', help="Use AI to analyze an image and return insights or features.")
        image_subparser.add_argument('image', nargs='?', type=str, help='Path to the image for analysis.')

        # AI audio analysis
        audio_subparser = ai_subparser_subparsers.add_parser('ai-audio', help="Use AI to analyze an audio clip and return insights or features.")
        audio_subparser.add_argument('audio', type=str, help='Path to the audio file to be analyzed by AI.')

    def process_args(self):
        try:
            print()
            args = self.parse_args()
            if   args.terminal:
                open_cmd()
                print('Terminal Opened')
            elif args.screenshot:
                if args.file_path:
                    print(take_screenshot(file_path=args.file_path))
            elif args.lock_screen:
                print(lock_screen())
            elif args.manual:
                self.print_all_help()
            elif args.command == 'calc':
                if args.expression:
                    result = calculate(args.expression)
                    result_dict = json.loads(result)
                    if "result" in result_dict:
                        print(round(result_dict["result"], args.precision))
                else:
                    print("Error:", result_dict.get("error"))
            elif args.command == 'datetime':
                if args.date:
                    print(tell_time(date=True, time=False))
                elif args.time:
                    print(tell_time(date=False, time=True))
                else:
                    print(tell_time(date=True, time=True))
            elif args.command == 'url':
                if args.link:
                    open_website(args.link)
                    print(f'{args.link} Opened')
                else:
                    print("Error: No link provided to open a website.")    
            elif args.command == 'youtube':
                if args.download == 'show':
                    if args.video_name:
                        play_video(args.video_name)  
                        print(f'{args.video_name} Opened on YouTube')
                    else:
                        print("Error: No video provided to show.")
                # Error if no command is provided
                else:
                    print("Error: No valid command provided. Provide a video, link or download option.")
            elif args.command == 'volume':
                if args.get_volume:
                    print(get_volume())
                elif args.set_volume:
                        set_volume(args.set_volume)
                        print(f'Volume Set To {args.set_volume}')
                elif args.mute_volume:
                    print(mute_volume())      
            elif args.command == 'ai':
                if args.subcommand == 'chat':
                    if args.speech or args.text:
                        if args.create_conversation:
                            self.toggle_conversation()
                        elif args.switch_conversation:
                            success  = self.utilities.conversation.switch_conversation(args.switch_conversation)
                            if success == 'Failed':
                                print(f'Sorry {self.ascii_colors.color(args.switch_conversation, self.ascii_colors.ITALIC)} does not exist')
                            else:
                                print(f'Conversation Switched From {self.ascii_colors.color(self.utilities.conversation.current_file_name, self.ascii_colors.ITALIC)} to {self.ascii_colors.color(args.switch_conversation, self.ascii_colors.ITALIC)} Successfully')
                        elif args.list_conversation:
                            self.list_conversations()
                        else:
                            self.start_conversation(args.speech, args.text)
                    else:
                        print("Please specify an interaction mode with --speech or --text.")
                elif args.subcommand == 'ai-image':
                    if args.image:
                        self.handle_audio_or_image_analysis(ai_image_analysis, args.image)
                    else:
                        print('No image provided for ai analysis')

                elif args.subcommand == 'ai-audio':
                    if args.audio:
                        self.handle_audio_or_image_analysis(ai_sound_analysis, args.audio)
                    else:
                        print('Error: No audio file provided for AI analysis.')
            else:
                self.start_conversation(False, True)
            print()
            return
        except Exception as e:
            print(f'\n\nSomething went Wrong. This Was The issue: {e}')

    def validate_speed(self, value):
        value = float(value)
        if value < 0 or value > 2:
            raise ag.ArgumentTypeError("Speed must be between 0 and 2.")
        return value
 
    def validate_extension(self, extension):
        video_file_extensions = ['mp4', 'mkv', 'webm', 'avi', 'mov', 'flv', 'wmv']
        if extension in video_file_extensions:
            return extension
        else:
            print(f"\nSorry {extension} is either not supprted or invalid. Using Default\n")
            return None

    def print_all_help(self):
        print(self.ascii_colors.center_block_text(self.ascii_colors.random_color(title)))
        print('\n\n', self.format_help())
        print("\nAvailable commands and options:")
        for action in self._actions:
            if action.dest != 'command':
                print(f"  {action.dest}: {action.help}")

        # Print subcommands and their options
        for subparser in self.subparsers.choices.values():
            print(f"\nSubcommand: {subparser.prog}")
            print(f"  Help: {subparser.description}")
            for sub_action in subparser._actions:
                print(f"    {sub_action.dest}: {sub_action.help}")
        print('\n\n')

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
        response = ai_function_execution(user_prompt, tools, available_functions)
        if speech:
            say(speech, response or "Nothing in response")
        else:
            print(self.ascii_colors.color("\nConviva: ", self.ascii_colors.GREEN), end="")
            self.print_response(""+self.ascii_colors.color(response, self.ascii_colors.YELLOW)+"\n")
   


    def start_conversation(self, speech, text):
        print(self.ascii_colors.center_block_text(self.ascii_colors.random_color(title)))
        while True:
            user_prompt = self.get_user_input(speech, text)[0]
            if user_prompt.lower() in ['x', 'exit']:
                break
            elif user_prompt.lower() == 'c':
                self.toggle_conversation()
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

    def toggle_conversation(self):
        self.utilities.conversation.move_file = True
        self.utilities.conversation.create_new_conversation()
        print("New Conversation Should Start here!!!")
        self.utilities.conversation.move_file = False

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

if __name__ == '__main__':
    CLI()




# TODO Make it so that one can select -lc, or the others also without specifying the interaction mode.
# TODO Modify code so that it run on Windows as well.
# TODO make it so that any task that could take a longer period of time is run on a different thread. now while that is running the ai model, would get an additional string that would force it to call a function to check if the result is in. this would continue while the background operation is still in fluself.ascii_colors. when it is done, it stops adding that extra string.
# TODO Check on how to atart and stop a thread. OR you can write a function to handle that for you.
# TODO Find out how to do websrcapping without showing your ip address (i think it is called proxy something.)
