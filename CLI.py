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
import os




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


a = AI_Utilties()
x = AsciiColors()

class CLI(ag.ArgumentParser):
    def __init__(self):
        super().__init__(description="""This command-line interface (CLI) tool offers a range of functionalities, including mathematical calculations, date and time retrieval, web browsing, audio and video downloading from YouTube, and AI-powered features such as chat and media analysis. Users can perform actions like taking screenshots, locking the screen, managing system volume, and more through straightforward commands and options. The program supports both speech and text interactions for an engaging user experience.""", add_help=False)  

        self.subparsers = self.add_subparsers(dest='command', required=False, parser_class=ag.ArgumentParser)

        self.stop_input_thread = threading.Event()
        self.stop_print_thread = threading.Event()

        self.add_arguments()
        self.process_args()
   
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

        # Audio Download subparser
        download_audio = download_subparser.add_parser('audio', help='Downloads audio', description="Downloads audio from the provided link.")
        download_audio.add_argument('link', type=str, help='Link for the audio to download.')
        download_audio.add_argument('-s', '--speed', type=self.validate_speed, default=1.0, help="The speed of the audio to download.")

        # Video Download subparser
        download_video = download_subparser.add_parser('video', help='Downloads video', description="Downloads video from the provided link.")
        download_video.add_argument('link', type=str, help='Link for the video to download.')
        download_video.add_argument('-e', '--extension', type=self.validate_extension, default=1.0, help="This specifies the file type of the video to downlaod.")

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
        chat_parser.add_argument('-tc', '--toggle-conversation', action='store_true', help='Start a new conversation from scratch.')

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
                # Handle audio download
                if args.download == 'audio':
                    if args.link:
                        YoutubeDownloader(False, lambda: "").download_audio(args.link, speed=args.speed)
                    else:
                        print("Error: No link provided for audio download.")
                
                # Handle video download
                elif args.download == 'video':
                    if args.link:
                        YoutubeDownloader(False, lambda: "").download_video(args.link, file_type=args.extension)
                    else:
                        print("Error: No link provided for video download.")
                
                elif args.download == 'show':
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
                        if args.toggle_conversation:
                            self.toggle_conversation()
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
        print(x.center_block_text(x.random_color(title)))
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
            user_speech = a.get_speech_prompt()
            return user_speech, user_speech.split(' ')
        elif text:
            user_text = a.get_text_prompt()
            return user_text, user_text.split(' ')
        
    def show_model_response(self, user_prompt, speech, text):
        response = ai_function_execution(user_prompt, tools, available_functions)
        if speech:
            say(speech, response or "Nothing in response")
        else:
            print(x.color("\nConviva: ", x.GREEN), end="")
            self.print_response(""+x.color(response, x.YELLOW)+"\n")
   
    def start_conversation(self, speech, text):
        print(x.center_block_text(x.random_color(title)))
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
        a.conversation.move_file = True
        print(a.conversation.move_file)
        a.conversation.create_new_conversation()
        print("New Conversation Should Start here!!!")
        a.conversation.move_file = False
        print(a.conversation.move_file)

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



if __name__ == '__main__':
    CLI()




# TODO make so that one can toggle between previous conversation based on an id or title. there should also, be a function that allows the user to create a title, and even update it. also, there should be one that allows the user to view all conversation histories., like a table, with their title, id, file name, first and then last entry. so for the cli, when the user uses -tc, without any title name or id, then i new conversation is created, else, the user is navigated back to the other conversation. all this should be done in the Conversations class.