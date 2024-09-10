import customtkinter as ctk
import sounddevice as sd
import librosa
from PIL import Image, ImageTk
import os
import random
import subprocess
import threading
import tkinter as tk




class Pulser(ctk.CTkFrame):
    """
    A class representing a pulsing animation frame with audio playback capabilities.

    Attributes:
        parent (tk.Tk): The parent window.
        speed (int): The speed of the GIF animation.
        speaking (bool): The speaking state of the Pulser.
        color (str): The foreground color of the frame.
        output_file (str): The audio output file.
        y (ndarray): The audio data.
        sr (int): The sample rate of the audio.
    """
    def __init__(self, parent: tk.Tk, border_width: int = 2, border_color: str = 'black', 
                 corner_radius: int = 200, fg_color: str = 'black', width: int = 350, 
                 height: int = 350, speed: int = 50):
        """
        Initialize the Pulser class.

        Args:
            parent (tk.Tk): The parent window.
            border_width (int): The width of the border. Defaults to 2.
            border_color (str): The color of the border. Defaults to 'black'.
            corner_radius (int): The radius of the corners. Defaults to 200.
            fg_color (str): The foreground color. Defaults to 'black'.
            width (int): The width of the frame. Defaults to 350.
            height (int): The height of the frame. Defaults to 350.
            speed (int): The speed of the GIF animation. Defaults to 50.
        """
        self.parent = parent
        background_corner_colors = (self.parent.SECONDARY_COLOR, self.parent.SECONDARY_COLOR, 
                                    self.parent.TERTIARY_COLOR, self.parent.TERTIARY_COLOR)
        super().__init__(parent, border_width=border_width, border_color=border_color, 
                         corner_radius=corner_radius, fg_color=fg_color, width=width, 
                         height=height, background_corner_colors=background_corner_colors)
        self.speed = speed
        self.speaking = False
        self.color = fg_color
        self.output_file = os.path.join(os.getcwd(), 'Sound', 'prompt.aiff')
        self.y, self.sr = librosa.load(self.output_file, sr=None)

        self._create_gif_section()

    def _play(self) -> None:
        """
        Play the audio file and toggle the speaking state.

        Returns:
            None
        """
        self.speaking = not self.speaking
        sd.play(self.y, self.sr)
        sd.wait()
        self.speaking = not self.speaking

    def pack_frame(self) -> 'Pulser':
        """
        Pack the frame and prevent propagation.

        Returns:
            Pulser: The instance of the Pulser class.
        """
        self.pack(expand=True)
        self.pack_propagate(False)
        return self

    def speech(self, text: str) -> None:
        """
        Convert the text to speech and play it.

        Args:
            text (str): The text to be converted to speech.

        Returns:
            None
        """
        subprocess.run(["say", "-o", os.path.join(os.getcwd(), 'Sound', 'prompt.aiff'), text])
        self.y, self.sr = librosa.load(self.output_file, sr=None)
        self._toggle_speech()

    def _toggle_speech(self) -> None:
        """
        Toggle the speech playback in a separate thread.

        Returns:
            None
        """
        threading.Thread(target=self._play).start()

    def _create_gif_section(self) -> None:
        """
        Create the section for displaying the GIF.

        Returns:
            None
        """
        gif_div_ctk = tk.Label(self, text='', bd=0, background='black')
        self._play_gif(gif_div_ctk, self._get_frames(os.path.join(os.getcwd(), 'Images', 'conviva-orb.gif')))
        gif_div_ctk.pack(expand=True)

    def _get_frames(self, img_path: str) -> list:
        """
        Get the frames from the GIF image.

        Args:
            img_path (str): The path to the GIF image.

        Returns:
            list: The frames of the GIF image.
        """
        frames = []
        try:
            with Image.open(img_path) as img:
                while True:
                    try:
                        img.seek(img.tell() + 1)
                        frames.append(img.copy())
                    except EOFError:
                        break
        except Exception as e:
            print("Error:", e)
        return frames

    def _play_gif(self, container: tk.Label, frames: list) -> None:
        """
        Play the GIF animation.

        Args:
            container (tk.Label): The label to display the GIF.
            frames (list): The frames of the GIF image.

        Returns:
            None
        """
        total_delay = 50
        for frame in frames:
            self.parent.after(total_delay, self._next_frame, frame, container, frames)
            total_delay += self.speed
        self.parent.after(total_delay, self._next_frame, frame, container, frames, True)

    def _next_frame(self, frame: Image, container: tk.Label, frames: list, restart: bool = False) -> None:
        """
        Display the next frame of the GIF animation.

        Args:
            frame (Image): The current frame to display.
            container (tk.Label): The label to display the frame.
            frames (list): The frames of the GIF image.
            restart (bool, optional): Whether to restart the animation. Defaults to False.

        Returns:
            None
        """
        if self.speaking:
            x = random.randint(200, 250)
        else:
            x = 200
        if restart:
            self.parent.after(1, self._play_gif, container, frames)
        photo_image = ImageTk.PhotoImage(frame.resize((x, x)))
        container.configure(image=photo_image)
        container.image = photo_image




w = ctk.CTk()


w.PRIMARY_COLOR = "#29174a"
w.SECONDARY_COLOR = "#16082f"
w.TERTIARY_COLOR = "#212052"
w.AUXILIARY_COLOR = "#413468"
w.LESSER_COLOR = "#5376a7"
Pulser(w).speech("Hello")
w.mainloop()