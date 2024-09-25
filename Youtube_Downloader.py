import json
import math
import os
import random
import socket
import subprocess
import time
import sys
from datetime import datetime
from typing import List, Union
import platform
import yt_dlp
from yt_dlp import YoutubeDL
import logging
import ssl
from cli_colors import AsciiColors
import re


logging.basicConfig(
    filename='conviva_app.log',  # Log file name
    level=logging.DEBUG,  # Log level
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
    datefmt='%Y-%m-%d %H:%M:%S'  # Date format
)





def say(speak: bool, text: str) -> str:
    """
    Speak the given text if the 'speak' flag is True.

    Args:
        speak (bool): Flag to determine whether to speak the text.
        text (str): The text to be spoken.

    Returns:
        str: The input text.
    """
    if speak:
        if platform.system() == 'Darwin':  # macOS
            subprocess.run(["say", "-o", 'prompt.aiff', text])
            ALLOWED_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 /-.,?_!@$%^&*()#|")
            clean_text = ''.join(c for c in text if c in ALLOWED_CHARS)
            subprocess.run(["say", clean_text])
        # elif platform.system() == 'Windows':  # Windows
        #     engine = pyttsx3.init()
        #     engine.say(text)
        #     engine.runAndWait()
    return text


class YoutubeDownloader:
    """
    A class to interact with YouTube and download videos or audio.

    Attributes:
        link (str): The YouTube video link.
        speak (bool): Flag to determine whether to speak prompts.
        say (callable): A function to speak text.
    """

    def __init__(self, speak: bool, say: callable):
        """
        Initialize the YoutubeDownloader object.

        Args:
            speak (bool): Flag to determine whether to speak prompts.
            say (callable): A function to speak text.
        """
        self.link = ''
        self.speak = speak
        self.say = say
        self.progress = 0
        self.total_size = 0
        self.download_speed = ''
        self.time_elapsed = ''

    def get_link(self) -> str:
        """
        Prompt the user to enter a valid YouTube video link.

        Returns:
            str: The entered YouTube video link.
        """
        while True:
            link = input("Please Enter Link For The Video to Work With... ")
            if "https://www.youtube.com/watch?v=" in link:
                return link
            else:
                print("Invalid Youtube Link")
                continue

    def is_internet_connected(self) -> bool:
        """
        Check if the device is connected to the internet.

        Returns:
            bool: True if connected, False otherwise.
        """
        try:
            socket.create_connection(("www.google.com", 80))
            return True
        except OSError:
            return False

    def fetch_suggestions(self, query: str) -> List[str]:
        """
        Fetch search suggestions based on the given query.

        Args:
            query (str): The search query.

        Returns:
            List[str]: List of search suggestions.
        """
        ydl_opts = {
            'default_search': 'auto',
            'format': 'bestaudio/best',
            'quiet': True,
            'extract_flat': True,
            'extractor_args': {'search': query}
        }

        with YoutubeDL(ydl_opts) as ydl:
            if not query.strip():
                return []
            else:
                result = ydl.extract_info(f'ytsearch{random.randint(5, 10)}:' + query, download=False)
                if 'entries' in result:
                    suggestions = [entry['title'] for entry in result['entries']]
                    return suggestions
                else:
                    return []

    def get_video_details(self, video_id: str) -> dict:
        """
        Fetch details of a YouTube video.

        Args:
            video_id (str): The ID of the YouTube video.

        Returns:
            dict: Dictionary containing details of the video.
        """
        ydl_opts = {
            'quiet': True,
            'print_json': True,
            'extract_flat': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            video_info = ydl.extract_info(video_id, download=False)
        return video_info

    def save_as_json(self, data: Union[dict, list], filename: str) -> None:
        """
        Save data as JSON to a file.

        Args:
            data (Union[dict, list]): Data to be saved.
            filename (str): Name of the file to save the data to.
        """
        with open(filename, 'w') as json_file:
            json.dump(data, json_file, indent=4)

    def format_audio_length(self, seconds: int) -> str:
        """
        Format duration in seconds to a human-readable format (HH:MM:SS).

        Args:
            seconds (int): Duration in seconds.

        Returns:
            str: Formatted duration string.
        """
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{'0' if hours < 10 and hours > 0 else ''}{str(hours)+':' if hours > 0 else ''}{'0' if minutes < 10  else ''}{str(minutes)+':'}{'0' if seconds < 10 else ''}{seconds}"

    def format_upload_date(self, upload_date: str) -> str:
        """
        Format the upload date of a video to a human-readable format.

        Args:
            upload_date (str): The upload date string in the format 'YYYYMMDD'.

        Returns:
            str: The formatted upload date string in the format 'DD/MM/YYYY'.
        """
        date_object = datetime.strptime(upload_date, "%Y%m%d")
        return date_object.strftime("%d/%m/%Y")

    def search_videos(self, query: str, max_result: int) -> List[dict]:
        """
        Search YouTube videos based on the given query.

        Args:
            query (str): The search query.
            max_result (int): The maximum number of search results to retrieve.

        Returns:
            List[dict]: A list of dictionaries containing details of the search results.
        """
        try:
            search_query = f'ytsearch{max_result}:{query}'
            ydl_opts = {
                'default_search': 'auto',
                'skip_download': True,
                'quiet': True,
                'print_json': True,
                'extract_flat': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                search_results = ydl.extract_info(search_query, download=False)
            
            if not search_results or 'entries' not in search_results:
                print("No search results found.")
                return []
            
            processed_results = []
            id_count = 0
            for entry in search_results['entries']:
                video_id = entry.get('id')
                video_info = self.get_video_details(video_id)
                
                # Extract required fields from video_info
                processed_entry = {
                    'id': f"{'00' if id_count < 10 else  '' if id_count > 99 else '0' }{id_count}",
                    'title': video_info.get('title'),
                    'largest_thumbnail': max(video_info.get('thumbnails', []), key=lambda t: t.get('height', 0) * t.get('width', 0)).get('url'),
                    'smallest_thumbnail': min(video_info.get('thumbnails', []), key=lambda t: t.get('filesize', float('inf'))).get('url'),
                    'url': video_info.get('webpage_url'),
                    'audio_length': self.format_audio_length(video_info.get('duration')),
                    'channel_name': video_info.get('uploader'),
                    'upload_date': self.format_upload_date(video_info.get('upload_date'))
                }
                processed_results.append(processed_entry)
                id_count += 1
            
            return processed_results
        except:
            return []

    # def download_video(self, link: str = None, progress_hook: callable = None) -> str:
    def download_video(self, link) -> str:
        """
        Download a YouTube video.

        Args:
            link (str, optional): The YouTube video link to download. Defaults to None.
            progress_hook (callable, optional): A progress hook function. Defaults to None.

        Returns:
            str: Success message or error message if there is no internet connection.
        """
        # try:
        ydl_opts = {
            'quiet': True,
            'progress_hooks': [self.progress_hook],
            'format': 'bestvideo+bestaudio/best',  
            # '--no-check-certificates': True, # Uncomment this when the SSL error arises
            'ssl_context': ssl._create_unverified_context(),
            'outtmpl': os.path.join('Downloads', '%(title)s.%(ext)s'),  # Save to a 'downloads' folder
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.link if link is None else link])
        logging.info(f"{os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Downloads')}  {'%(title)s.%(ext)s'} Successfully ---Video")
        return 'Success'
        # except:
        #     logging.info(f"Failed to Download {'%(title)s.%(ext)s'} ---Video")
        #     return "Sorry, There is no internet connection"

    # def download_audio(self, link: str = None, progress_hook: callable = None) -> str:
    
    def download_audio(self, link, speed = 1.25) -> str:
        """
        Download the audio of a YouTube video.

        Args:
            link (str, optional): The YouTube video link to download. Defaults to None.
            progress_hook (callable, optional): A progress hook function. Defaults to None.

        Returns:
            str: Success message or error message if there is no internet connection.
        """
        try:
            ydl_opts = {
                'quiet': True,
                'progress_hooks': [self.progress_hook],
                # '--no-check-certificates': True, # Uncomment this when the SSL error arises
                'ssl_context': ssl._create_unverified_context(),
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'postprocessor_args': [
                    '-filter:a', f'atempo={speed}'  # Change playback speed using atempo filter
                ],
                    'outtmpl': os.path.join('Downloads', '%(title)s.%(ext)s'),  # Save to a 'downloads' folder
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.link if link is None else link])
        


        
            logging.info(f"{os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Downloads')} {'%(title)s.%(ext)s'} Successfully ---Audio")
            return 'Success'
        except Exception as e:
            logging.info(f"Failed to Download {'%(title)s.%(ext)s'} ---Audio")
            print(e)
            return "Sorry, There is no internet connection"


    def cli_progress_animation(self, progress, total, bar_length=50, final=False):
        """Displays a download-like progress bar."""
        # Calculate the filled portion of the bar
        filled_length = int(bar_length * progress // 100)
        colors = AsciiColors()

        # Create the bar: green for the completed part, grey for the remaining part
        bar = colors.color("━", colors.BLUE) * filled_length + colors.color("━", colors.DIM) * (bar_length - filled_length)

        # Display progress with download info
        if final:
            # Print final bar without overwriting
            print(f"\r{bar} {round((progress/100) * total, 1)}/{round(total, 1)} MB - Download Complete")
        else:
            sys.stdout.write(f"\r{bar} {round((progress/100) * total, 1)}/{round(total, 1)} MB")
            sys.stdout.flush()

        

    def progress_hook(self, d: dict) -> None:
            """
            A callback function to update the download progress.

            Args:
                d (dict): The download status dictionary.
            """
            try:
                if d['status'] == 'downloading':
                    percent_str = re.sub(r'\x1b\[[0-9;]*m', '', d['_percent_str'])
                    speed_str = re.sub(r'\x1b\[[0-9;]*m', '', d['_speed_str'])
                    elapsed_str = re.sub(r'\x1b\[[0-9;]*m', '', d['_elapsed_str'])
                    total_size_str = re.sub(r'\x1b\[[0-9;]*m', '', d['_total_bytes_str'])
                    if percent_str.strip().endswith('%'):
                        self.progress = (float(float(percent_str.replace('%', ''))))
                        self.total_size = (float(float(total_size_str.strip().replace('MiB', '')))) * 1.048576
                        self.time_elapsed = elapsed_str
                        self.download_speed = speed_str
                        self.cli_progress_animation(self.progress, self.total_size)
                elif d['status'] == 'finished':
                    # Print the final bar when the download is complete
                    self.cli_progress_animation(100, self.total_size, final=True)
            except:
                raise ValueError







# c = YoutubeDownloader(False, say)







# (.conviva-venv) mac@Sai Ai % pip install certifi                          
# Requirement already satisfied: certifi in /Users/mac/.conviva-venv/lib/python3.10/site-packages (2024.6.2)
# (.conviva-venv) mac@Sai Ai % /Applications/Python\ 3.10/Install\ Certificates.command
#  -- pip install --upgrade certifi
# Requirement already satisfied: certifi in /Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/site-packages (2024.2.2)
# Collecting certifi
#   Using cached certifi-2024.6.2-py3-none-any.whl.metadata (2.2 kB)
# Using cached certifi-2024.6.2-py3-none-any.whl (164 kB)
# Installing collected packages: certifi
#   Attempting uninstall: certifi
#     Found existing installation: certifi 2024.2.2
#     Uninstalling certifi-2024.2.2:
#       Successfully uninstalled certifi-2024.2.2
# Successfully installed certifi-2024.6.2
#  -- removing any existing file or link
#  -- creating symlink to certifi certificate bundle
#  -- setting permissions
#  -- update complete
# (.conviva-venv) mac@Sai Ai % 