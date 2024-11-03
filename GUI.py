import customtkinter as ctk
import sounddevice as sd
import librosa
from PIL import Image, ImageTk
import os
import random
import subprocess
import threading
import tkinter as tk
from tkinter import PhotoImage

from llm_processing import say




class GUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode('dark')
        self.title('Conviva 2.0')
        self.size = (900, 620)
          

        self.purple_palette = [
            "#E6E6FA",  # Lavender
            "#E0B0FF",  # Mauve
            "#C8A2C8",  # Lilac
            "#9966CC",  # Amethyst
            "#7851A9",  # Royal Purple
            "#9C51B6",  # Purple Plum
            "#673AB7",  # Deep Purple
            "#614051",  # Eggplant
            "#2E003E",  # Midnight Purple
            "#9932CC",  # Dark Orchid
            "#4B0082",  # Indigo
            "#2C003E",  # Dark Grape
            "#1D0033",  # Dark Violet
            "#12002C",  # Deep Eggplant
            "#0D001A"   # Almost Black Purple
        ]




        self.current_page_index = 0
        self.pages = [ self.speech_chat, self.page_two, self.page_three ]



        # Define Some Other shades Of Purple.

        self.geometry(f"{self.size[0]}x{self.size[1]}+{int(self.winfo_screenwidth()/2)-int(self.size[0]/2)}+{int(self.winfo_screenheight()/2)-int(self.size[1]/2)-50}")
       
        self.load_page()


        self.mainloop()

    def load_page(self):
        self.page_frame = tk.Frame(self)
        self.pages[self.current_page_index]()
        self.page_frame.pack(fill='both', expand=True)
        self.nav_buttons()

    def clear_page(self, frame):
        for child in frame.winfo_children():
            child.destroy()

    def speech_chat(self):
        self.speech_chat_frame = tk.Frame(self.page_frame)

        self.side_panel_visible = True



        self.side_panel = tk.Frame(self.speech_chat_frame)
        self.side_panel_content()
        self.side_panel.place(x=0, y=0, relheight=1.0)


        self.main_content = tk.Frame(self.speech_chat_frame, )
        self.main_content_content()
        self.main_content.place_configure(relwidth=1.0, relx=0, rely=0, relheight=1.0)



        self.speech_chat_frame.pack(fill='both', expand=True)

        self.bind("<Command-b>", self.toggle_side_panel)
        self.bind("<Control-b>", self.toggle_side_panel)


    def toggle_side_panel(self, e):
        if self.side_panel_visible:
            # Hide the side panel
            self.side_panel.place_configure(relwidth=0)
            self.main_content.place_configure(relwidth=1.0, relx=0, rely=0, relheight=1.0)
            self.side_panel_visible = False
            self.main_menu_button_visible = True
            self.toggle_main_menu_button()

        else:
            # Show the side panel
            self.side_panel.place_configure(relwidth=0.25)
            self.main_content.place_configure(relx=0.25, relwidth=0.75, rely=0, relheight=1.0)
            self.side_panel_visible = True
            self.main_menu_button_visible = False
            self.toggle_main_menu_button()



    def side_panel_content(self):
        self.menu_image = ctk.CTkImage(
            dark_image=Image.open("Images/Menu.png"), 
            light_image=Image.open("Images/Menu.png") 
        )

        self.new_conversation_image = ctk.CTkImage(
            dark_image=Image.open("Images/NewConversation.png"), 
            light_image=Image.open("Images/NewConversation.png") 
        )

        header = tk.Frame(self.side_panel, background=self.purple_palette[8])

        toggle_button = ctk.CTkButton(header, text='', image=self.menu_image, width=100, fg_color=self.purple_palette[8], hover_color=self.purple_palette[7], command=lambda e=None :self.toggle_side_panel(e))
        toggle_button.place(relx=0, rely=0, relwidth=0.3, relheight=1.0)

        new_conversation = ctk.CTkButton(header, text='', image=self.new_conversation_image, width=100, fg_color=self.purple_palette[8], hover_color=self.purple_palette[7],)
        new_conversation.place(relx=1, rely=0, relwidth=0.3, relheight=1.0, anchor='ne')

        header.place(relx=0, rely=0, relwidth=1, relheight=0.1)

        conversations = ctk.CTkScrollableFrame(self.side_panel, fg_color=self.purple_palette[7])

        for i in range(50):
            tk.Label(conversations, text=str(i+1), background=self.purple_palette[9]).pack(fill='both', pady=10)

        tk.Frame(conversations, height=100, background=self.purple_palette[7]).pack(fill='both')

        conversations.place(relx=0, rely=0.1, relwidth=1, relheight=1)

    def main_content_content(self):
        # Load image and setup header
        self.menu_image = ctk.CTkImage(
            dark_image=Image.open("Images/Menu.png"), 
            light_image=Image.open("Images/Menu.png")
        )

        header = tk.Frame(self.main_content, background=self.purple_palette[10])
        self.maintoggle_button = ctk.CTkButton(header, text='', image=self.menu_image, width=100, 
                                            fg_color=self.purple_palette[8], hover_color=self.purple_palette[7], 
                                            command=lambda e=None: self.toggle_side_panel(e))
        self.maintoggle_button.place(relx=0, rely=0, relwidth=0.3, relheight=1.0)
        header.place(relx=0, rely=0, relwidth=1, relheight=0.1)

        # Setup body
        self.body = tk.Frame(self.main_content, background=self.purple_palette[1])


        self.pulser = Pulser(self, self.body, (self.purple_palette[1], self.purple_palette[1], self.purple_palette[1], self.purple_palette[1]) , corner_radius=200, border_width=2, border_color=self.purple_palette[9]).pack_frame()

        # Initialize widgets but don't pack them yet
        self.prompt = tk.StringVar()

        self.entry_widget = ctk.CTkEntry(self.body, width=500, height=50, corner_radius=50, textvariable=self.prompt)
        self.textbox_widget = ctk.CTkTextbox(self.body, width=500, height=100, corner_radius=10)

        self.entry_widget.focus_set()
        self.textbox_widget.focus_set()

        # Start with the entry widget
        self.entry_widget.pack(pady=20)

        # Bind events
        self.entry_widget.bind("<Key>", self.toggle_prompt_box)
        self.textbox_widget.bind("<Key>", self.toggle_prompt_box)
        self.textbox_widget.bind("<Command-Return>", self.get_prompt_from_text_box)
        self.textbox_widget.bind("<Control-Return>", self.get_prompt_from_text_box)
        self.entry_widget.bind("<Return>", self.get_prompt_from_text_box)

        self.body.place(relx=0, rely=0.1, relwidth=1, relheight=0.9)


    def toggle_prompt_box(self, e):
        current_text = self.prompt.get()
        current_textbox_content = self.textbox_widget.get("1.0", tk.END).strip()

        if len(current_text) > 10 and self.entry_widget.winfo_ismapped():
            # Switch to the textbox
            self.entry_widget.pack_forget()
            self.textbox_widget.delete("1.0", tk.END)  
            self.textbox_widget.insert("1.0", current_text)  # Insert new text
            self.textbox_widget.focus_set()
            self.textbox_widget.pack(pady=20)
        elif len(current_textbox_content) <= 10 and self.textbox_widget.winfo_ismapped():
            # Switch back to the entry widget
            self.textbox_widget.pack_forget()
            self.entry_widget.focus_set()
            self.prompt.set(current_textbox_content)  
            self.entry_widget.pack(pady=20)

    def toggle_main_menu_button(self):
        if self.main_menu_button_visible:
            self.maintoggle_button.place(relx=0, rely=0, relwidth=0.3, relheight=1.0) 
        else:
            self.maintoggle_button.place_forget()

       
    def get_prompt_from_text_box(self, e):
        if self.entry_widget.winfo_ismapped(): 
            prompt = self.prompt.get()
            self.pulser.speech(prompt)
            self.prompt.set("")
        else:
            prompt = self.textbox_widget.get("1.0", tk.END).strip()
            self.pulser.speech(prompt)
            self.textbox_widget.delete("1.0", tk.END) 
            self.prompt.set("")
            self.textbox_widget.pack_forget()
            self.entry_widget.focus_set()
            self.entry_widget.pack(pady=20)


    
   
    def page_two(self):
        self.label = tk.Label(self.page_frame, text='Page Two', background='purple')
        self.label.pack(fill='both', expand=True)
        # self.page_frame.pack()


    def page_three(self):
        self.label = tk.Label(self.page_frame, text='Page Three', background='green')
        self.label.pack(fill='both', expand=True)
        # self.page_frame.pack()


    def nav_buttons(self):
        for idx in range(3):
            nav_button = ctk.CTkButton(
                self.page_frame, 
                text='Page ' + str(idx + 1), 
                command=lambda idx=idx: self.change_page(idx), 
                fg_color=self.purple_palette[-1],
                hover_color=self.purple_palette[4]
            )
            nav_button.pack(side='left', expand=True)



    def change_page(self, idx):
        self.clear_page(self.page_frame)
        self.set_current_page_index(idx)
        self.pages[self.current_page_index]()
        self.page_frame.pack(fill='both', expand=True)
        self.nav_buttons()


    def set_current_page_index(self, index):
        self.current_page_index = index



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
    def __init__(self, parent: tk.Tk, container, bg_corners, border_width: int = 2, border_color: str = 'black', 
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
        background_corner_colors = bg_corners or (self.parent.purple_palette[1], self.parent.purple_palette[1], self.parent.purple_palette[1], self.parent.purple_palette[1]) 
        super().__init__(container, border_width=border_width, border_color=border_color, 
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
        # say(True, text)
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
        # self._play_gif(gif_div_ctk, self._get_frames(os.path.join(os.getcwd(), 'Images', 'conviva-orb.gif')))
        self._play_gif(gif_div_ctk, self._get_frames('Images/GIF2.gif'))
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








if __name__ == "__main__":
    GUI()


# TODO when the app initally loads, it greets the user after some time of silence. that is for the ai page, where the glowing orb would be.