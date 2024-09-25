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
        super().__init__(description="Your CLI description here")  

        self.stop_input_thread = threading.Event()
        self.stop_print_thread = threading.Event()

        self.add_arguments()
        self.process_args()
    
    def add_arguments(self):
        # Mathematical calculation arguments
        self.add_argument('-m', '--calculate', action='store_true', help="This takes an expression as a string, performs calculations, and returns the result.")
        self.add_argument('--precision', type=int, default=2, help="The number of decimal places to round the result.")
        self.add_argument('--expression', type=str, help="The mathematical expression to calculate.")  # Expression as an optional argument

        # Terminal command argument
        self.add_argument('-o', '--terminal', action='store_true', help='Opens the terminal')

        # Date and time arguments
        self.add_argument('--datetime', action='store_true', help='Tells the current date and time.')
        self.add_argument('--date', action='store_true', help='Tells only the current date.')
        self.add_argument('--time', action='store_true', help='Tells only the current time.')

        # Website and YouTube video arguments
        self.add_argument('-w', '--open-website', action='store_true', help='Opens a website')
        self.add_argument('--link', type=str, help="The link to be opened.")  # Optional link argument

        self.add_argument('-y', '--open-youtube-video', action='store_true', help='Opens a YouTube video.')
        self.add_argument('--video', type=str, help="The video to search and play on YouTube.")  # Optional video argument
    
        self.add_argument('-s', '--screenshot', action='store_true', help='Takes a Screenshot.')
        
        self.add_argument('-g', '--get-volume', action='store_true', help="Get's and display's the volume")
        self.add_argument('-t', '--set-volume', action='store_true', help='Sets the volume')
        self.add_argument('--volume', type=int, help="The volume to set.")  # Optional video argument
        self.add_argument('-x', '--mute-volume', action='store_true', help='Mutes the volume')

        self.add_argument('-l', '--lock-screen', action='store_true', help='locks the screen')

    def process_args(self):
        try:
            args = self.parse_args()

            if args.calculate and args.expression:
                result = calculate(args.expression)
                result_dict = json.loads(result)
                if "result" in result_dict:
                    print(round(result_dict["result"], args.precision))
                else:
                    print("Error:", result_dict.get("error"))
            elif args.terminal:
                open_cmd()
            elif args.datetime:
                print(tell_time(date=True, time=True))
            elif args.date:
                print(tell_time(date=True, time=False))
            elif args.time:
                print(tell_time(date=False, time=True))
            elif args.open_website:
                if args.link:
                    open_website(args.link)
                else:
                    print("Error: No link provided to open a website.")
            elif args.open_youtube_video:
                if args.video:
                    play_video(args.video)
                else:
                    print("Error: No video provided to search on YouTube.")
            elif args.screenshot:
                take_screenshot()
            elif args.get_volume:
                print(get_volume())
            elif args.set_volume:
                if args.volume:
                    set_volume(args.volume)
                else:
                    print("Error: No volume provided .")
            elif args.mute_volume:
                mute_volume()
            elif args.lock_screen:
                lock_screen()
            else:
                self.start_conversation(False, True)

        except Exception as e:
            print(f"An error occurred: {str(e)}")
    

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
                a.conversation.move_file = True
                print(a.conversation.move_file)
                a.conversation.create_new_conversation()
                print("New Conversation Should Start here!!!")
                a.conversation.move_file = False
                print(a.conversation.move_file)
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




if __name__ == '__main__':
    CLI()
