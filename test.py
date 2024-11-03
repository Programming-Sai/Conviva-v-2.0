# import threading
# import time
# import random
# import sys

# def spinner():
#     """Spinner animation displayed while waiting."""
#     characters = [
#         '⣿', '⠿', '⠾', '⠽', '⠼', '⠻', '⠺', '⠹', '⠸', '⠷', 
#         '⠶', '⠵', '⠴', '⠳', '⠲', '⠱', '⠰', '⠯', '⠮', '⠭', 
#         '⠬', '⠫', '⠪', '⠩', '⠨', '⠧', '⠦', '⠥', '⠤', '⠣', 
#         '⠢', '⠡', '⠠', '⠟', '⠞', '⠝', '⠜', '⠛', '⠚', '⠙', 
#         '⠘', '⠗', '⠖', '⠕', '⠔', '⠓', '⠒', '⠑', '⠐', '⠏', 
#         '⠎', '⠍', '⠌', '⠋', '⠊', '⠉', '⠈', '⠇', '⠆', '⠅', 
#         '⠄', '⠃', '⠂'
#     ]
    
#     while not stop_spinner_event.is_set():
#         for char in characters:
#             if stop_spinner_event.is_set():
#                 break
#             sys.stdout.write(f'\r{char}')
#             sys.stdout.flush()
#             time.sleep(0.5)  # Adjust the speed of the spinner

# def load_data(main_task):
#     """Simulates loading data from the internet."""
#     time.sleep(random.uniform(2, 5))  # Simulate variable loading time
#     result = main_task()  # Call the main task
#     print(f"\nData loaded: {result}")

# def main(main_task):
#     global stop_spinner_event
#     stop_spinner_event = threading.Event()  # Event to control spinner
    
#     # Start the spinner in a separate thread
#     spinner_thread = threading.Thread(target=spinner)
#     spinner_thread.start()
    
#     load_data(main_task)  # Load the data
    
#     stop_spinner_event.set()  # Stop the spinner
#     spinner_thread.join()  # Wait for the spinner thread to finish
#     print("Done!")

# # Example main task function
# def example_task():
#     return "This is the result of the main task."

# # Run the main function with the example task
# if __name__ == "__main__":
#     main(example_task)




print(len("the quick brown fox jumped over the lazy dog. or did it. guess we will now"))