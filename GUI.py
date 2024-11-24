import customtkinter as ctk
import sounddevice as sd
import librosa
from PIL import Image, ImageTk
import os
import random
import subprocess
import threading
import tkinter as tk
from tkinter import PhotoImage, TclError
import time
from llm_processing import say
from tkinterdnd2 import TkinterDnD, DND_ALL
from pathlib import Path






class GUI(TkinterDnD.Tk):  # Multiple inheritance
    def __init__(self):
        # Initialize both parent classes
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

        self.file_type_colors = {
            'txt': 'blue',
            'md': 'gray',
            'png': 'blue',
            'jpg': 'blue',
            'jpeg': 'blue',
            'pdf': 'red',
            'doc': 'blue',
            'docx': 'blue',
            'xls': 'green',
            'xlsx': 'green',
            'ppt': 'purple',
            'pptx': 'purple',
            'mp3': 'yellow',
            'wav': 'yellow',
            'mp4': 'blue',
            'avi': 'green',
            'mkv': 'green',
            'zip': 'green',
            'rar': 'yellow',
            'exe': 'red',
            'bat': 'red',
            'html': 'blue',
            'htm': 'blue',
            'py': 'green',
            'js': 'blue',
            'java': 'blue'
        }

        self.current_page_index = 0
        self.file_tag = None
        self.pages = [ self.speech_chat, self.text_chat, ]

        # Define Some Other shades Of Purple.

        self.geometry(f"{self.size[0]}x{self.size[1]}+{int(self.winfo_screenwidth()/2)-int(self.size[0]/2)}+{int(self.winfo_screenheight()/2)-int(self.size[1]/2)-50}")
       
        self.page_frame = tk.Frame(self)
        
        self.speech_chat_frame = tk.Frame(self.page_frame)
        self.main_speech_content = tk.Frame(self.speech_chat_frame, )
        self.speech_body = tk.Frame(self.main_speech_content, background=self.purple_palette[1])

        self.text_chat_frame = tk.Frame(self.page_frame)
        self.main_text_content = tk.Frame(self.text_chat_frame, )
        self.text_body = tk.Frame(self.main_text_content, background=self.purple_palette[8])

        self.load_page()
        
        self.bind("<Command-b>", self.toggle_side_panel)
        self.bind("<Control-b>", self.toggle_side_panel)
        self.bind("<Configure>", self.on_resize)

        self.mainloop()





    def load_page(self):
        self.pages[self.current_page_index]()
        self.page_frame.pack(fill='both', expand=True)
        self.nav_buttons()

    def clear_page(self, frame):
        for child in frame.winfo_children():
            child.destroy()

    def speech_chat(self):
        try:
            self.speech_chat_frame = tk.Frame(self.page_frame)
            self.side_panel_creator(self.speech_chat_frame)
            self.main_speech_content = tk.Frame(self.speech_chat_frame, )
            self.main_speech_content_content()
            self.main_speech_content.place_configure(relwidth=1.0, relx=0, rely=0, relheight=1.0)
            self.speech_chat_frame.pack(fill='both', expand=True)
        except:
            print("Not In Existance (Speech Chat)")

    def side_panel_creator(self, frame):
        self.side_panel_visible = True
        self.side_panel = tk.Frame(frame)
        self.side_panel_content()
        self.side_panel.place(x=0, y=0, relheight=1.0)

    def toggle_side_panel(self, e):
        if self.side_panel_visible:
            # Hide the side panel
            self.side_panel.place_configure(relwidth=0)

            if self.main_speech_content is not None and self.main_speech_content.winfo_exists():
                self.main_speech_content.place_configure(relwidth=1.0, relx=0, rely=0, relheight=1.0)
            if self.main_text_content is not None and self.main_text_content.winfo_exists():
                self.main_text_content.place_configure(relwidth=1.0, relx=0, rely=0, relheight=1.0)

            self.side_panel_visible = False
            self.main_menu_button_visible = True
            self.toggle_main_menu_button()

        else:
            # Show the side panel
            self.side_panel.place_configure(relwidth=0.25)
            if self.main_speech_content is not None and self.main_speech_content.winfo_exists():
                self.main_speech_content.place_configure(relx=0.25, relwidth=0.75, rely=0, relheight=1.0)
            if self.main_text_content is not None and self.main_text_content.winfo_exists():
                self.main_text_content.place_configure(relx=0.25, relwidth=0.75, rely=0, relheight=1.0)
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

    def main_speech_content_content(self):
        # Load image and setup header
        self.topbar(self.main_speech_content)

        # Setup body
        self.speech_body = tk.Frame(self.main_speech_content, background=self.purple_palette[1])

        self.pulser = Pulser(self, self.speech_body, (self.purple_palette[1], self.purple_palette[1], self.purple_palette[1], self.purple_palette[1]) , corner_radius=200, border_width=2, border_color=self.purple_palette[9]).pack_frame()

        self.pulser.drop_target_register(DND_ALL)
        self.pulser.dnd_bind('<<Drop>>', self.handleDropEvent)

        
        # Initialize widgets but don't pack them yet
        self.chatbar(self.speech_body)

        self.speech_body.place(relx=0, rely=0.1, relwidth=1, relheight=0.9)

    def topbar(self, frame):
        self.menu_image = ctk.CTkImage(
            dark_image=Image.open("Images/Menu.png"), 
            light_image=Image.open("Images/Menu.png")
        )

        header = tk.Frame(frame, background=self.purple_palette[10])
        self.maintoggle_button = ctk.CTkButton(header, text='', image=self.menu_image, width=100, 
                                            fg_color=self.purple_palette[8], hover_color=self.purple_palette[7], 
                                            command=lambda e=None: self.toggle_side_panel(e))
        self.maintoggle_button.place(relx=0, rely=0, relwidth=0.3, relheight=1.0)
        header.place(relx=0, rely=0, relwidth=1, relheight=0.1)





    def handleDropEvent(self, e):
        frame = e.widget  
        data = e.data.strip("{}")
        file_extension = Path(data).suffix.replace('.', '').upper()
        # Determine the label color based on file type
        color = self.file_type_colors.get(file_extension.lower(), 'gray')  # Default to gray if not found
        try:
            if not self.file_tag or not self.file_tag.winfo_exists():  # Create the label if it doesn't exist
                self.file_tag = ctk.CTkLabel(
                    self.speech_body if self.speech_body.winfo_exists() else self.text_body if self.text_body.winfo_exists() else frame,  # Or the relevant parent frame
                    font=('Arial Black', 16, 'bold'),
                    width=50,
                    height=70,
                    corner_radius=20,
                    text=file_extension,
                    fg_color=color
                )
            else:
                # Update existing label content and color
                self.file_tag.configure(text=file_extension, fg_color=color)
            # Ensure the label is visible
            self.file_tag.lift()  # Bring the label to the top
            self.file_tag.bind("<Button-1>", lambda e : self.file_tag.place_forget())
            self.place_file_tag(Size(self.winfo_screenwidth(), self.winfo_screenheight()))
        except TclError as error:
            print(f"Error handling drop event: {error}")



        




    def chatbar(self, frame):
        self.prompt = tk.StringVar()

        self.entry_widget = ctk.CTkEntry(frame, width=500, height=50, corner_radius=50, textvariable=self.prompt)
        self.textbox_widget = ctk.CTkTextbox(frame, width=500, height=100, corner_radius=10)


        self.entry_widget.focus_set()
        self.textbox_widget.focus_set()

        self.entry_widget.drop_target_register(DND_ALL)
        self.textbox_widget.drop_target_register(DND_ALL)

        self.entry_widget.dnd_bind('<<Drop>>', lambda e : self.handleDropEvent(e))
        self.textbox_widget.dnd_bind('<<Drop>>', lambda e : self.handleDropEvent(e))

        self.entry_widget.pack(pady=20)

        if frame == self.speech_body:
            self.entry_widget.bind("<KeyRelease>", self.toggle_prompt_box)
            self.textbox_widget.bind("<KeyRelease>", self.toggle_prompt_box)
            self.textbox_widget.bind("<Command-Return>", self.get_prompt_from_text_box)
            self.textbox_widget.bind("<Control-Return>", self.get_prompt_from_text_box)
            self.entry_widget.bind("<Return>", self.get_prompt_from_text_box)
        if frame == self.text_body:
            self.entry_widget.bind("<KeyRelease>", self.toggle_prompt_box)
            self.textbox_widget.bind("<KeyRelease>", self.toggle_prompt_box)
            self.textbox_widget.bind("<Command-Return>", self.get_prompt_from_text_box_text)
            self.textbox_widget.bind("<Control-Return>", self.get_prompt_from_text_box_text)
            self.entry_widget.bind("<Return>", self.get_prompt_from_text_box_text)








    def place_file_tag(self, e):
        if self.file_tag and self.file_tag.winfo_exists():
            width = e.width
            height = e.height
            window_width = self.winfo_width()
            window_height = self.winfo_height()
            # Check window size and reposition the label accordingly
            if window_width == width or window_height == height:
                self.file_tag.place(relx=0.28, rely=0.8)
            else:
                self.file_tag.place(relx=0.13, rely=0.8)

    def on_resize(self, event):
        # Reposition the file_tag when the window is resized
        e = Size(self.winfo_screenwidth(), self.winfo_screenheight())
        self.place_file_tag(e)



    def toggle_prompt_box(self, e):
        current_text = self.prompt.get()
        current_textbox_content = self.textbox_widget.get("1.0", tk.END).strip()

        # Switch to the textbox if text length exceeds 4
        if len(current_text) >= 75 and self.entry_widget.winfo_ismapped():
            # Switch to the textbox
            self.entry_widget.pack_forget()
            self.textbox_widget.delete("1.0", tk.END)  
            self.textbox_widget.insert("1.0", current_text)  # Insert new text
            self.textbox_widget.focus_set()
            self.textbox_widget.pack(pady=20)

        # Switch back to the entry widget if text length drops below 4
        elif len(current_textbox_content) < 75 and self.textbox_widget.winfo_ismapped():
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
            self.user_prompt = self.prompt.get()
            self.pulser.speech(self.user_prompt)
            self.prompt.set("")
        else:
            self.user_prompt = self.textbox_widget.get("1.0", tk.END).strip()
            self.pulser.speech(self.user_prompt)
            self.textbox_widget.delete("1.0", tk.END) 
            self.prompt.set("")
            self.textbox_widget.pack_forget()
            self.entry_widget.focus_set()
            self.entry_widget.pack(pady=20)

    def text_chat(self):
        try:
            self.text_chat_frame = tk.Frame(self.page_frame)
            self.side_panel_creator(self.text_chat_frame)
            self.main_text_content = tk.Frame(self.text_chat_frame, )
            self.main_text_content_content()
            self.main_text_content.place_configure(relwidth=1.0, relx=0, rely=0, relheight=1.0)
            self.text_chat_frame.pack(fill='both', expand=True)
        except:
            print("Not In Existance (Text Chat)")

    def main_text_content_content(self):
        self.topbar(self.main_text_content)

        # Setup body
        self.text_body = tk.Frame(self.main_text_content, background=self.purple_palette[8])

        self.scroll_frame = ctk.CTkScrollableFrame(self.text_body, corner_radius=0, fg_color=self.purple_palette[8])
        

        self.scroll_frame.drop_target_register(DND_ALL)
        self.scroll_frame.dnd_bind('<<Drop>>', self.handleDropEvent)


        tk.Frame(self.scroll_frame, height=50).pack(side='top')
        # self.scroll_frame_content()
        tk.Frame(self.scroll_frame, height=50).pack(side='bottom')

        self.scroll_frame.pack(fill='both', expand=True)

        self.bind("<Command-j>", self.scroll_to_top)


        self.chatbar(self.text_body)

        self.button_frame = ctk.CTkFrame(self.text_body, corner_radius=50, width=60, height=60, fg_color=self.purple_palette[9])

        self.button_frame.place(relx=.85, rely=.8)
        self.button_frame.pack_propagate(False) 

        self.button_frame.bind("<Button-1>", self.scroll_button_method)

        self.scroll_button = ctk.CTkButton(self.button_frame, text="▲", font=("Segoe UI Symbol", 24), width=0, height=60, fg_color=self.purple_palette[9], hover_color=self.purple_palette[9], command=self.scroll_button_method)
        self.scroll_button.pack()

        self.text_body.place(relx=0, rely=0.1, relwidth=1, relheight=0.9)
        
    def scroll_frame_content(self):
        tk.Frame(self.scroll_frame, height=50).pack()
        for i in range(30):
            label = ctk.CTkLabel(self.scroll_frame, text='Test' + str(i), fg_color='red', corner_radius=10)
            if i % 2 == 0:
                label.pack(ipadx=5, ipady=20, padx=40, pady=10, anchor='w')  
            else:
                label.pack(ipadx=5, ipady=20, padx=40, pady=10, anchor='e') 
        tk.Frame(self.scroll_frame, height=50).pack()
 
    def get_prompt_from_text_box_text(self, e):
        if self.entry_widget.winfo_ismapped(): 
            self.user_prompt = self.prompt.get()
            self.prompt.set("")
        else:
            self.user_prompt = self.textbox_widget.get("1.0", tk.END).strip()
            self.textbox_widget.delete("1.0", tk.END) 
            self.prompt.set("")
            self.textbox_widget.pack_forget()
            self.entry_widget.focus_set()
            self.entry_widget.pack(pady=20)



        input_label = ctk.CTkLabel(self.scroll_frame, text=self.user_prompt, justify='left', fg_color='red', corner_radius=10, wraplength=self.wrap_length(0.5))
        input_label.pack(ipadx=5, ipady=20, padx=40, pady=10, anchor='e') 
        
        
        response_label = ctk.CTkLabel(self.scroll_frame, text='', justify='left', fg_color='blue', corner_radius=10, wraplength=self.wrap_length(0.5))
        response_label.pack(ipadx=5, ipady=20, padx=40, pady=10, anchor='w') 


        input_label.bind("<Double-1>", self.copy_text)
        response_label.bind("<Double-1>", self.copy_text)

        # Initialize the state for this label
        response_label.typing_state = {
            "text": "",  # Current text in the label
            "count": 0,  # Index of the character to add next
            "prompt": self.user_prompt  # Store the prompt specifically for this label
        }
        
        self.slider(response_label)


        
        self.auto_scroll_to_end()

    def copy_text(self, e):
        widget = e.widget
        text_to_copy = ""

        # Check if the widget is a Label, Button, or other text-holding widget
        if isinstance(widget, tk.Label):
            text_to_copy = widget.cget("text")

        self.clipboard_clear()
        self.clipboard_append(text_to_copy)
        print(f"Text Copied Successfully: ({text_to_copy})")
        self.toast(f"Text Copied Successfully: ({text_to_copy})")



    def slider(self, label):
        typing_state = getattr(label, "typing_state", None)
    
        if not typing_state:
        # If the state is not set, initialize it
            typing_state = {
                "text": "",
                "count": 0,
                "prompt": ""  # Add an empty prompt as a fallback
            }
            label.typing_state = typing_state
        
        # Get current state values
        text = typing_state["text"]
        count = typing_state["count"]
        user_prompt = typing_state["prompt"]  # Retrieve the specific prompt for this label
        
        # If all characters have been added, stop the effect
        if count >= len(user_prompt):
            label.configure(text=user_prompt)  # Display the full text
        else:
            # Add the next character to the label
            text += user_prompt[count]
            label.configure(text=text)

       # Update the state for the next call
        typing_state["count"] += 1
        typing_state["text"] = text

        # Call the slider function again after 100 ms for typing effect
        label.after(50, lambda: self.slider(label))

    def scroll_button_method(self, e=None):
        direction = self.scroll_button.cget('text')
        if direction == '▲':
            self.scroll_to_top()
            self.scroll_button.configure(text = '▼')
        else:
            self.auto_scroll_to_end()
            self.scroll_button.configure(text = '▲')

    def auto_scroll_to_end(self):
        self.scroll_frame._scrollbar.set(*self.scroll_frame._parent_canvas.yview())
        self.scroll_frame._parent_canvas.configure(yscrollcommand=self.scroll_frame._scrollbar.set, scrollregion=self.scroll_frame._parent_canvas.bbox('all'))
        self.scroll_frame._parent_canvas.yview_moveto(1.0)

    def scroll_to_top(self, event=None):
        self.scroll_frame._parent_canvas.yview_moveto(0.0)

    def wrap_length(self, rel_width):
        return rel_width * self.winfo_width()
        
    def nav_buttons(self):
        for idx in range(2):
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

    def toast(self, message, position="top"):
        # Create a topmost window for the toast notification
        toast_window = tk.Toplevel(self)
        toast_window.overrideredirect(True)  # Remove window borders
        
        # Get screen width and height
        window_width = self.winfo_width()
        window_height = self.winfo_height()
        window_x = self.winfo_x()
        window_y = self.winfo_y()

        # Calculate the X and Y position for top or bottom center relative to the main window
        if position == "top":
            x_pos = window_x + (window_width // 2) - 100  # Center horizontally
            y_pos = window_y + 30  # Offset from the top of the window
        elif position == "bottom":
            x_pos = window_x + (window_width // 2) - 100  # Center horizontally
            y_pos = window_y + window_height - 70  # Offset from the bottom of the window

        # Set the geometry to position the window
        toast_window.geometry(f"+{x_pos}+{y_pos}")
        
        # Set background color
        toast_window.config(bg=self.purple_palette[4])

        # Create a label widget for the message
        toast_label = tk.Label(toast_window, text=message, bg=self.purple_palette[4], fg="white", font=("Arial", 12, "bold"), padx=10, pady=5)
        toast_label.pack()

        # Destroy the toast window after 2 seconds
        self.after(2000, toast_window.destroy)


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
        

        subprocess.run(["say", "-v", "Daniel", "-o", os.path.join(os.getcwd(), 'Sound', 'prompt.aiff'), text])

        try:
            # say(True, text)
            self.y, self.sr = librosa.load(self.output_file, sr=None)
        except Exception as e:
             print(f"Error loading audio file: {e}")

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

        # Ensure the container exists and is still valid
        if container.winfo_exists():
            if restart:
                self.parent.after(1, self._play_gif, container, frames)
            
            # Resize and configure the image
            photo_image = ImageTk.PhotoImage(frame.resize((x, x)))
            
            try:
                container.configure(image=photo_image)
                container.image = photo_image  # Keep a reference to avoid garbage collection
            except tk.TclError as e:
                print(f"TclError when configuring image: {e}")
        else:
            pass


class Size:
    def __init__(self, width, height):
        self.width = width
        self.height = height






if __name__ == "__main__":
    GUI()


# TODO when the app initally loads, it greets the user after some time of silence. that is for the ai page, where the glowing orb would be.