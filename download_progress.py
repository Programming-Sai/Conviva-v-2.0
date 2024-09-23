import sys
import time
from cli_colors import AsciiColors
import numpy 

# ANSI escape codes for colors
COLOR_GREEN = '\033[92m'
COLOR_GREY = '\033[2m'
COLOR_RESET = '\033[0m'

def download_progress_bar(progress, total, bar_length=50):
    """Displays a download-like progress bar."""
    # Calculate the filled portion of the bar
    filled_length = int(bar_length * progress // total)

    # Create the bar: green for the completed part, grey for the remaining part
    bar = f"{COLOR_GREEN}━{COLOR_RESET}" * filled_length + f"{COLOR_GREY}━{COLOR_RESET}" * (bar_length - filled_length)
    bar2 = f"{AsciiColors.RED}━{COLOR_RESET}" * filled_length + f"{COLOR_GREY}━{COLOR_RESET}" * (bar_length - filled_length)

    # Display progress with download info
    sys.stdout.write(f"\r{bar}{COLOR_RESET} {progress}/{total} MB")
    sys.stdout.flush()
    if progress == total:
        print(f"\r{bar2}{COLOR_RESET} {progress}/{total} MB",)
# Example usage to simulate a download
total_size = 9.5 # in MB
for i in numpy.arange(0.0, 1.0, 0.1):
    download_progress_bar(i, total_size)
    time.sleep(0.5)  # Simulate download time
